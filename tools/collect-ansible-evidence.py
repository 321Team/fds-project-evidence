#!/usr/bin/env python3
"""ansible01 evidence export. Read source bytes; write a new private output only."""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import pwd
import re
import socket
import stat
import tarfile
import tempfile

VERSION = "1.0"
DNS_ZIP = "P1-DNS-01-FRESH-20260902-R2.zip"
DNS_HASH = "e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab"
CR_HASHES = {
    "EVIDENCE_INDEX.md": "6f5568d805a5d7f43130d2fdca2ba631358f4f8be23e1f7d0799ae8243c7db1e",
    "SHA256SUMS": "05de9ba6b22d36ef8fc67bdf3dd8c6629c3e334fbb61620a265a46acdbfd4115",
    "20260904T180632+0900_verify_all_nodes.txt": "18cbda0fc7d91ebf58c89c230dccabaf9ad8239305856da03067210582194e83",
    "20260904T182705+0900_integrity_check.txt": "35a320650312e343764a5d7eecfe70c42bafcf43c8043a422d920030a20dee14",
}
REFINALIZATION_HASH = "db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d"
ANS_REQUIRED = ["03_inventory_validation.txt", "04b_ansible_ping_success.txt",
                "05h_ssh_key_lifecycle_record.md", "05j_reviewer_approver_record.md",
                "06h_full_idempotency.txt", "07_final_ansible_ping.txt", "99_SHA256SUMS.txt"]
TEXT_SUFFIXES = {".txt", ".md", ".log", ".json", ".csv", ".yml", ".yaml", ".cfg", ".conf"}
STRONG_SECRET = re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
MAX_FILE = 256 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def original_bytes(path):
    """Reject symlinks/special files and detect changes while reading."""
    path = Path(path).absolute()
    if path.resolve() != path:
        raise ValueError("SYMLINK_PATH")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("NOT_REGULAR")
        if before.st_size > MAX_FILE:
            raise ValueError("FILE_TOO_LARGE")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_FILE + 1)
        after = os.fstat(fd)
        current = path.lstat()
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if len(data) > MAX_FILE or signature(before) != signature(after) or signature(after) != signature(current):
            raise ValueError("SOURCE_CHANGED_DURING_READ")
        return data, {"mode": oct(stat.S_IMODE(before.st_mode)), "uid": before.st_uid,
                      "gid": before.st_gid, "bytes": len(data), "sha256": sha(data),
                      "mtime_ns": before.st_mtime_ns}
    finally:
        os.close(fd)


def manifest_report(data, copied, root):
    """Check existing manifest against the collected bytes, never run its text."""
    results, seen = [], set()
    for line in data.decode("utf-8").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64}) [ *](.+)", line)
        if not match:
            results.append({"result": "INVALID_MANIFEST_LINE"})
            continue
        digest, name = match.groups()
        candidate = Path(name)
        if ".." in candidate.parts or any(ord(c) < 32 for c in name) or "\\" in name:
            results.append({"result": "UNSAFE_MANIFEST_PATH"})
            continue
        if candidate.is_absolute():
            try:
                rel = candidate.relative_to(root).as_posix()
            except ValueError:
                results.append({"result": "OUTSIDE_TICKET_ROOT"})
                continue
        else:
            prefix = "docs/evidence/" + root.name + "/"
            rel = candidate.as_posix()
            if rel.startswith(prefix):
                rel = rel[len(prefix):]
        if rel in seen:
            results.append({"path": rel, "result": "DUPLICATE_ENTRY"})
            continue
        seen.add(rel)
        actual = copied.get(rel)
        result = "NOT_COLLECTED" if actual is None else "MATCH" if sha(actual) == digest.lower() else "MISMATCH"
        results.append({"path": rel, "result": result})
    return {"result": "MATCH" if results and all(x["result"] == "MATCH" for x in results) else "REVIEW_REQUIRED",
            "entries": results, "unlisted_files": sorted(set(copied) - seen)}


def collect_directory(ticket, root, manifest, required, expected=None):
    record = {"ticket": ticket, "source_root": str(root), "files": [], "issues": [],
              "test_verdict": "NOT_ASSESSED", "handoff_acceptance": "PENDING"}
    copied = {}
    try:
        if root.resolve() != root or not root.is_dir():
            raise ValueError("MISSING_OR_SYMLINK_ROOT")
        total = 0
        def walk_error(error):
            raise error
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            for name in list(dirs):
                if (Path(directory) / name).is_symlink():
                    dirs.remove(name)
                    record["issues"].append({"path": str((Path(directory) / name).relative_to(root)), "reason": "SYMLINK_DIRECTORY"})
            for name in sorted(files):
                path = Path(directory) / name
                rel = path.relative_to(root).as_posix()
                try:
                    if any(ord(c) < 32 for c in rel) or "\\" in rel:
                        raise ValueError("UNSUPPORTED_FILENAME")
                    if path.suffix.lower() not in TEXT_SUFFIXES and name not in {"SHA256SUMS", "PACKAGE_SHA256SUMS"}:
                        raise ValueError("UNSUPPORTED_FILE_TYPE")
                    data, meta = original_bytes(path)
                    data.decode("utf-8")
                    if STRONG_SECRET.search(data):
                        raise ValueError("SECRET_PATTERN_REQUIRES_LOCAL_REVIEW")
                    if total + len(data) > MAX_TOTAL:
                        raise ValueError("TICKET_SIZE_LIMIT")
                    copied[rel] = data
                    total += len(data)
                    record["files"].append({"path": rel, **meta})
                except (OSError, ValueError) as error:
                    record["issues"].append({"path": rel, "reason": type(error).__name__ + ": " + str(error)})
    except (OSError, ValueError) as error:
        record["issues"].append({"reason": type(error).__name__ + ": " + str(error)})
    record["missing_required"] = [name for name in required if name not in copied]
    if manifest in copied:
        try:
            record["original_manifest"] = manifest_report(copied[manifest], copied, root)
        except UnicodeError:
            record["original_manifest"] = {"result": "INVALID_ENCODING"}
    else:
        record["original_manifest"] = {"result": "MISSING_NOT_VERIFIED"}
    if expected:
        record["recorded_hash_checks"] = {name: "MISSING" if name not in copied else "MATCH" if sha(copied[name]) == digest else "MISMATCH"
                                          for name, digest in expected.items()}
        record["refinalization_hash_matches"] = [name for name, data in copied.items() if sha(data) == REFINALIZATION_HASH]
    record["collection"] = "REVIEW_REQUIRED"
    return {ticket + "/" + name: data for name, data in copied.items()}, record


def collect_dns(root):
    record = {"ticket": "P1-DNS-01", "source_root": str(root), "files": [], "issues": [],
              "collection": "REVIEW_REQUIRED", "internal_manifest": "NOT_VERIFIED",
              "test_verdict": "NOT_ASSESSED", "handoff_acceptance": "PENDING"}
    payload = {}
    for name in [DNS_ZIP, DNS_ZIP + ".sha256"]:
        try:
            data, meta = original_bytes(root / name)
            payload[name] = data
            record["files"].append({"path": name, **meta})
        except (OSError, ValueError) as error:
            record["issues"].append({"path": name, "reason": str(error)})
    archive = payload.get(DNS_ZIP)
    record["recorded_archive_hash"] = "MISSING" if archive is None else "MATCH" if sha(archive) == DNS_HASH else "MISMATCH"
    sidecar = payload.get(DNS_ZIP + ".sha256")
    record["sidecar"] = {"result": "MISSING_NOT_VERIFIED"}
    if sidecar is not None:
        try:
            record["sidecar"] = manifest_report(sidecar, {DNS_ZIP: archive} if archive is not None else {}, root)
        except UnicodeError:
            record["sidecar"] = {"result": "INVALID_ENCODING"}
    # A different archive must not be exported as the approved immutable R2 original.
    if archive is not None and record["recorded_archive_hash"] != "MATCH":
        payload.pop(DNS_ZIP)
        record["issues"].append({"path": DNS_ZIP, "reason": "ARCHIVE_NOT_EXPORTED_HASH_MISMATCH"})
    record["archive_handling"] = "UNCHANGED_BYTES; NO_EXTRACTION; NO_REPACK; CONTENT_SCAN_NOT_PERFORMED"
    return {"P1-DNS-01/" + name: data for name, data in payload.items()}, record


def output_owner():
    if os.geteuid() == 0:
        if not os.environ.get("SUDO_UID") or not os.environ.get("SUDO_USER"):
            raise ValueError("Run from the normal login user with sudo; direct root invocation is unsupported")
        user = pwd.getpwuid(int(os.environ["SUDO_UID"]))
        if user.pw_uid == 0 or user.pw_name != os.environ["SUDO_USER"]:
            raise ValueError("Invalid sudo caller identity")
    else:
        user = pwd.getpwuid(os.getuid())
    if user.pw_name != "server01_ansible":
        raise ValueError("Expected login user server01_ansible")
    return user


def write_export(payload, report, output_home, uid, gid):
    """Only the newly created directory and its three files receive ownership changes."""
    folder = Path(tempfile.mkdtemp(prefix="FDS_Evidence_Receipt_", dir=output_home))
    report_data = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    content = {**payload, "COLLECTION_REPORT.json": report_data}
    checksum = "".join(sha(data) + "  " + name + "\n" for name, data in sorted(content.items())).encode()
    content["COLLECTION_SHA256SUMS"] = checksum
    archive = folder / "FDS_Evidence_Receipt_v1.0.tar.gz"
    try:
        with tarfile.open(archive, "w:gz") as bundle:
            for name, data in sorted(content.items()):
                info = tarfile.TarInfo("review-input/" + name)
                info.size, info.mode, info.uid, info.gid = len(data), 0o600, uid, gid
                info.mtime = int(dt.datetime.now(dt.timezone.utc).timestamp())
                bundle.addfile(info, io.BytesIO(data))
        digest = sha(archive.read_bytes())
        sidecar = folder / (archive.name + ".sha256")
        sidecar.write_text(digest + "  " + archive.name + "\n", encoding="utf-8")
        (folder / "COLLECTION_REPORT.json").write_bytes(report_data)
        # Verify our new output, not historical tests or approvals.
        with tarfile.open(archive, "r:gz") as bundle:
            if {m.name for m in bundle.getmembers()} != {"review-input/" + n for n in content}:
                raise ValueError("OUTPUT_MEMBER_MISMATCH")
            for name, data in content.items():
                if bundle.extractfile("review-input/" + name).read() != data:
                    raise ValueError("OUTPUT_BYTES_MISMATCH")
        return folder, archive, sidecar
    finally:
        for path in folder.iterdir():
            os.chmod(path, 0o600)
            if os.geteuid() == 0:
                os.chown(path, uid, gid)
        os.chmod(folder, 0o700)
        if os.geteuid() == 0:
            os.chown(folder, uid, gid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticket", choices=["all", "CR-P1-ANS-01-01", "P1-ANS-01", "P1-DNS-01"], default="all")
    args = parser.parse_args()
    os.umask(0o077)
    if socket.gethostname() != "ansible01":
        raise ValueError("Expected host ansible01")
    owner = output_owner()
    home = Path(owner.pw_dir)
    if home.resolve() != home or not home.is_dir():
        raise ValueError("Home must be an existing non-symlink directory")
    root = home / "p1-ans-01" / "docs" / "evidence"
    jobs = {
        "CR-P1-ANS-01-01": lambda: collect_directory("CR-P1-ANS-01-01", root / "CR-P1-ANS-01-01", "SHA256SUMS", list(CR_HASHES), CR_HASHES),
        "P1-ANS-01": lambda: collect_directory("P1-ANS-01", root / "P1-ANS-01", "99_SHA256SUMS.txt", ANS_REQUIRED),
        "P1-DNS-01": lambda: collect_dns(home / "p1-dns-01-r2" / "docs" / "evidence" / "P1-DNS-01"),
    }
    payload, reports = {}, []
    for ticket, job in jobs.items():
        if args.ticket in {"all", ticket}:
            data, report = job()
            payload.update(data)
            reports.append(report)
    report = {"collector_version": VERSION, "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
              "host": "ansible01", "operator": owner.pw_name, "source_access": "READ_ONLY",
              "scope": "three approved ticket roots only; no SSH keys, environment or whole project export",
              "source_changes": "NONE; no chmod/chown, original manifest rewrite, git pull or server test",
              "content_scan": "known strong secret patterns for text only; not exhaustive; DNS ZIP not scanned",
              "test_verdict": "NOT_ASSESSED", "handoff_acceptance": "PENDING", "bootstrap": "HOLD",
              "tickets": reports}
    folder, archive, sidecar = write_export(payload, report, home, owner.pw_uid, owner.pw_gid)
    print("[REVIEW EXPORT READY]")
    print("ARCHIVE=" + str(archive))
    print("SIDECAR=" + str(sidecar))
    print("REPORT=" + str(folder / "COLLECTION_REPORT.json"))
    for record in reports:
        print(record["ticket"] + ": REVIEW_REQUIRED; collected=" + str(sum(n.startswith(record["ticket"] + "/") for n in payload)) + "; issues=" + str(len(record["issues"])))
    print("SOURCE_UNCHANGED; RECEIVER_APPROVAL=PENDING; BOOTSTRAP=HOLD")
    print("Transfer only the ARCHIVE and SIDECAR shown above to the agreed review destination.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("[FAIL] " + str(error))
