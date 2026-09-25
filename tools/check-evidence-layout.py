#!/usr/bin/env python3
"""증적 저장소의 경로·예외·해시 대장 규칙을 읽기 전용으로 점검한다.

EVIDENCE_POLICY의 "저장 경로"와 "REGISTRY_SHA256SUMS 등록 범위"를 기계적으로
확인한다. 예외 목록의 정본은 governance/EVIDENCE_LAYOUT_EXCEPTIONS.json이며,
정책 문서에 적힌 예외와 어긋나면 실패한다. 파일을 수정하지 않는다.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import zipfile


REGISTRY = "REGISTRY_SHA256SUMS"
EXCEPTIONS = "governance/EVIDENCE_LAYOUT_EXCEPTIONS.json"
MANIFEST_NAME = re.compile(r"SHA256SUMS[^/]*$")
ARCHIVE_NAME = re.compile(r"\.(zip|tar|tar\.gz|tgz|tar\.xz|7z)$")
ARCHIVE_INDEX = "registry/ARCHIVE_CONTENTS.json"
ARCHIVE_MAX_BYTES = 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_sums(path: Path) -> list[tuple[str, str]]:
    """sha256sum 형식을 (hash, 상대경로) 목록으로 읽는다. 해시 형식이 아닌 줄은 무시한다."""
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([0-9a-f]{64}) [ *](.+)$", line)
        if match:
            entries.append((match.group(1), match.group(2)))
    return entries


def normalize(base: PurePosixPath, name: str) -> str:
    parts = []
    for part in (base / name).parts:
        if part == ".":
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def archive_entries(path: Path) -> list[dict]:
    """압축 파일 안의 일반 파일 목록(이름·크기·SHA-256)을 바이트에서 직접 계산한다."""
    data = path.read_bytes()
    entries = []
    if path.name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                body = archive.read(info)
                entries.append({"name": info.filename, "size": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    else:
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for member in archive.getmembers():
                if member.isdir():
                    continue
                if not member.isfile():
                    entries.append({"name": member.name, "size": 0, "sha256": None, "type": "link-or-special"})
                    continue
                body = archive.extractfile(member).read()
                entries.append({"name": member.name, "size": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    return sorted(entries, key=lambda item: item["name"])


def tracked_files(root: Path) -> list[str]:
    output = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True
    ).stdout.decode("utf-8")
    return [name for name in output.split("\0") if name]


def changed_files(root: Path, base: str) -> list[tuple[str, str]]:
    """기준 ref와의 merge-base 대비 변경을 (상태, 경로)로 돌려준다. 이름 변경은 삭제+추가로 본다."""
    output = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames", "-z", f"{base}...HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")
    parts = [part for part in output.split("\0") if part]
    return [(parts[i][0], parts[i + 1]) for i in range(0, len(parts) - 1, 2)]


def base_files(root: Path, base: str) -> list[str]:
    """기준 ref와의 merge-base에 있던 추적 파일 목록."""
    merge_base = subprocess.run(
        ["git", "merge-base", base, "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    output = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", merge_base], cwd=root, check=True, capture_output=True
    ).stdout.decode("utf-8")
    return [name for name in output.split("\0") if name]


def sealed_collections(names: list[str]) -> set[str]:
    """이미 있는 수집회차 폴더: evidence/<ID>/ 아래에서 파일을 직접 가진 폴더."""
    sealed = set()
    for name in names:
        parts = name.split("/")
        if parts[0] == "evidence" and len(parts) >= 4:
            sealed.add("/".join(parts[:-1]) + "/")
    return sealed


def check(root: Path, files: list[str], new_files: list[str] | None,
          changes: list[tuple[str, str]] | None = None, before: list[str] | None = None,
          warnings: list[str] | None = None) -> list[str]:
    errors: list[str] = []
    warnings = warnings if warnings is not None else []
    file_set = set(files)

    config = json.loads((root / EXCEPTIONS).read_text(encoding="utf-8"))
    pattern = re.compile(config["record_id_pattern"])
    exceptions = {item["path"].rstrip("/") + "/": item for item in config["path_exceptions"]}
    for path, item in exceptions.items():
        record_id = item.get("record_id", "")
        if not pattern.match(record_id):
            errors.append(f"EXCEPTION: {path} — 상위 Record ID(record_id)가 없거나 형식이 맞지 않다")

    # 1. 정책 문서와 예외 목록의 일치
    policy_text = (root / config["policy"]).read_text(encoding="utf-8")
    for path in exceptions:
        if path.rstrip("/") not in policy_text:
            errors.append(f"POLICY_SYNC: 예외 {path}가 {config['policy']}에 없다")
    for mentioned in sorted(set(re.findall(r"evidence/infra-ansible-[a-z0-9-]+", policy_text))):
        if mentioned + "/" not in exceptions:
            errors.append(f"POLICY_SYNC: 정책에 적힌 {mentioned}/가 {EXCEPTIONS}에 없다")

    # 2. evidence/ 최상위 경로는 Record ID 또는 등록된 예외
    for top in sorted({name.split("/")[1] for name in files if name.startswith("evidence/") and name.count("/") >= 2}):
        path = f"evidence/{top}/"
        if not pattern.match(top) and path not in exceptions:
            errors.append(f"LAYOUT: {path}는 Record ID 형식이 아니고 예외 목록에도 없다")
    for path in exceptions:
        if not any(name.startswith(path) for name in files):
            errors.append(f"LAYOUT: 예외 {path}에 해당하는 파일이 없다(예외 목록 정리 필요)")

    # 3. 새 증적을 닫힌 예외 경로에 추가하지 않는다
    if new_files is not None:
        for name in new_files:
            for path, item in exceptions.items():
                if name.startswith(path) and not item.get("allow_new_content", False):
                    errors.append(f"FROZEN: {name} — 예외 경로 {path}에는 새 증적을 추가하지 않는다")

    # 3-1. 기준 ref에 이미 있는 증적은 바꾸지 않는다. 기존 evidence/ 파일의 변경·삭제와
    #      기존 수집회차 폴더(하위 폴더 포함) 안의 새 파일을 막는다. 정정·보완은 새 경로에 둔다.
    if changes is not None and before is not None:
        before_set = set(before)
        sealed = sealed_collections(before)
        for status, name in changes:
            if not name.startswith("evidence/") or any(name.startswith(path) for path in exceptions):
                continue
            if status != "A" and name in before_set:
                errors.append(f"SEALED: {name} — 기준에 있는 증적을 변경·삭제하지 않는다(정정은 새 기록으로)")
                continue
            if status == "A":
                parts = name.split("/")
                for depth in range(3, len(parts)):
                    folder = "/".join(parts[:depth]) + "/"
                    if folder in sealed:
                        errors.append(f"SEALED: {name} — 기존 수집회차 {folder} 안에 새 파일을 두지 않는다(새 경로 사용)")
                        break

    # 4. 대장 해시 확인
    registry = read_sums(root / REGISTRY)
    covered = set()
    trusted_manifests = []
    for value, name in registry:
        target = root / name
        if name not in file_set or not target.is_file():
            errors.append(f"REGISTRY: {name} — 대장에 있으나 추적 파일이 아니다")
            continue
        if sha256(target) != value:
            errors.append(f"REGISTRY: {name} — 해시 불일치")
        covered.add(name)
        if name.startswith("evidence/") and MANIFEST_NAME.search(name):
            trusted_manifests.append(name)

    # 5. 대장에 직접 등록됐고 대장에 없는 파일을 확인하는 수집회차 Manifest만 검사한다.
    #    과거에 개별 등록된 원본 Manifest(서버 쪽 경로를 기록한 데이터)와, Manifest 안에
    #    든 하위 원본 Manifest(선별 편입이라 일부 파일만 Git에 있음)는 검사 대상이 아니다.
    registered = set(covered)
    for manifest in trusted_manifests:
        base = PurePosixPath(manifest).parent
        entries = [(value, entry, normalize(base, entry)) for value, entry in read_sums(root / manifest)]
        # Manifest는 자기 폴더 안의 파일만 확인할 수 있다. 밖을 가리키면 다른 폴더의 파일이
        # 이 Manifest로 "확인됨" 처리될 수 있으므로 오류로 막는다.
        outside = [entry for _, entry, name in entries if not name.startswith(f"{base}/")]
        for entry in outside:
            errors.append(f"MANIFEST: {manifest} — {entry}는 Manifest 폴더 밖을 가리킨다")
        entries = [item for item in entries if item[1] not in outside]
        if entries and not any(name in file_set for _, _, name in entries):
            warnings.append(f"WARN: {manifest} — 항목 {len(entries)}개가 모두 Git에 없어 대조를 건너뛴다(서버 경로 기록 등 선별 편입)")
        if not any(name in file_set and name not in registered for _, _, name in entries):
            continue
        for value, entry, name in entries:
            target = root / name
            if name not in file_set or not target.is_file():
                errors.append(f"MANIFEST: {manifest} — {entry} 파일이 없다")
                continue
            if sha256(target) != value:
                errors.append(f"MANIFEST: {manifest} — {entry} 해시 불일치")
                continue
            covered.add(name)

    # 6. Git에 둔 압축 파일은 같은 이름의 .sha256 sidecar와 바이트 해시가 일치해야 한다
    for name in files:
        if not ARCHIVE_NAME.search(name):
            continue
        sidecar = name + ".sha256"
        if sidecar not in file_set:
            errors.append(f"ARCHIVE: {name} — .sha256 sidecar가 없다")
            continue
        recorded = re.findall(r"\b[0-9a-f]{64}\b", (root / sidecar).read_text(encoding="utf-8", errors="replace"))
        if sha256(root / name) not in recorded:
            errors.append(f"ARCHIVE: {name} — sidecar 해시와 바이트가 다르다")

    # 7. Git에 둔 압축 파일은 1MB 이하이고, 내부 파일 목록이 ARCHIVE_INDEX에 있으며
    #    그 목록이 압축 파일 바이트에서 다시 계산한 값과 같아야 한다(리뷰에서 내용이 보이도록).
    archives = [name for name in files if ARCHIVE_NAME.search(name)]
    index_path = root / ARCHIVE_INDEX
    index = json.loads(index_path.read_text(encoding="utf-8")).get("archives", {}) if index_path.is_file() else {}
    for name in archives:
        target = root / name
        size = target.stat().st_size
        if size > ARCHIVE_MAX_BYTES:
            errors.append(f"ARCHIVE: {name} — {size} bytes, Git 보관 한도 {ARCHIVE_MAX_BYTES} bytes 초과(별도 보관소 사용)")
        record = index.get(name)
        if record is None:
            errors.append(f"ARCHIVE: {name} — {ARCHIVE_INDEX}에 내부 파일 목록이 없다")
            continue
        if record.get("sha256") != sha256(target):
            errors.append(f"ARCHIVE: {name} — {ARCHIVE_INDEX}의 sha256이 파일과 다르다")
        try:
            actual = archive_entries(target)
        except Exception as exc:  # 형식 미지원·손상
            errors.append(f"ARCHIVE: {name} — 내부 목록을 계산할 수 없다({type(exc).__name__})")
            continue
        if record.get("entries") != actual:
            errors.append(f"ARCHIVE: {name} — {ARCHIVE_INDEX}의 내부 목록이 실제 내용과 다르다")
    for name in index:
        if name not in file_set:
            errors.append(f"ARCHIVE: {ARCHIVE_INDEX}에 있는 {name}가 추적 파일이 아니다")

    # 8. 모든 추적 파일은 대장 또는 대장에 연결된 Manifest로 확인된다
    for name in files:
        if name != REGISTRY and name not in covered:
            errors.append(f"COVERAGE: {name} — 대장에도, 대장에 등록된 Manifest에도 없다")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="저장소 루트")
    parser.add_argument("--base", help="새로 추가된 파일을 가릴 기준 ref (예: origin/main)")
    parser.add_argument("--archive-index-draft", action="store_true",
                        help=f"{ARCHIVE_INDEX} 초안을 표준 출력으로 낸다(파일은 쓰지 않는다)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = tracked_files(root)
    if args.archive_index_draft:
        draft = {"version": 1, "max_bytes": ARCHIVE_MAX_BYTES, "archives": {}}
        for name in files:
            if ARCHIVE_NAME.search(name):
                target = root / name
                draft["archives"][name] = {"sha256": sha256(target), "size": target.stat().st_size,
                                           "entries": archive_entries(target)}
        print(json.dumps(draft, ensure_ascii=False, indent=2))
        return 0
    changes = changed_files(root, args.base) if args.base else None
    new_files = [name for status, name in changes if status == "A"] if changes is not None else None
    before = base_files(root, args.base) if args.base else None
    warnings: list[str] = []
    errors = check(root, files, new_files, changes, before, warnings)
    for line in errors + warnings:
        print(line)
    scope = f", 기준 {args.base}" if args.base else ", 기준 ref 없음(FROZEN·SEALED 점검 생략)"
    status = "FAIL" if errors else "PASS"
    print(f"evidence-layout: {status} — 추적 파일 {len(files)}개, 오류 {len(errors)}건, 경고 {len(warnings)}건{scope}")
    print("이 결과는 경로·목록·현재 바이트 점검이며 원본 진위, 시험 PASS, 인수 승인을 뜻하지 않는다.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
