#!/usr/bin/env python3
"""FUP-01 Refinalization 원본만 로컬에서 찾아 새 수신 패키지로 보존한다."""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import socket
import stat
import tarfile
import tempfile
import zipfile
import zlib

VERSION = "1.0"
EXPECTED_SHA256 = "db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d"
MAX_FILE = 8 * 1024 * 1024
MAX_ARCHIVE = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_ENTRIES = 20000
TEXT_SUFFIXES = {".md", ".txt", ".json", ".log", ".csv", ".yaml", ".yml", ".sha256"}
SECRET = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|\bBearer\s+[A-Za-z0-9._~+/-]{12,}", re.I)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def metadata(s: os.stat_result) -> dict:
    return {"device": s.st_dev, "inode": s.st_ino, "size": s.st_size,
            "mode": oct(stat.S_IMODE(s.st_mode)), "uid": s.st_uid,
            "gid": s.st_gid, "mtime_ns": s.st_mtime_ns, "ctime_ns": s.st_ctime_ns}


def read_stable(path: Path, limit: int) -> tuple[bytes, dict]:
    """소스 수정 없이 읽으며 심볼릭 링크·특수 파일·읽는 중 변경을 거부한다."""
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("SYMLINK")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("NOT_REGULAR")
    if before.st_size > limit:
        raise ValueError("SIZE_LIMIT")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if (len(data) > limit or metadata(before) != metadata(opened)
            or metadata(before) != metadata(after)
            or metadata(before) != metadata(path.lstat())):
        raise ValueError("SOURCE_CHANGED_OR_LIMIT")
    return data, {"before": metadata(before), "after": metadata(after),
                  "stable_fields_match": True, "atime_preservation": "NOT_CLAIMED"}


def text_candidate(name: str) -> bool:
    p = PurePosixPath(name)
    return p.suffix.lower() in TEXT_SUFFIXES or not p.suffix or bool(re.search(r"refinal|finalization|재최종", p.name, re.I))


def safe_member(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts and "\\" not in name and not re.match(r"^[A-Za-z]:", name)


class Finder:
    def __init__(self, roots: list[Path], include_archives: bool = False):
        self.roots = roots
        self.include_archives = include_archives
        self.original = None
        self.seen = set()
        self.total = 0
        self.entries = 0
        self.report = {
            "tool": "collect-fup01-refinalization.py", "version": VERSION,
            "collected_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "expected_sha256": EXPECTED_SHA256, "search_roots": [str(p) for p in roots],
            "include_archives": include_archives, "matches": [], "named_candidates": [],
            "issues": [], "skipped": {"hidden_or_link": 0, "non_candidate": 0, "archives_disabled": 0},
            "limits": {"file_bytes": MAX_FILE, "archive_bytes": MAX_ARCHIVE,
                       "total_read_bytes": MAX_TOTAL, "entries": MAX_ENTRIES},
            "scope": "LOCAL_FILES_ONLY_NO_NETWORK_NO_ANSIBLE_NO_RUNTIME",
            "source_changes": "NO_WRITE_OPERATIONS; reads may update access time",
            "excluded": "Hidden paths, symlinks, special files, non-text candidates, nested archives",
            "global_absence": "NOT_ESTABLISHED", "independent_review": "PENDING",
        }

    def issue(self, source: str, reason: str):
        self.report["issues"].append({"source": source, "reason": reason})

    def check(self, data: bytes, source: dict):
        checksum = sha256(data)
        label = source.get("member", source["path"])
        if re.search(r"refinal|finalization|재최종", label, re.I):
            self.report["named_candidates"].append({**source, "sha256": checksum})
        if checksum != EXPECTED_SHA256:
            return
        if SECRET.search(data):
            self.issue(source["path"], "MATCH_BLOCKED_SECRET_PATTERN")
            return
        self.original = data
        self.report["matches"].append({**source, "sha256": checksum, "bytes": len(data)})

    def budget(self, size: int):
        self.total += size
        if self.total > MAX_TOTAL:
            raise ValueError("TOTAL_READ_LIMIT")

    def visit_member(self, name: str, size: int, stream, source: dict):
        self.entries += 1
        if self.entries > MAX_ENTRIES:
            raise ValueError("ENTRY_LIMIT")
        if not safe_member(name):
            raise ValueError("UNSAFE_ARCHIVE_PATH")
        if not text_candidate(name):
            self.report["skipped"]["non_candidate"] += 1
            return
        if size > MAX_FILE:
            raise ValueError("MEMBER_SIZE_LIMIT")
        self.budget(size)
        with stream() as reader:
            data = reader.read(MAX_FILE + 1)
        if len(data) != size or len(data) > MAX_FILE:
            raise ValueError("MEMBER_SIZE_MISMATCH")
        self.check(data, {**source, "member": name})

    def scan_archive(self, path: Path, data: bytes, info: dict):
        source = {"path": str(path), "kind": "archive_member", "archive_sha256": sha256(data), "source_stat": info}
        if path.name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as bundle:
                members = bundle.infolist()
                if len(members) > MAX_ENTRIES:
                    raise ValueError("ENTRY_LIMIT")
                names = set()
                for item in members:
                    if item.filename in names:
                        raise ValueError("DUPLICATE_ARCHIVE_PATH")
                    names.add(item.filename)
                    if not safe_member(item.filename):
                        raise ValueError("UNSAFE_ARCHIVE_PATH")
                    if item.is_dir():
                        continue
                    mode = item.external_attr >> 16
                    if stat.S_ISLNK(mode):
                        raise ValueError("ARCHIVE_LINK")
                    if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                        raise ValueError("ARCHIVE_SPECIAL_FILE")
                    self.visit_member(item.filename, item.file_size, lambda: bundle.open(item), source)
        else:
            if data.startswith(b"\x1f\x8b"):
                with gzip.GzipFile(fileobj=io.BytesIO(data)) as compressed:
                    data = compressed.read(MAX_ARCHIVE + 1)
                if len(data) > MAX_ARCHIVE:
                    raise ValueError("DECOMPRESSED_ARCHIVE_LIMIT")
                self.budget(len(data))
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as bundle:
                names = set()
                for item in bundle:
                    if len(names) >= MAX_ENTRIES:
                        raise ValueError("ENTRY_LIMIT")
                    if item.name in names:
                        raise ValueError("DUPLICATE_ARCHIVE_PATH")
                    names.add(item.name)
                    if not safe_member(item.name):
                        raise ValueError("UNSAFE_ARCHIVE_PATH")
                    if item.isdir():
                        continue
                    if not item.isfile():
                        raise ValueError("ARCHIVE_LINK_OR_SPECIAL")
                    self.visit_member(item.name, item.size, lambda: bundle.extractfile(item), source)

    def scan_file(self, path: Path, explicit: bool = False):
        if str(path) in self.seen:
            return
        self.seen.add(str(path))
        self.entries += 1
        if self.entries > MAX_ENTRIES:
            self.issue(str(path), "ENTRY_LIMIT")
            return
        archive = path.name.lower().endswith((".zip", ".tar", ".tar.gz", ".tgz"))
        if archive and not self.include_archives:
            self.report["skipped"]["archives_disabled"] += 1
            return
        if not archive and not explicit and not text_candidate(path.name):
            self.report["skipped"]["non_candidate"] += 1
            return
        try:
            size = path.lstat().st_size
            if self.total + size > MAX_TOTAL:
                raise ValueError("TOTAL_READ_LIMIT")
            data, info = read_stable(path, MAX_ARCHIVE if archive else MAX_FILE)
            self.budget(len(data))
            if archive:
                self.scan_archive(path, data, info)
            else:
                self.check(data, {"path": str(path), "kind": "file", "source_stat": info})
        except (OSError, ValueError, EOFError, RuntimeError, zlib.error, zipfile.BadZipFile, tarfile.TarError) as exc:
            self.issue(str(path), type(exc).__name__ + ": " + str(exc))

    def run(self):
        for root in self.roots:
            if not root.exists() or any(p.is_symlink() for p in (root, *root.parents)):
                self.issue(str(root), "MISSING_OR_SYMLINK_ROOT")
                continue
            if root.is_file():
                self.scan_file(root, explicit=True)
                continue
            def onerror(exc):
                self.issue(str(exc.filename), "UNREADABLE_DIRECTORY")
            for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
                self.entries += 1
                if self.entries >= MAX_ENTRIES:
                    self.issue(str(root), "DIRECTORY_ENTRY_LIMIT")
                    break
                kept = [d for d in dirs if not d.startswith(".") and not (Path(directory) / d).is_symlink()]
                self.report["skipped"]["hidden_or_link"] += len(dirs) - len(kept)
                dirs[:] = sorted(kept)
                for name in sorted(files):
                    path = Path(directory) / name
                    if name.startswith(".") or path.is_symlink():
                        self.report["skipped"]["hidden_or_link"] += 1
                        continue
                    if self.total >= MAX_TOTAL or self.entries >= MAX_ENTRIES:
                        self.issue(str(root), "SEARCH_LIMIT_REACHED")
                        break
                    self.scan_file(path)
                else:
                    continue
                break
        self.report["read_bytes"] = self.total
        self.report["entries_examined"] = self.entries
        found = self.original is not None
        self.report["status"] = ("MATCH_FOUND_REVIEW_REQUIRED" if found else
                                  "SEARCH_INCOMPLETE" if self.report["issues"] else "NOT_FOUND_IN_SCOPE")
        self.report["search_complete_within_filters"] = not bool(self.report["issues"])
        return self.report


def write_bundle(finder: Finder, output_parent: Path) -> tuple[Path, Path]:
    folder = Path(tempfile.mkdtemp(prefix="FDS_FUP01_Refinalization_", dir=output_parent))
    os.chmod(folder, 0o700)
    payload = {"SEARCH_REPORT.json": (json.dumps(finder.report, ensure_ascii=False, indent=2) + "\n").encode()}
    if finder.original is not None:
        payload["originals/refinalization-original.bin"] = finder.original
    payload["SHA256SUMS"] = "".join(f"{sha256(b)}  {n}\n" for n, b in sorted(payload.items())).encode()
    archive = folder / "FDS_FUP01_Refinalization_Result_v1.0.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for name, data in sorted(payload.items()):
            item = tarfile.TarInfo("review-input/" + name)
            item.size, item.mode = len(data), 0o600
            bundle.addfile(item, io.BytesIO(data))
    sidecar = archive.with_name(archive.name + ".sha256")
    sidecar.write_text(f"{sha256(archive.read_bytes())}  {archive.name}\n", encoding="utf-8")
    return archive, sidecar


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-root", type=Path, action="append", required=True,
                        help="탐색할 기존 디렉터리 또는 원본 파일. 반복 지정 가능")
    parser.add_argument("--include-archives", action="store_true", help="ZIP/tar/tar.gz 내부 텍스트도 검사. 중첩 압축은 제외")
    args = parser.parse_args()
    if socket.gethostname().split(".")[0] != "ansible01" or pwd.getpwuid(os.geteuid()).pw_name != "server01_ansible":
        parser.error("ansible01의 server01_ansible 일반 계정에서 실행하십시오. sudo는 사용하지 않습니다.")
    os.umask(0o077)
    roots = [Path(os.path.abspath(p.expanduser())) for p in args.search_root]
    finder = Finder(roots, args.include_archives)
    finder.report["host"] = socket.gethostname()
    finder.report["operator"] = pwd.getpwuid(os.geteuid()).pw_name
    finder.report["collector_sha256"] = sha256(Path(__file__).read_bytes())
    report = finder.run()
    archive, sidecar = write_bundle(finder, Path.home())
    print("STATUS=" + report["status"])
    print("MATCHES=" + str(len(report["matches"])))
    print("ISSUES=" + str(len(report["issues"])))
    print("ARCHIVE=" + str(archive))
    print("SIDECAR=" + str(sidecar))
    return 0 if finder.original is not None else 3 if report["issues"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
