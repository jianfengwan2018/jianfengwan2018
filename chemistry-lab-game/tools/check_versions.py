#!/usr/bin/env python3
"""Read-only archive checks. Default: bytes; --tree-json: Git object metadata."""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath

SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def safe_path(value, allow_dot=False):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Invalid relative path: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or (value == "." and not allow_dot):
        raise ValueError(f"Unsafe path: {value!r}")
    if str(p) != value:
        raise ValueError(f"Non-canonical path: {value!r}")
    return p


def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(catalog):
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    if not SHA1.fullmatch(catalog.get("audited_git_head", "")):
        raise ValueError("Invalid audited Git head")
    ids = set()
    snapshots = catalog.get("snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        raise ValueError("No snapshots")
    for entry in snapshots:
        identity = entry.get("id")
        if not isinstance(identity, str) or not identity or identity in ids:
            raise ValueError(f"Missing or duplicate snapshot id: {identity}")
        ids.add(identity)
        if entry.get("source_commit") and not SHA1.fullmatch(entry["source_commit"]):
            raise ValueError(f"Invalid source commit: {identity}")
        if entry.get("status") == "pending_archive":
            for field in ("archived_at", "archive_commit", "root", "tag", "manifest"):
                if entry.get(field) is not None:
                    raise ValueError(f"Pending snapshot has {field}: {identity}")
            continue
        if entry.get("status") != "archived":
            raise ValueError(f"Unknown status: {identity}")
        if not SHA1.fullmatch(entry.get("archive_commit", "")):
            raise ValueError(f"Invalid archive commit: {identity}")
        stamp = entry.get("archived_at", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp):
            raise ValueError(f"Archive time must be UTC: {identity}")
        datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        safe_path(entry.get("root"), allow_dot=entry.get("kind") == "godot")
        if entry.get("kind") not in {"godot", "html5", "map-assets"}:
            raise ValueError(f"Unknown archive kind: {identity}")
        if entry["kind"] != "godot":
            safe_path(entry.get("manifest"))


def entries_from_manifest(entry, manifest):
    if entry["kind"] == "html5":
        if manifest.get("source_commit") != entry.get("source_commit"):
            raise ValueError(f"Source commit differs: {entry['id']}")
        source = manifest.get("files", [])
        entries = [{"path": f["path"], "bytes": f["bytes"], "sha256": f["sha256"],
                    "blob": f["git_blob_sha1"]} for f in source]
    elif entry["kind"] == "map-assets":
        source = manifest.get("images", []) + manifest.get("full_png_original", {}).get("parts", [])
        entries = [{"path": f["path"], "bytes": f["bytes"], "sha256": f["sha256"],
                    "blob": f["blob_sha"]} for f in source]
        parts = manifest.get("full_png_original", {}).get("parts", [])
        if not parts or sum(p["bytes"] for p in parts) != manifest["full_png_original"]["bytes"]:
            raise ValueError("Full PNG part size mismatch")
    else:
        return []
    if not entries:
        raise ValueError(f"Empty archive manifest: {entry['id']}")
    seen = set()
    for item in entries:
        safe_path(item["path"])
        if item["path"] in seen:
            raise ValueError(f"Duplicate manifest path: {item['path']}")
        seen.add(item["path"])
        if type(item["bytes"]) is not int or item["bytes"] < 0:
            raise ValueError("Invalid file size")
        if not SHA1.fullmatch(item["blob"]) or not SHA256.fullmatch(item["sha256"]):
            raise ValueError("Invalid manifest digest")
    return entries


def check_archives(project, catalog, tree=None):
    validate_catalog(catalog)
    root = project.resolve()
    metadata = None
    if tree is not None:
        if tree.get("truncated") is not False:
            raise ValueError("Recursive tree is truncated or completeness is unknown")
        allowed = {catalog["audited_git_head"], catalog.get("audited_root_tree")}
        if tree.get("sha") not in allowed - {None}:
            raise ValueError("Tree does not match the catalog audit snapshot")
        metadata = {}
        for item in tree["tree"]:
            if item.get("path") in metadata:
                raise ValueError("Duplicate tree path")
            metadata[item["path"]] = item
    errors, results = [], []
    for entry in catalog["snapshots"]:
        if entry["status"] == "pending_archive":
            results.append(f"PENDING {entry['id']} (not an archived release)")
            continue
        if entry["kind"] == "godot":
            results.append(f"HISTORICAL {entry['id']} (no byte manifest; use fixed commit)")
            continue
        archive = root / entry["root"]
        manifest_path = archive / entry["manifest"]
        if not manifest_path.resolve().is_relative_to(root):
            raise ValueError("Manifest resolves outside project")
        manifest = read_json(manifest_path)
        files = entries_from_manifest(entry, manifest)
        before = len(errors)
        if metadata is not None:
            # Pin the local manifest itself to the supplied remote tree.
            data = manifest_path.read_bytes()
            key = f"chemistry-lab-game/{entry['root']}/{entry['manifest']}"
            remote = metadata.get(key, {})
            if remote.get("sha") != git_blob_sha(data) or remote.get("size") != len(data):
                errors.append(f"Manifest metadata mismatch: {key}")
        for item in files:
            rel = f"{entry['root']}/{item['path']}"
            if metadata is not None:
                remote = metadata.get(f"chemistry-lab-game/{rel}", {})
                if remote.get("type") != "blob" or remote.get("sha") != item["blob"] or remote.get("size") != item["bytes"]:
                    errors.append(f"Remote blob mismatch/missing: {rel}")
                continue
            path = archive / item["path"]
            if not path.resolve().is_relative_to(root):
                errors.append(f"File resolves outside project: {rel}")
                continue
            if not path.is_file():
                errors.append(f"Missing file: {rel}")
                continue
            data = path.read_bytes()
            if (len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]
                    or git_blob_sha(data) != item["blob"]):
                errors.append(f"File digest/size mismatch: {rel}")
        if len(errors) == before:
            results.append(f"MATCH {entry['id']}: {len(files)} files ({'Git metadata' if metadata is not None else 'bytes'})")
    return errors, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--tree-json", type=Path)
    args = parser.parse_args()
    try:
        catalog = read_json(args.project / "releases/index.json")
        tree = read_json(args.tree_json) if args.tree_json else None
        errors, results = check_archives(args.project, catalog, tree)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"ERROR {exc}")
        return 1
    for line in results:
        print(line)
    for error in errors:
        print(f"ERROR {error}")
    print("Archive checks failed." if errors else "Archive checks passed within the stated scope.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
