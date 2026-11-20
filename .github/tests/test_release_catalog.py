import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


CHECK = Path(__file__).resolve().parents[1] / "check_release_catalog.rb"


class ReleaseCatalogTests(unittest.TestCase):
    def check_catalog(self, frontmatter, *, include_skill=True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skills/config").mkdir(parents=True)
            archive = root / "release.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                if include_skill:
                    content = f"---\n{frontmatter}\n---\n# Configuration\n".encode()
                    entry = tarfile.TarInfo("coderabbit-skills-1.2.3/skills/config/SKILL.md")
                    entry.size = len(content)
                    tar.addfile(entry, io.BytesIO(content))
            return subprocess.run(
                ["ruby", str(CHECK), str(archive), "1.2.3"],
                cwd=root, text=True, capture_output=True,
            )

    def test_packaged_metadata(self):
        result = self.check_catalog('name: config\nmetadata:\n  version: "0.1.0"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("config 0.1.0", result.stdout)

    def test_missing_metadata_version(self):
        for header in ["name: config", 'name: config\nother:\n  version: "0.1.0"']:
            with self.subTest(header=header):
                result = self.check_catalog(header)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("metadata.version", result.stderr)

    def test_name_must_match_directory(self):
        result = self.check_catalog('name: other\nmetadata:\n  version: "0.1.0"')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("name must match its directory", result.stderr)

    def test_skill_omitted_from_archive(self):
        result = self.check_catalog("", include_skill=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing from archive: config", result.stderr)
