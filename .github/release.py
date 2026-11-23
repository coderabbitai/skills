"""Maintain the shared source version and build CLI-compatible release assets.

Python standard library only. Marketplace publication is tracked separately.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    '.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
    '.cursor-plugin/plugin.json', 'gemini-extension.json', 'plugin.json',
    'packaging/codex-connected/plugin.json',
)
# Include consumer-facing documentation as well as installed components.
PACKAGE_PATHS = (
    'VERSION', *MANIFESTS, 'skills', 'agents', 'commands', 'assets', 'rules',
    'hooks.json', 'mcp_config.json', '.mcp.json', '.antigravity-plugin',
    '.claude-plugin', '.codex-plugin', '.cursor-plugin', 'scripts',
    'README.md', 'docs/mcp.md', 'packaging/codex-connected',
)
SEMVER = r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'


def version(value):
    if not isinstance(value, str) or not re.fullmatch(SEMVER, value):
        raise ValueError(f'Expected stable MAJOR.MINOR.PATCH, got {value!r}')
    return tuple(map(int, value.split('.')))


def git(root, *args):
    return subprocess.check_output(
        ['git', '-C', str(root), *args], text=True, stderr=subprocess.PIPE,
    ).strip()


def resolve(root, ref):
    return git(root, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}')


def read_version(root):
    value = (root / 'VERSION').read_text().strip()
    version(value)
    return value


def skill_metadata(path):
    text = path.read_text()
    front = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not front:
        raise ValueError(f'{path}: missing frontmatter')
    # Enforce the repository's simple, CLI-readable frontmatter form.
    name = re.findall(r'^name: ([a-z0-9]+(?:-[a-z0-9]+)*)$', front[1], re.M)
    metadata = re.findall(r'^metadata:\n((?:[ \t]+[^\n]*\n?)*)', front[1], re.M)
    versions = re.findall(r'^  version: [\"\']?([^\"\'\n]+)[\"\']?$', metadata[0], re.M) if len(metadata) == 1 else []
    if name != [path.parent.name] or len(versions) != 1:
        raise ValueError(f'{path}: require matching name and one metadata.version')
    if not re.search(r'^description: \S', front[1], re.M):
        raise ValueError(f'{path}: missing description')
    version(versions[0])
    return versions[0], text


def skills(root):
    paths = sorted(root.glob('skills/*/SKILL.md'))
    directories = {p.name for p in (root / 'skills').iterdir() if p.is_dir() and not p.name.startswith('.')}
    if not paths or {p.parent.name for p in paths} != directories:
        raise ValueError('Every skills/ directory must contain SKILL.md')
    return paths


def check_inventory(root):
    # New manifests must join this inventory, rather than silently escaping CI.
    discovered = {str(p.relative_to(root)) for pattern in ('.*-plugin/plugin.json', 'packaging/*/plugin.json') for p in root.glob(pattern)}
    unknown = discovered - set(MANIFESTS)
    if unknown:
        raise ValueError(f'Add new active manifests to MANIFESTS: {sorted(unknown)}')


def check(root, base=None, tag=None, after_tag=None):
    current = read_version(root)
    check_inventory(root)
    for name in MANIFESTS:
        data = json.loads((root / name).read_text())
        if data.get('name') != 'coderabbit' or data.get('version') != current:
            raise ValueError(f'{name}: expected coderabbit version {current}; run bump')
    for path in skills(root):
        if skill_metadata(path)[0] != current:
            raise ValueError(f'{path.relative_to(root)}: expected metadata.version {current}; run bump')
    if tag is not None and tag != f'v{current}':
        raise ValueError(f'Tag {tag!r} must be v{current}')
    if after_tag is not None:
        if not after_tag.startswith('v') or version(current) <= version(after_tag[1:]):
            raise ValueError(f'Source {current} must be newer than published {after_tag}')
    if base:
        base = resolve(root, base)
        # Bootstrap from the largest existing manifest version on pre-policy main.
        if git(root, 'ls-tree', '--name-only', base, '--', 'VERSION'):
            previous = git(root, 'show', f'{base}:VERSION')
        else:
            previous = max(
                (json.loads(git(root, 'show', f'{base}:{name}'))['version'] for name in MANIFESTS),
                key=version,
            )
        if version(current) < version(previous):
            raise ValueError(f'Version cannot go backwards from {previous} to {current}')
        changed = git(root, 'diff', '--name-only', base, '--', *PACKAGE_PATHS)
        untracked = git(root, 'ls-files', '--others', '--exclude-standard', '--', *PACKAGE_PATHS)
        if (changed or untracked) and version(current) <= version(previous):
            raise ValueError(f'Package changed: increment VERSION beyond {previous} with bump')
    return current


def bump(root, target):
    version(target)
    check_inventory(root)
    existing = []
    updates = {}
    for name in MANIFESTS:
        path = root / name
        text = path.read_text()
        data = json.loads(text)
        if data.get('name') != 'coderabbit':
            raise ValueError(f'{name}: preserve the coderabbit package identity')
        existing.append(data['version'])
        updated, count = re.subn(r'^(  "version": )"[^"\n]+"', lambda m: m[1] + json.dumps(target), text, flags=re.M)
        if count != 1:
            raise ValueError(f'{name}: expected one top-level version field')
        updates[path] = updated
    for path in skills(root):
        previous, text = skill_metadata(path)
        existing.append(previous)
        front, body = text.split('\n---', 1)
        front, count = re.subn(r'^  version: [^\n]+$', f'  version: "{target}"', front, flags=re.M)
        if count != 1:
            raise ValueError(f'{path}: expected one version field')
        updates[path] = front + '\n---' + body
    if (root / 'VERSION').exists():
        existing.append(read_version(root))
    if version(target) <= max(map(version, existing)):
        raise ValueError('Choose a version greater than every current source version')
    # Preflight every file before changing any of them. Historical release records
    # and published marketplace versions deliberately do not participate.
    updates[root / 'VERSION'] = target + '\n'
    for path, text in updates.items():
        path.write_text(text)
    check(root)


def build(root, output, tag=None):
    current = check(root, tag=tag)
    commit = resolve(root, 'HEAD')
    if git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Build from a clean, committed checkout')
    if tag and resolve(root, tag) != commit:
        raise ValueError('Release tag must identify the checked-out commit')
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError('Build output must be outside the source checkout')
    tag = tag or f'v{current}'
    archive = f'coderabbit-skills-{tag}.tar.gz'
    checksum = f'coderabbit-skills-{tag}.sha256'
    release_url = f'https://github.com/coderabbitai/skills/releases/download/{tag}'
    tar = subprocess.check_output([
        'git', '-C', str(root), 'archive', '--format=tar',
        f'--prefix=coderabbit-skills-{current}/', commit,
    ])
    compressed = gzip.compress(tar, mtime=0)
    digest = hashlib.sha256(compressed).hexdigest()
    manifest = {
        'version': current, 'tag': tag, 'sourceCommit': commit,
        'sourceTarballUrl': f'https://codeload.github.com/coderabbitai/skills/tar.gz/refs/tags/{tag}',
        'archive': {'name': archive, 'url': f'{release_url}/{archive}', 'sha256': digest},
        'checksum': {'name': checksum, 'url': f'{release_url}/{checksum}'},
        'packages': {name: current for name in MANIFESTS},
        'skills': {p.parent.name: current for p in skills(root)},
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / archive).write_bytes(compressed)
    (output / checksum).write_text(f'{digest}  {archive}\n')
    (output / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    audit = commands.add_parser('check')
    audit.add_argument('--base', help='fresh canonical main SHA, or previous main SHA in CI')
    audit.add_argument('--tag')
    audit.add_argument('--after-tag', help='currently published latest tag; release must be newer')
    commands.add_parser('bump').add_argument('version')
    package = commands.add_parser('build')
    package.add_argument('--output', type=Path, required=True, help='new directory outside checkout')
    modes = package.add_mutually_exclusive_group(required=True)
    modes.add_argument('--tag', help='existing vMAJOR.MINOR.PATCH tag at HEAD')
    modes.add_argument('--snapshot', action='store_true', help='validate packaging without a release tag; never publishes')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            print(f'Source versions valid: {check(args.root, args.base, args.tag, args.after_tag)}')
        elif args.command == 'bump':
            bump(args.root, args.version)
            print(f'Updated all source versions to {args.version}')
        else:
            result = build(args.root, args.output, args.tag)
            print(f'Built {result["tag"]} from {result["sourceCommit"]} in {args.output}')
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Release validation failed: {error}\n')


if __name__ == '__main__':
    main()
