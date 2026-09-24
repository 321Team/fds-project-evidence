"""증적 경로·예외·대장 점검기의 로컬 fixture 테스트."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import unittest.mock


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "check-evidence-layout.py"
SPEC = importlib.util.spec_from_file_location("layout_checker", SCRIPT)
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)

POLICY = "예외: `evidence/infra-ansible-issue-6/`\n"
EXCEPTIONS = {
    "version": 1,
    "policy": "governance/EVIDENCE_POLICY.md",
    "record_id_pattern": "^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$",
    "path_exceptions": [
        {"path": "evidence/infra-ansible-issue-6/", "reason": "test", "allow_new_content": False}
    ],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class LayoutCheckerTests(unittest.TestCase):
    def build(self, root: Path, extra: dict[str, bytes] | None = None, registry_skip: set[str] | None = None,
              policy: str = POLICY, exceptions: dict | None = None) -> list[str]:
        files = {
            "governance/EVIDENCE_POLICY.md": policy.encode(),
            "governance/EVIDENCE_LAYOUT_EXCEPTIONS.json": json.dumps(exceptions or EXCEPTIONS).encode(),
            "evidence/P1-DB-01/received-1/a.txt": b"a\n",
            "evidence/infra-ansible-issue-6/old/b.txt": b"b\n",
        }
        manifest = (digest(b"a\n") + "  a.txt\n").encode()
        files["evidence/P1-DB-01/received-1/SHA256SUMS"] = manifest
        files.update(extra or {})
        skip = {"evidence/P1-DB-01/received-1/a.txt"} | (registry_skip or set())
        for name, data in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes(data)
        lines = "".join(f"{digest(data)}  {name}\n" for name, data in sorted(files.items()) if name not in skip)
        (root / "REGISTRY_SHA256SUMS").write_text(lines, encoding="utf-8")
        return sorted(files) + ["REGISTRY_SHA256SUMS"]

    def test_clean_layout_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root)
            self.assertEqual(C.check(root, files, []), [])

    def test_new_file_in_frozen_exception_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root, {"evidence/infra-ansible-issue-6/new/c.txt": b"c\n"})
            errors = C.check(root, files, ["evidence/infra-ansible-issue-6/new/c.txt"])
            self.assertTrue(any(e.startswith("FROZEN:") for e in errors), errors)

    def test_unlisted_non_record_directory_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root, {"evidence/infra-ansible-issue-9/x/d.txt": b"d\n"})
            errors = C.check(root, files, None)
            self.assertTrue(any("LAYOUT: evidence/infra-ansible-issue-9/" in e for e in errors), errors)

    def test_exception_missing_from_policy_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root, policy="예외 없음\n")
            errors = C.check(root, files, None)
            self.assertTrue(any(e.startswith("POLICY_SYNC:") for e in errors), errors)

    def test_abbreviated_policy_mention_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            policy = POLICY + "`evidence/infra-ansible-issue-7/`도 예외다\n"
            files = self.build(root, policy=policy)
            errors = C.check(root, files, None)
            self.assertTrue(any("infra-ansible-issue-7/가" in e for e in errors), errors)

    def test_uncovered_file_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root, {"registry/NEW.md": b"n\n"}, registry_skip={"registry/NEW.md"})
            errors = C.check(root, files, None)
            self.assertIn("COVERAGE: registry/NEW.md — 대장에도, 대장에 등록된 Manifest에도 없다", errors)

    def test_manifest_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.build(root)
            (root / "evidence/P1-DB-01/received-1/a.txt").write_bytes(b"changed\n")
            errors = C.check(root, files, None)
            self.assertTrue(any(e.startswith("MANIFEST:") and "해시 불일치" in e for e in errors), errors)

    def add_zip(self, root: Path, files: list[str], name: str, members: dict[str, bytes],
                index: bool = True, tamper: bool = False) -> list[str]:
        import io, zipfile
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for member, body in members.items():
                archive.writestr(member, body)
        data = buffer.getvalue()
        path = f"evidence/P1-DB-01/received-1/{name}"
        (root / path).write_bytes(data)
        (root / (path + ".sha256")).write_text(digest(data) + f"  {name}\n")
        entries = sorted(({"name": m, "size": len(b), "sha256": digest(b)} for m, b in members.items()),
                         key=lambda item: item["name"])
        if tamper:
            entries = entries[:-1]
        if index:
            (root / "registry").mkdir(exist_ok=True)
            payload = {"version": 1, "archives": {path: {"sha256": digest(data), "size": len(data), "entries": entries}}}
            (root / "registry/ARCHIVE_CONTENTS.json").write_text(json.dumps(payload))
        return files + [path, path + ".sha256"]

    def test_archive_requires_matching_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.add_zip(root, self.build(root), "pkg.zip", {"a.txt": b"a"})
            (root / "evidence/P1-DB-01/received-1/pkg.zip.sha256").write_text(digest(b"other") + "  pkg.zip\n")
            errors = C.check(root, files, None)
            self.assertTrue(any("sidecar 해시와 바이트가 다르다" in e for e in errors), errors)

    def test_archive_listing_is_recomputed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.add_zip(root, self.build(root), "pkg.zip", {"a.txt": b"a", "b.txt": b"b"})
            self.assertFalse([e for e in C.check(root, files, None) if e.startswith("ARCHIVE:")])
            files = self.add_zip(root, self.build(root), "pkg.zip", {"a.txt": b"a", "b.txt": b"b"}, tamper=True)
            errors = C.check(root, files, None)
            self.assertTrue(any("내부 목록이 실제 내용과 다르다" in e for e in errors), errors)

    def test_archive_without_listing_or_oversized_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = self.add_zip(root, self.build(root), "pkg.zip", {"a.txt": b"a"}, index=False)
            errors = C.check(root, files, None)
            self.assertTrue(any("내부 파일 목록이 없다" in e for e in errors), errors)
            with unittest.mock.patch.object(C, "ARCHIVE_MAX_BYTES", 10):
                files = self.add_zip(root, self.build(root), "pkg.zip", {"a.txt": b"a" * 100})
                errors = C.check(root, files, None)
            self.assertTrue(any("보관 한도" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
