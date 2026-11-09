import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from check_versions import check_archives, git_blob_sha, validate_catalog, safe_path


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "web-demo/test"
        self.archive.mkdir(parents=True)
        self.data = b"sample game\n"
        (self.archive / "game.js").write_bytes(self.data)
        self.file = {"path": "game.js", "bytes": len(self.data),
                     "sha256": hashlib.sha256(self.data).hexdigest(),
                     "git_blob_sha1": git_blob_sha(self.data)}
        self.manifest = {"source_commit": "a" * 40, "files": [self.file]}
        self.save_manifest()
        self.entry = {"id": "v1-20261109T120000Z", "kind": "html5", "status": "archived",
                      "archived_at": "2026-11-09T12:00:00Z", "archive_commit": "b" * 40,
                      "source_commit": "a" * 40, "root": "web-demo/test", "manifest": "version.json", "tag": None}
        self.catalog = {"schema_version": 1, "audited_git_head": "c" * 40, "snapshots": [self.entry]}

    def save_manifest(self):
        (self.archive / "version.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def tree(self):
        return {"sha": "c" * 40, "truncated": False, "tree": [
            {"path": "chemistry-lab-game/web-demo/test/" + name, "type": "blob", "size": len(data), "sha": git_blob_sha(data)}
            for name, data in [("game.js", self.data), ("version.json", (self.archive / "version.json").read_bytes())]]}

    def test_bytes_match(self):
        self.assertEqual(check_archives(self.root, self.catalog)[0], [])

    def test_changed_bytes_fail(self):
        (self.archive / "game.js").write_bytes(b"changed")
        self.assertTrue(check_archives(self.root, self.catalog)[0])

    def test_missing_bytes_fail(self):
        (self.archive / "game.js").unlink()
        self.assertTrue(check_archives(self.root, self.catalog)[0])

    def test_metadata_match(self):
        self.assertEqual(check_archives(self.root, self.catalog, self.tree())[0], [])

    def test_metadata_missing_fails(self):
        tree = self.tree(); tree["tree"].pop(0)
        self.assertTrue(check_archives(self.root, self.catalog, tree)[0])

    def test_metadata_changed_fails(self):
        tree = self.tree(); tree["tree"][0]["sha"] = "d" * 40
        self.assertTrue(check_archives(self.root, self.catalog, tree)[0])

    def test_manifest_pin(self):
        tree = self.tree(); self.manifest["note"] = "changed"; self.save_manifest()
        self.assertTrue(check_archives(self.root, self.catalog, tree)[0])

    def test_truncated_tree_rejected(self):
        tree = self.tree(); tree["truncated"] = True
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog, tree)

    def test_wrong_tree_rejected(self):
        tree = self.tree(); tree["sha"] = "d" * 40
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog, tree)

    def test_pending_not_published(self):
        pending = {"id": "r25-pending", "status": "pending_archive", "source_commit": "e" * 40}
        self.catalog["snapshots"].append(pending)
        errors, results = check_archives(self.root, self.catalog)
        self.assertFalse(errors); self.assertIn("PENDING", results[-1])
        pending["archive_commit"] = "b" * 40
        with self.assertRaises(ValueError): validate_catalog(self.catalog)

    def test_duplicate_id(self):
        self.catalog["snapshots"].append(copy.deepcopy(self.entry))
        with self.assertRaises(ValueError): validate_catalog(self.catalog)

    def test_source_mismatch(self):
        self.entry["source_commit"] = "f" * 40
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog)

    def test_utc_required(self):
        self.entry["archived_at"] = "2026-11-09T12:00:00"
        with self.assertRaises(ValueError): validate_catalog(self.catalog)

    def test_invalid_paths(self):
        for path in ("../secret", "/etc/passwd", "x/../../secret", "a\\b", "a//b"):
            with self.subTest(path=path), self.assertRaises(ValueError): safe_path(path)

    def test_duplicate_manifest_path(self):
        self.manifest["files"].append(copy.deepcopy(self.file)); self.save_manifest()
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog)

    def test_bad_size(self):
        self.manifest["files"][0]["bytes"] = -1; self.save_manifest()
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog)

    def test_map_parts_match(self):
        self.entry["kind"] = "map-assets"
        item = {"path": "game.js", "bytes": len(self.data), "sha256": self.file["sha256"],
                "blob_sha": self.file["git_blob_sha1"]}
        self.manifest = {"images": [], "full_png_original": {"parts": [item], "bytes": len(self.data)}}
        self.save_manifest()
        self.assertEqual(check_archives(self.root, self.catalog)[0], [])
        self.manifest["full_png_original"]["bytes"] += 1; self.save_manifest()
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog)

    def test_duplicate_tree_path(self):
        tree = self.tree(); tree["tree"].append(copy.deepcopy(tree["tree"][0]))
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog, tree)

    def test_empty_manifest(self):
        self.manifest["files"] = []; self.save_manifest()
        with self.assertRaises(ValueError): check_archives(self.root, self.catalog)

    def test_symlink_escape(self):
        (self.archive / "game.js").unlink()
        (self.archive / "game.js").symlink_to("/etc/hosts")
        self.assertTrue(check_archives(self.root, self.catalog)[0])


if __name__ == "__main__":
    unittest.main()
