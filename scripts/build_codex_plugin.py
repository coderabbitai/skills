#!/usr/bin/env python3
"""Export the Codex package without exposing its skill to repository discovery."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def build(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    if not (source / ".codex-plugin/plugin.json").is_file():
        raise ValueError("Source must contain .codex-plugin/plugin.json")
    if output.is_relative_to(source):
        raise ValueError("Output must be outside the package source directory")

    entries = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Package must not contain symlinks: {path}")
        if not path.is_file():
            continue
        name = path.relative_to(source).as_posix()
        if path.name == "SKILL.md.source":
            name = name.removesuffix(".source")
        if name in entries:
            raise ValueError(f"Duplicate archive path: {name}")
        entries[name] = path.read_bytes()

    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    print(f"Built {output} ({len(entries)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[1] / "packaging/codex")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.source, args.output)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
