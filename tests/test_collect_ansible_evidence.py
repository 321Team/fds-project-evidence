"""Local fixtures only; never reads operational server evidence."""
import importlib.util
import os
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("collector", Path(__file__).resolve().parents[1] / "tools/collect-ansible-evidence.py")
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "CR-P1-ANS-01-01"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_manifest_and_source_unchanged(self):
        source = self.root / "result.txt"
        source.write_bytes(b"PASS\r\n")
        source.chmod(0o640)
        original_stat = source.stat()
        manifest = (C.sha(source.read_bytes()) + "  ./result.txt\n").encode()
        (self.root / "SHA256SUMS").write_bytes(manifest)
        data, report = C.collect_directory("CR", self.root, "SHA256SUMS", ["result.txt"])
        self.assertEqual(report["original_manifest"]["result"], "MATCH")
        self.assertEqual(data["CR/result.txt"], b"PASS\r\n")
        self.assertEqual(source.stat().st_mode, original_stat.st_mode)
        self.assertEqual(source.stat().st_uid, original_stat.st_uid)
        self.assertEqual(source.stat().st_mtime_ns, original_stat.st_mtime_ns)
        self.assertEqual((self.root / "SHA256SUMS").read_bytes(), manifest)
        self.assertEqual(report["handoff_acceptance"], "PENDING")

    def test_missing_manifest_keeps_review_input(self):
        (self.root / "result.txt").write_text("collected evidence")
        data, report = C.collect_directory("CR", self.root, "SHA256SUMS", ["missing.txt"])
        self.assertIn("CR/result.txt", data)
        self.assertEqual(report["missing_required"], ["missing.txt"])
        self.assertEqual(report["original_manifest"]["result"], "MISSING_NOT_VERIFIED")

    def test_mismatch_never_becomes_test_pass(self):
        (self.root / "result.txt").write_text("current bytes")
        (self.root / "SHA256SUMS").write_text("0" * 64 + "  result.txt\n")
        _, report = C.collect_directory("CR", self.root, "SHA256SUMS", [])
        self.assertEqual(report["original_manifest"]["entries"][0]["result"], "MISMATCH")
        self.assertEqual(report["test_verdict"], "NOT_ASSESSED")

    def test_unsafe_manifest_and_symlink_not_read(self):
        outside = self.root.parent / "outside.txt"
        outside.write_text("must not be exported")
        (self.root / "link.txt").symlink_to(outside)
        (self.root / "SHA256SUMS").write_text(C.sha(outside.read_bytes()) + "  ../outside.txt\n")
        data, report = C.collect_directory("CR", self.root, "SHA256SUMS", [])
        self.assertNotIn("CR/link.txt", data)
        self.assertEqual(report["original_manifest"]["entries"][0]["result"], "UNSAFE_MANIFEST_PATH")

    def test_fifo_rejected_without_blocking(self):
        fifo = self.root / "pipe.txt"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(ValueError, "NOT_REGULAR"):
            C.original_bytes(fifo)

    def test_secret_bytes_excluded_and_not_echoed(self):
        secret = b"-----BEGIN OPENSSH PRIVATE KEY-----\nfixture-not-a-key"
        (self.root / "result.txt").write_bytes(secret)
        data, report = C.collect_directory("CR", self.root, "SHA256SUMS", [])
        self.assertNotIn("CR/result.txt", data)
        self.assertNotIn(secret.decode(), str(report))
        self.assertIn("SECRET_PATTERN", report["issues"][0]["reason"])

    def test_expected_hashes_checked_separately(self):
        (self.root / "result.txt").write_text("test")
        _, report = C.collect_directory("CR", self.root, "SHA256SUMS", [], {"result.txt": "0" * 64, "missing.txt": "0" * 64})
        self.assertEqual(report["recorded_hash_checks"], {"result.txt": "MISMATCH", "missing.txt": "MISSING"})

    def test_dns_original_is_not_recompressed(self):
        original = b"fixture of immutable zip bytes"
        (self.root / C.DNS_ZIP).write_bytes(original)
        (self.root / (C.DNS_ZIP + ".sha256")).write_text(C.sha(original) + "  " + C.DNS_ZIP + "\n")
        with patch.object(C, "DNS_HASH", C.sha(original)):
            data, report = C.collect_dns(self.root)
        self.assertEqual(data["P1-DNS-01/" + C.DNS_ZIP], original)
        self.assertEqual(report["recorded_archive_hash"], "MATCH")
        self.assertEqual(report["internal_manifest"], "NOT_VERIFIED")

    def test_wrong_dns_archive_excluded(self):
        (self.root / C.DNS_ZIP).write_bytes(b"wrong archive")
        data, report = C.collect_dns(self.root)
        self.assertNotIn("P1-DNS-01/" + C.DNS_ZIP, data)
        self.assertEqual(report["recorded_archive_hash"], "MISMATCH")

    def test_export_roundtrip_hash_permissions_and_ownership(self):
        uid, gid = os.getuid(), os.getgid()
        folder, archive, sidecar = C.write_export({"CR/result.txt": b"exact\r\n"}, {"handoff_acceptance": "PENDING"}, self.root.parent, uid, gid)
        self.assertEqual(stat.S_IMODE(folder.stat().st_mode), 0o700)
        self.assertEqual(folder.stat().st_uid, uid)
        for path in folder.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(path.stat().st_uid, uid)
        self.assertEqual(sidecar.read_text(), C.sha(archive.read_bytes()) + "  " + archive.name + "\n")
        with tarfile.open(archive) as bundle:
            self.assertEqual(bundle.extractfile("review-input/CR/result.txt").read(), b"exact\r\n")

    def test_sudo_ownership_targets_new_output_only(self):
        # Cross-UID chown is unavailable in some test containers; inspect requests.
        with patch.object(C.os, "geteuid", return_value=0), patch.object(C.os, "chown") as chown:
            folder, _, _ = C.write_export({}, {"fixture": True}, self.root.parent, 1001, 1002)
        self.assertEqual(chown.call_count, 4)
        for call in chown.call_args_list:
            path, uid, gid = call.args
            self.assertTrue(path == folder or path.parent == folder)
            self.assertEqual((uid, gid), (1001, 1002))


if __name__ == "__main__":
    unittest.main()
