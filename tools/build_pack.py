#!/usr/bin/env python3
"""
Pack builder for the refresh collection.

Turns each unpacked pack under  src/<slug>/  into the two files that ship:
  <folder>/<slug>-v<version>-mc<mcver>.zip   the plain data pack
  <folder>/<slug>-v<version>-mc<mcver>.jar   the same payload plus loader metadata

Run with no arguments to build everything, or name one or more slugs.
"""
import json, os, sys, zipfile
from pathlib import Path

import convert_26_3

MC_VERSION = "26.3"


def collection_root():
    """The collection folder: where Build-Loot sits, or one level above tools/."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT = collection_root()
SRC = ROOT / "src"

# Never ends up inside a built archive.
EXCLUDE_NAMES = {".loader", "pack.json", ".gitkeep", ".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIXES = {".bbmodel"}  # working files, never part of a shipped pack


def payload_files(pack_dir):
    """Every shippable file in the pack, as (absolute path, archive path)."""
    for path in sorted(pack_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(pack_dir)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if path.suffix in EXCLUDE_SUFFIXES:
            continue
        yield path, rel.as_posix()


def write_archive(target, entries):
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for source, name in entries:
            zf.write(source, name)
    return target


def build(slug):
    pack_dir = SRC / slug
    meta = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    convert_26_3.generate(pack_dir)
    out_dir = ROOT / meta["folder"]
    stem = f"{slug}-v{meta['version']}-mc{MC_VERSION}"

    payload = list(payload_files(pack_dir))
    zip_path = write_archive(out_dir / f"{stem}.zip", payload)

    if meta.get("kind") == "resource":
        # A resource pack has no loader wrapper; the .zip is the whole product.
        print(f"{slug}: {zip_path.name} ({len(payload)} files)")
        return

    loader = pack_dir / ".loader"
    jar_entries = list(payload)
    for path in sorted(loader.rglob("*")):
        if path.is_file():
            jar_entries.append((path, path.relative_to(loader).as_posix()))
    # The loader metadata points at its own copy of the icon.
    icon = pack_dir / "pack.png"
    if icon.is_file():
        jar_entries.append((icon, meta["logo"]))
    jar_path = write_archive(out_dir / f"{stem}.jar", jar_entries)

    print(f"{slug}: {zip_path.name} ({len(payload)} files), {jar_path.name} ({len(jar_entries)} files)")


def main(argv):
    slugs = argv[1:] or sorted(p.name for p in SRC.iterdir() if (p / "pack.json").is_file())
    for slug in slugs:
        build(slug)


if __name__ == "__main__":
    main(sys.argv)
