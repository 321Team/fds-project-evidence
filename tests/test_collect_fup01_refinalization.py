"""운영 서버 접속 없이 원본 판별·파일 보존·압축 안전 경계를 확인한다."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).parents[1] / "tools/collect-fup01-refinalization.py"
spec = importlib.util.spec_from_file_location("collector", SCRIPT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = "기존 재최종화 원본\r\n끝".encode()
        self.patcher = patch.object(c, "EXPECTED_SHA256", hashlib.sha256(self.data).hexdigest())
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_exact_match_duplicate_and_byte_preservation(self):
        for name in ("renamed.md", "refinalization.txt"):
            (self.root / name).write_bytes(self.data)
        before = {p.name: c.metadata(p.stat()) for p in self.root.iterdir()}
        f = c.Finder([self.root]); result = f.run()
        self.assertEqual(result["status"], "MATCH_FOUND_REVIEW_REQUIRED")
        self.assertEqual(len(result["matches"]), 2)
        self.assertEqual(f.original, self.data)
        self.assertEqual(before, {p.name: c.metadata(p.stat()) for p in self.root.iterdir()})

    def test_name_alone_never_passes(self):
        (self.root / "Refinalization.md").write_bytes(self.data + b"\n")
        f = c.Finder([self.root]); report = f.run()
        self.assertEqual(report["status"], "NOT_FOUND_IN_SCOPE")
        self.assertEqual(len(report["named_candidates"]), 1)
        self.assertIsNone(f.original)

    def test_links_hidden_and_missing_root(self):
        (self.root / ".original.md").write_bytes(self.data)
        (self.root / "link.md").symlink_to(self.root / ".original.md")
        f = c.Finder([self.root, self.root / "missing"]); r = f.run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertIsNone(f.original)
        with self.assertRaises(ValueError):
            c.read_stable(self.root / "link.md", c.MAX_FILE)

    def test_zip_and_tar_match_without_extraction(self):
        with zipfile.ZipFile(self.root / "saved.zip", "w") as z:
            z.writestr("old/record.md", self.data)
        with tarfile.open(self.root / "saved.tar.gz", "w:gz") as t:
            item = tarfile.TarInfo("old/record.md"); item.size = len(self.data)
            t.addfile(item, io.BytesIO(self.data))
        f = c.Finder([self.root], True); r = f.run()
        self.assertEqual(len(r["matches"]), 2)
        self.assertEqual(r["issues"], [])
        self.assertFalse((self.root / "old").exists())

    def test_archive_path_and_link_rejected(self):
        with zipfile.ZipFile(self.root / "bad.zip", "w") as z:
            z.writestr("../escape.md", self.data)
        with tarfile.open(self.root / "link.tar", "w") as t:
            item = tarfile.TarInfo("link.md"); item.type = tarfile.SYMTYPE
            item.linkname = "/etc/passwd"; t.addfile(item)
        f = c.Finder([self.root], True); r = f.run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertEqual(len(r["issues"]), 2)

        with patch.object(c, "MAX_ENTRIES", 0):
            r = c.Finder([self.root / "bad.zip", self.root / "link.tar"]).run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertEqual(len(r["issues"]), 2)
        self.assertTrue(all(i["reason"] == "ENTRY_LIMIT" for i in r["issues"]))
        self.assertIsNone(f.original)

    def test_size_limit_and_corrupt_archive(self):
        (self.root / "huge.md").write_bytes(b"x" * 30)
        (self.root / "bad.zip").write_bytes(b"invalid")
        with patch.object(c, "MAX_FILE", 10):
            f = c.Finder([self.root], True); r = f.run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertEqual(len(r["issues"]), 2)

    def test_compressed_expansion_limit(self):
        import gzip
        (self.root / "bomb.tar.gz").write_bytes(gzip.compress(b"0" * 4096))
        (self.root / "disguised.tar").write_bytes(gzip.compress(b"0" * 4096))
        with patch.object(c, "MAX_ARCHIVE", 512):
            f = c.Finder([self.root], True); r = f.run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertEqual(len(r["issues"]), 2)
        self.assertTrue(all("DECOMPRESSED_ARCHIVE_LIMIT" in i["reason"] for i in r["issues"]))

    def test_search_only_result_has_no_fabricated_original(self):
        f = c.Finder([self.root]); f.run()
        archive, sidecar = c.write_bundle(f, self.root)
        self.assertEqual(sidecar.read_text().split()[0], c.sha256(archive.read_bytes()))
        with tarfile.open(archive) as t:
            self.assertEqual(set(t.getnames()), {"review-input/SEARCH_REPORT.json", "review-input/SHA256SUMS"})

    def test_bundle_original_and_internal_hashes(self):
        (self.root / "original.md").write_bytes(self.data)
        f = c.Finder([self.root]); f.run()
        archive, _ = c.write_bundle(f, self.root)
        with tarfile.open(archive) as t:
            self.assertEqual(t.extractfile("review-input/originals/refinalization-original.bin").read(), self.data)
            manifest = t.extractfile("review-input/SHA256SUMS").read().decode()
            for line in manifest.splitlines():
                expected, name = line.split("  ", 1)
                self.assertEqual(c.sha256(t.extractfile("review-input/" + name).read()), expected)

    def test_read_race_and_secret_match_fail_closed(self):
        p = self.root / "original.md"; p.write_bytes(self.data)
        real_meta = c.metadata
        calls = 0
        def changed(s):
            nonlocal calls
            calls += 1
            m = real_meta(s)
            if calls >= 2: m["size"] += 1
            return m
        with patch.object(c, "metadata", side_effect=changed):
            with self.assertRaises(ValueError): c.read_stable(p, c.MAX_FILE)
        secret = b"-----BEGIN PRIVATE KEY-----"
        p.write_bytes(secret)
        with patch.object(c, "EXPECTED_SHA256", c.sha256(secret)):
            f = c.Finder([p]); r = f.run()
        self.assertEqual(r["status"], "SEARCH_INCOMPLETE")
        self.assertIsNone(f.original)


if __name__ == "__main__":
    unittest.main()
