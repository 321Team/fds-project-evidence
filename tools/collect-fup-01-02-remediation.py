#!/usr/bin/env python3
"""FUP-01/02 보완 증적을 읽기 전용으로 수집한다.

기존 원본과 매니페스트는 수정하지 않는다. FUP-01은 변경된 다섯 노드의
보존 resolver 상태를 Ansible stat/slurp 모듈로 읽고, FUP-02는 승인본과
구 매니페스트의 바이트를 그대로 새 수신 패키지에 담는다.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import subprocess
import tarfile
import tempfile


VERSION = "1.0"
CHANGE_ID = "CR-P1-ANS-01-01"
STATE_PATH = "/var/lib/fds-change/CR-P1-ANS-01-01/original-resolver.json"
ROLLBACK_HOSTS = (
    "k8s-control02",
    "k8s-control03",
    "k8s-worker01",
    "k8s-worker02",
    "k8s-worker03",
)
REFINALIZATION_SHA256 = (
    "db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d"
)
P1_ANS_CURRENT = {
    "05h_ssh_key_lifecycle_record.md":
        "9f5b8c1b24dc9e44109d57205ca3c13bf54e3b0e05ee53615371f2604065ad95",
    "05j_review_approval_record.md":
        "944d3e74cfc72e9ed0ce56a5914a16fcba7ae35f2145cd243f2e2a5ef172006d",
    "99_SHA256SUMS.txt":
        "45a8d2ae43b62e96636fae1a4c43b8490de26a02e33ceff188b43784f37c8bce",
}
P1_ANS_LEGACY = {
    "05h_ssh_key_lifecycle_record.md":
        "7ab0ad3c1b1610009dfc5c777f17f1bbb74f3a8d172b696ddb22a56d37763752",
    "05j_review_approval_record.md":
        "e64c466161f441b7007e6dfb7bb2dbe1046cf7a74a68653731e66c69f20e826c",
}
MAX_FILE = 32 * 1024 * 1024
STRONG_SECRET = (
    b"-----BEGIN OPENSSH PRIVATE KEY-----",
    b"-----BEGIN RSA PRIVATE KEY-----",
    b"github_pat_",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_original(path: Path) -> tuple[bytes, dict]:
    """심볼릭 링크·특수 파일·읽기 도중 변경된 파일을 거부한다."""
    path = path.absolute()
    if path.resolve() != path:
        raise ValueError(f"SYMLINK_PATH: {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"NOT_REGULAR: {path}")
        if before.st_size > MAX_FILE:
            raise ValueError(f"FILE_TOO_LARGE: {path}")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_FILE + 1)
        after = os.fstat(fd)
        current = path.lstat()
        signature = lambda value: (
            value.st_dev,
            value.st_ino,
            value.st_size,
            value.st_mtime_ns,
            value.st_ctime_ns,
        )
        if len(data) > MAX_FILE or not (
            signature(before) == signature(after) == signature(current)
        ):
            raise ValueError(f"SOURCE_CHANGED_DURING_READ: {path}")
        return data, {
            "bytes": len(data),
            "sha256": digest(data),
            "mode": oct(stat.S_IMODE(before.st_mode)),
            "uid": before.st_uid,
            "gid": before.st_gid,
            "mtime_ns": before.st_mtime_ns,
        }
    finally:
        os.close(fd)


def find_refinalization(root: Path, explicit: Path | None) -> list[tuple[Path, bytes, dict]]:
    candidates = [explicit] if explicit else sorted(root.rglob("*"))
    matches = []
    for candidate in candidates:
        if candidate is None or candidate.is_symlink() or not candidate.is_file():
            continue
        try:
            data, metadata = read_original(candidate)
        except (OSError, ValueError):
            continue
        if metadata["sha256"] == REFINALIZATION_SHA256:
            matches.append((candidate, data, metadata))
    return matches


def run_ansible_tree(project_root: Path, module: str, module_args: str,
                     output: Path) -> dict[str, dict]:
    output.mkdir(mode=0o700)
    target = ",".join(ROLLBACK_HOSTS)
    command = [
        "ansible", target,
        "-i", "inventory/hosts.yml",
        "-b", "-m", module,
        "-a", module_args,
        "--tree", str(output),
    ]
    environment = os.environ.copy()
    environment["ANSIBLE_NOCOLOR"] = "true"
    environment["ANSIBLE_DISPLAY_ARGS_TO_STDOUT"] = "false"
    result = subprocess.run(
        command,
        cwd=project_root,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ANSIBLE_{module.upper()}_FAILED_RC_{result.returncode}")
    records = {}
    for host in ROLLBACK_HOSTS:
        path = output / host
        if not path.is_file():
            raise RuntimeError(f"ANSIBLE_RESULT_MISSING: {host}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("failed"):
            raise RuntimeError(f"ANSIBLE_RESULT_FAILED: {host}")
        records[host] = value
    return records


def stable_stat(value: dict) -> dict:
    source = value.get("stat", {})
    fields = ("checksum", "size", "inode", "mtime", "ctime", "mode", "uid", "gid")
    return {name: source.get(name) for name in fields}


def collect_fup01(project_root: Path, refinalization: Path | None) -> tuple[dict[str, bytes], dict]:
    evidence_root = project_root / "docs" / "evidence" / CHANGE_ID
    payload: dict[str, bytes] = {}
    report = {
        "followup": "FUP-01",
        "source_access": "READ_ONLY",
        "rollback_execution": "NOT_RUN",
        "remote_source": STATE_PATH,
        "hosts": {},
    }

    matches = find_refinalization(evidence_root, refinalization)
    if len(matches) == 1:
        path, data, metadata = matches[0]
        if any(pattern in data for pattern in STRONG_SECRET):
            raise ValueError("REFINALIZATION_SECRET_PATTERN")
        name = path.name
        payload[f"FUP-01/refinalization/{name}"] = data
        report["refinalization"] = {
            "result": "MATCH",
            "source_path": str(path),
            **metadata,
        }
    else:
        report["refinalization"] = {
            "result": "MISSING" if not matches else "MULTIPLE_MATCHES",
            "expected_sha256": REFINALIZATION_SHA256,
            "matches": len(matches),
        }

    with tempfile.TemporaryDirectory(prefix="fds-fup01-") as folder:
        temporary = Path(folder)
        before = run_ansible_tree(
            project_root,
            "ansible.builtin.stat",
            f"path={STATE_PATH} checksum_algorithm=sha256 get_checksum=true",
            temporary / "stat-before",
        )
        slurped = run_ansible_tree(
            project_root,
            "ansible.builtin.slurp",
            f"src={STATE_PATH}",
            temporary / "slurp",
        )
        after = run_ansible_tree(
            project_root,
            "ansible.builtin.stat",
            f"path={STATE_PATH} checksum_algorithm=sha256 get_checksum=true",
            temporary / "stat-after",
        )

        for host in ROLLBACK_HOSTS:
            before_stat = stable_stat(before[host])
            after_stat = stable_stat(after[host])
            if before_stat != after_stat:
                raise ValueError(f"REMOTE_SOURCE_CHANGED: {host}")
            if before_stat["mode"] != "0600" or before_stat["uid"] != 0 or before_stat["gid"] != 0:
                raise ValueError(f"REMOTE_PERMISSION_MISMATCH: {host}")
            data = base64.b64decode(slurped[host]["content"], validate=True)
            if any(pattern in data for pattern in STRONG_SECRET):
                raise ValueError(f"ROLLBACK_SECRET_PATTERN: {host}")
            if digest(data) != before_stat["checksum"]:
                raise ValueError(f"REMOTE_HASH_MISMATCH: {host}")
            decoded = json.loads(data.decode("utf-8"))
            if decoded.get("change_id") != CHANGE_ID or decoded.get("inventory_hostname") != host:
                raise ValueError(f"REMOTE_IDENTITY_MISMATCH: {host}")
            payload[f"FUP-01/rollback-state/{host}/original-resolver.json"] = data
            report["hosts"][host] = {
                "result": "MATCH",
                "sha256": digest(data),
                "bytes": len(data),
                "mode": before_stat["mode"],
                "uid": before_stat["uid"],
                "gid": before_stat["gid"],
                "source_unchanged": True,
            }

    report["status"] = (
        "READY_FOR_IMPORT"
        if report["refinalization"]["result"] == "MATCH"
        and len(report["hosts"]) == len(ROLLBACK_HOSTS)
        else "ROLLBACK_COLLECTED_REFINALIZATION_PENDING"
    )
    return payload, report


def parse_legacy_manifest(data: bytes) -> dict[str, str]:
    result = {}
    for raw in data.decode("utf-8").splitlines():
        if not raw.strip():
            continue
        checksum, name = raw.split(maxsplit=1)
        name = name.lstrip(" *")
        result[Path(name).name] = checksum.lower()
    return result


def collect_fup02(root: Path) -> tuple[dict[str, bytes], dict]:
    originals = {}
    metadata = {}
    for name, expected in P1_ANS_CURRENT.items():
        data, info = read_original(root / name)
        if info["sha256"] != expected:
            raise ValueError(f"UNAPPROVED_CURRENT_HASH: {name}")
        if any(pattern in data for pattern in STRONG_SECRET):
            raise ValueError(f"SECRET_PATTERN: {name}")
        originals[name] = data
        metadata[name] = info

    legacy = parse_legacy_manifest(originals["99_SHA256SUMS.txt"])
    mismatch = {
        name: {"legacy": legacy.get(name), "received": P1_ANS_CURRENT[name]}
        for name in P1_ANS_LEGACY
    }
    if {name: values["legacy"] for name, values in mismatch.items()} != P1_ANS_LEGACY:
        raise ValueError("LEGACY_MANIFEST_VALUES_CHANGED")

    alias = {
        "ticket": "P1-ANS-01",
        "designated_name": "05j_reviewer_approver_record.md",
        "received_legacy_name": "05j_review_approval_record.md",
        "sha256": P1_ANS_CURRENT["05j_review_approval_record.md"],
        "handling": "ALIAS_ONLY_NO_RENAME_NO_BYTE_CHANGE",
    }
    alias_data = (json.dumps(alias, ensure_ascii=False, indent=2) + "\n").encode()
    payload = {
        "FUP-02/originals/05h_ssh_key_lifecycle_record.md": originals["05h_ssh_key_lifecycle_record.md"],
        "FUP-02/originals/05j_review_approval_record.md": originals["05j_review_approval_record.md"],
        "FUP-02/originals/99_SHA256SUMS.legacy.txt": originals["99_SHA256SUMS.txt"],
        "FUP-02/FILENAME_ALIAS.json": alias_data,
    }
    distribution = "".join(
        f"{digest(data)}  {name}\n" for name, data in sorted(payload.items())
    ).encode()
    payload["FUP-02/DISTRIBUTION_SHA256SUMS"] = distribution
    report = {
        "followup": "FUP-02",
        "source_access": "READ_ONLY",
        "source_files": metadata,
        "legacy_manifest_mismatches": mismatch,
        "cause": "APPROVED_FILES_PRESENT_BUT_POST_APPROVAL_MANIFEST_REGEN_NOT_PERFORMED",
        "filename_alignment": alias,
        "new_distribution_manifest": "CREATED_FOR_THIS_RECEIPT_ONLY",
        "past_server_verification": "NOT_CLAIMED",
        "status": "REMEDIATED_PENDING_INDEPENDENT_REVIEW",
    }
    return payload, report


def output_owner():
    if os.geteuid() == 0:
        if not os.environ.get("SUDO_UID") or not os.environ.get("SUDO_USER"):
            raise ValueError("일반 로그인 사용자에서 sudo로 실행해야 합니다")
        user = pwd.getpwuid(int(os.environ["SUDO_UID"]))
    else:
        user = pwd.getpwuid(os.getuid())
    if user.pw_name != "server01_ansible":
        raise ValueError("실행 사용자는 server01_ansible이어야 합니다")
    return user


def write_bundle(payload: dict[str, bytes], report: dict, output_home: Path,
                 uid: int, gid: int) -> tuple[Path, Path]:
    folder = Path(tempfile.mkdtemp(prefix="FDS_FUP01_02_Receipt_", dir=output_home))
    report_data = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    content = {**payload, "COLLECTION_REPORT.json": report_data}
    checksums = "".join(
        f"{digest(data)}  {name}\n" for name, data in sorted(content.items())
    ).encode()
    content["COLLECTION_SHA256SUMS"] = checksums
    archive = folder / "FDS_FUP01_02_Remediation_Receipt_v1.0.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for name, data in sorted(content.items()):
            info = tarfile.TarInfo("review-input/" + name)
            info.size = len(data)
            info.mode = 0o600
            info.uid = uid
            info.gid = gid
            info.mtime = int(dt.datetime.now(dt.timezone.utc).timestamp())
            bundle.addfile(info, io.BytesIO(data))
    sidecar = archive.with_suffix(archive.suffix + ".sha256")
    sidecar.write_text(f"{digest(archive.read_bytes())}  {archive.name}\n", encoding="utf-8")
    for path in folder.iterdir():
        path.chmod(0o600)
        if os.geteuid() == 0:
            os.chown(path, uid, gid)
    folder.chmod(0o700)
    if os.geteuid() == 0:
        os.chown(folder, uid, gid)
    return archive, sidecar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticket", choices=("FUP-01", "FUP-02", "all"), default="all")
    parser.add_argument("--project-root", type=Path, default=Path("/home/server01_ansible/p1-ans-01"))
    parser.add_argument("--refinalization-original", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if socket.gethostname() != "ansible01":
        raise ValueError("ansible01에서만 실행할 수 있습니다")
    owner = output_owner()
    project_root = args.project_root.absolute()
    if project_root.resolve() != project_root or not project_root.is_dir():
        raise ValueError("프로젝트 경로는 실재하는 비심볼릭 디렉터리여야 합니다")

    payload = {}
    reports = []
    if args.ticket in ("FUP-01", "all"):
        data, report = collect_fup01(project_root, args.refinalization_original)
        payload.update(data)
        reports.append(report)
    if args.ticket in ("FUP-02", "all"):
        data, report = collect_fup02(project_root / "docs" / "evidence" / "P1-ANS-01")
        payload.update(data)
        reports.append(report)

    report = {
        "collector_version": VERSION,
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "host": "ansible01",
        "operator": owner.pw_name,
        "source_changes": "NONE",
        "runtime_or_rollback_execution": "NONE",
        "handoff_acceptance": "PENDING",
        "followups": reports,
    }
    archive, sidecar = write_bundle(payload, report, Path(owner.pw_dir), owner.pw_uid, owner.pw_gid)
    print(archive)
    print(sidecar)


if __name__ == "__main__":
    main()
