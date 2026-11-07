#!/usr/bin/env python3
"""Restore and verify the original campus PNG from its exact binary parts."""
from pathlib import Path
import hashlib
import json
import os

root = Path(__file__).resolve().parent
metadata = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
original = metadata["full_png_original"]
destination = root / original["restore_output"]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

if destination.exists():
    if destination.stat().st_size == original["bytes"] and digest(destination) == original["sha256"]:
        print("Original PNG already exists and matches SHA-256:", destination)
        raise SystemExit(0)
    raise SystemExit("Refusing to overwrite an existing file with different content: " + str(destination))

validated = []
for part in original["parts"]:
    path = root / part["path"]
    if not path.is_file() or path.stat().st_size != part["bytes"] or digest(path) != part["sha256"]:
        raise SystemExit("Missing or damaged part: " + str(path))
    validated.append(path)

destination.parent.mkdir(parents=True, exist_ok=True)
temporary = destination.with_suffix(".png.restoring")
with temporary.open("xb") as target:
    for path in validated:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                target.write(chunk)
if temporary.stat().st_size != original["bytes"] or digest(temporary) != original["sha256"]:
    temporary.unlink()
    raise SystemExit("Reassembled PNG failed validation.")
os.replace(temporary, destination)
print("Restored original PNG; byte count and SHA-256 verified:", destination)
