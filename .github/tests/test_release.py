import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('release', Path(__file__).parents[1] / 'release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class VersionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'core.hooksPath', '/dev/null')
        self.git('config', 'core.excludesFile', '/dev/null')
        self.write('VERSION', '1.4.0\n')
        for name in release.MANIFESTS:
            self.write(name, json.dumps({'name': 'coderabbit', 'version': '1.4.0'}, indent=2) + '\n')
        for name in ('code-review', 'coderabbit-config'):
            self.write(f'skills/{name}/SKILL.md', f'---\nname: {name}\ndescription: Review code\nmetadata:\n  version: "1.4.0"\n---\n\nReview instructions\n')
        self.commit()
        self.base = self.git('rev-parse', 'HEAD')

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def git(self, *args):
        return release.git(self.root, *args)

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture')

    def test_all_host_manifests_are_enforced(self):
        for name in release.MANIFESTS:
            with self.subTest(name=name):
                original = (self.root / name).read_text()
                self.write(name, original.replace('1.4.0', '1.3.0'))
                with self.assertRaisesRegex(ValueError, 'expected coderabbit version'):
                    release.check(self.root)
                self.write(name, original)

    def test_missing_skill_metadata_rejected_before_release(self):
        path = self.root / 'skills/coderabbit-config/SKILL.md'
        path.write_text(path.read_text().replace('  version: "1.4.0"\n', ''))
        with self.assertRaisesRegex(ValueError, 'metadata.version'):
            release.check(self.root)

    def test_wrong_skill_identity_and_duplicate_version_rejected(self):
        path = self.root / 'skills/code-review/SKILL.md'
        original = path.read_text()
        for content in (original.replace('name: code-review', 'name: wrong'),
                        original.replace('  version: "1.4.0"', '  version: "1.4.0"\n  version: "1.4.0"')):
            path.write_text(content)
            with self.assertRaises(ValueError):
                release.check(self.root)

    def test_new_skill_without_entrypoint_rejected(self):
        self.write('skills/new-skill/reference.md', 'incomplete')
        with self.assertRaisesRegex(ValueError, 'SKILL.md'):
            release.check(self.root)

    def test_unregistered_host_manifest_rejected(self):
        self.write('.new-plugin/plugin.json', '{}')
        with self.assertRaisesRegex(ValueError, 'Add new active manifests'):
            release.check(self.root)

    def test_package_change_requires_bump_in_any_git_state(self):
        self.write('agents/new.md', 'new agent')
        for state in ('untracked', 'staged', 'committed'):
            with self.subTest(state=state):
                if state == 'staged':
                    self.git('add', '.')
                elif state == 'committed':
                    self.commit()
                with self.assertRaisesRegex(ValueError, 'increment VERSION'):
                    release.check(self.root, self.base)

    def test_deletion_requires_bump(self):
        self.git('rm', '-qr', 'skills/coderabbit-config')
        with self.assertRaisesRegex(ValueError, 'increment VERSION'):
            release.check(self.root, self.base)

    def test_policy_and_publication_docs_do_not_require_bump(self):
        self.write('.github/check.py', '# maintainer tooling')
        self.write('DISTRIBUTION_CHANNELS.md', 'Marketplace observation')
        self.assertEqual(release.check(self.root, self.base), '1.4.0')

    def test_bump_updates_all_active_consumers_and_preserves_history(self):
        self.write('packaging/releases/old.json', '{"version": "1.0.0"}')
        release.bump(self.root, '1.4.1')
        self.assertEqual(release.check(self.root, self.base), '1.4.1')
        self.assertEqual(json.loads((self.root / 'packaging/releases/old.json').read_text())['version'], '1.0.0')

    def test_bad_bump_leaves_files_unchanged(self):
        before = (self.root / release.MANIFESTS[0]).read_bytes()
        for target in ('1.3.0', '1.4.0', '01.5.0', '1.5.0-beta', 'x'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                release.bump(self.root, target)
        self.assertEqual((self.root / release.MANIFESTS[0]).read_bytes(), before)

    def test_invalid_inventory_fails_bump_before_writing(self):
        before = (self.root / release.MANIFESTS[0]).read_bytes()
        self.write('.new-plugin/plugin.json', '{}')
        with self.assertRaises(ValueError):
            release.bump(self.root, '1.5.0')
        self.assertEqual((self.root / release.MANIFESTS[0]).read_bytes(), before)

    def test_bootstrap_must_exceed_every_old_manifest(self):
        self.git('rm', 'VERSION')
        self.write(release.MANIFESTS[0], '{"name":"coderabbit","version":"1.5.0"}')
        self.commit()
        base = self.git('rev-parse', 'HEAD')
        self.write(release.MANIFESTS[0], json.dumps({'name': 'coderabbit', 'version': '1.4.0'}, indent=2))
        self.write('VERSION', '1.4.0')
        with self.assertRaisesRegex(ValueError, 'backwards'):
            release.check(self.root, base)
        release.bump(self.root, '1.6.0')
        release.check(self.root, base)

    def test_parallel_pr_must_bump_again_after_other_pr_merges(self):
        release.bump(self.root, '1.4.1')
        self.commit()
        newer_main = self.git('rev-parse', 'HEAD')
        self.write('agents/new.md', 'second PR still has the same version')
        with self.assertRaisesRegex(ValueError, 'increment VERSION beyond 1.4.1'):
            release.check(self.root, newer_main)

    def test_tag_and_published_version_gates(self):
        release.check(self.root, tag='v1.4.0', after_tag='v1.2.2')
        for tag in ('v1.3.0', '1.4.0', 'v1.4.0-beta'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.check(self.root, tag=tag)
        for tag in ('v1.4.0', 'v1.5.0', 'claude-1.3.0'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.check(self.root, after_tag=tag)

    def test_release_assets_preserve_cli_contract_and_commit_identity(self):
        self.git('tag', 'v1.4.0')
        output = Path(self.temp.name) / 'release'
        manifest = release.build(self.root, output, 'v1.4.0')
        archive = output / manifest['archive']['name']
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(manifest['sourceCommit'], self.base)
        self.assertEqual(manifest['archive']['sha256'], digest)
        self.assertEqual(manifest['archive']['name'], 'coderabbit-skills-v1.4.0.tar.gz')
        self.assertEqual(manifest['archive']['url'], 'https://github.com/coderabbitai/skills/releases/download/v1.4.0/coderabbit-skills-v1.4.0.tar.gz')
        self.assertEqual((output / manifest['checksum']['name']).read_text(), f'{digest}  {archive.name}\n')
        with tarfile.open(archive) as package:
            for name in ('code-review', 'coderabbit-config'):
                skill = package.extractfile(f'coderabbit-skills-1.4.0/skills/{name}/SKILL.md').read().decode()
                self.assertIn('  version: "1.4.0"', skill)
            self.assertEqual(package.extractfile('coderabbit-skills-1.4.0/VERSION').read(), b'1.4.0\n')
        again = Path(self.temp.name) / 'repeat'
        release.build(self.root, again, 'v1.4.0')
        self.assertEqual(archive.read_bytes(), (again / archive.name).read_bytes())
        self.assertEqual((output / 'release-manifest.json').read_bytes(), (again / 'release-manifest.json').read_bytes())

    def test_dirty_checkout_and_wrong_commit_cannot_be_released(self):
        self.git('tag', 'v1.4.0')
        self.write('README.md', 'changed')
        output = Path(self.temp.name) / 'release'
        with self.assertRaisesRegex(ValueError, 'clean'):
            release.build(self.root, output, 'v1.4.0')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'checked-out commit'):
            release.build(self.root, output, 'v1.4.0')
        self.assertFalse(output.exists())

    def test_build_refuses_existing_output(self):
        output = Path(self.temp.name) / 'release'
        output.mkdir()
        (output / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError):
            release.build(self.root, output)
        self.assertEqual((output / 'keep').read_text(), 'keep')


class ConnectedPackageTests(unittest.TestCase):
    def test_both_profiles_preserve_shared_version_and_skill_payloads(self):
        root = Path(__file__).resolve().parents[2]
        expected = release.read_version(root)
        with tempfile.TemporaryDirectory() as directory:
            for profile in ('portal', 'native'):
                with self.subTest(profile=profile):
                    output = Path(directory) / f'{profile}.zip'
                    subprocess.run([
                        sys.executable, str(root / 'packaging/codex-connected/build.py'),
                        profile, str(output),
                    ], check=True, capture_output=True)
                    with ZipFile(output) as package:
                        name = 'plugin.json' if profile == 'portal' else '.codex-plugin/plugin.json'
                        self.assertEqual(json.loads(package.read(name))['version'], expected)
                        for skill in release.skills(root):
                            relative = str(skill.relative_to(root))
                            self.assertEqual(package.read(relative), skill.read_bytes())
                        self.assertIn('mcp.json' if profile == 'portal' else '.mcp.json', package.namelist())


if __name__ == '__main__':
    unittest.main()
