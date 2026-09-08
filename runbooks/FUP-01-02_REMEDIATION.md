# FUP-01/02 우선 보완 절차

기준일: 2026-09-08  
범위: 기존 종결 티켓의 증적 수신·정합성 보완만 수행한다. 티켓 재구현, DNS 재변경, resolver rollback, 신규 Runtime 시험은 수행하지 않는다.

## 현재 판정

| ID | 현재 상태 | 이번 절차의 목적 |
|---|---|---|
| FUP-01 | 변경 노드 5대의 보존 파일 및 Refinalization 원본 미수신 | 원본 바이트·SHA-256·권한·보관 위치를 읽기 전용으로 수령 |
| FUP-02 | 05h/05j 승인본은 존재하나 구 매니페스트가 이전 해시를 유지 | 구 매니페스트 보존, 실제 승인본 해시 고정, 05j 파일명 alias 및 신규 수신회차 매니페스트 생성 |

## 안전 경계

- `ansible01`에서 `server01_ansible` 사용자로만 실행한다.
- `git pull`, Playbook apply, rollback, DNS 변경, SSH Key 변경을 수행하지 않는다.
- 원본 파일에 `chmod`, `chown`, rename, 내용 수정 또는 매니페스트 재쓰기를 수행하지 않는다.
- FUP-01 원격 노드에는 `ansible.builtin.stat`과 `ansible.builtin.slurp`만 사용한다.
- Private Key·Token·Password가 탐지되면 해당 파일을 수집하지 않고 중단한다.
- 새 결과는 새 수신 디렉터리와 새 압축파일에만 기록한다.

## 1. 승인된 수집기 준비

```bash
cd /home/server01_ansible/p1-ans-01
git status --short
source ~/.config/ansible/p1-ans-01.env
python3 --version
ansible --version
```

작업 트리가 변경돼 있으면 정리하지 말고 중단한다. 기존 증적을 삭제하거나 덮어쓰지 않는다.

## 2. FUP-01 수집

Refinalization 원본의 기존 경로를 아는 경우에만 그 경로를 명시한다.

```bash
python3 tools/collect-fup-01-02-remediation.py \
  --ticket FUP-01 \
  --refinalization-original /기존/원본/경로
```

경로를 모르면 옵션을 빼고 실행할 수 있다. 이 경우 승인된 CR 증적 디렉터리 안에서 기대 SHA-256과 정확히 같은 기존 파일만 찾는다.

```bash
python3 tools/collect-fup-01-02-remediation.py --ticket FUP-01
```

수집기는 다음 5개 노드에서 `/var/lib/fds-change/CR-P1-ANS-01-01/original-resolver.json`을 읽는다.

- `k8s-control02`
- `k8s-control03`
- `k8s-worker01`
- `k8s-worker02`
- `k8s-worker03`

기대 조건은 `root:root`, mode `0600`, 변경 전후 stat 동일, 파일 내부 `change_id`·`inventory_hostname` 일치다. 수집기는 rollback을 실행하지 않는다.

## 3. FUP-02 재수집이 필요한 경우

2026-09-08 사용자 제출 `evidence.zip` 수신으로 FUP-02 정합성 보완 자료는 이미 생성됐다. 서버 원본을 다시 받아야 할 때만 아래를 실행한다.

```bash
python3 tools/collect-fup-01-02-remediation.py --ticket FUP-02
```

이 모드는 05h, 실제 수신명 05j, 구 `99_SHA256SUMS.txt`를 그대로 보존한다. 지정명 `05j_reviewer_approver_record.md`와 실제명 `05j_review_approval_record.md`는 rename이 아니라 alias 기록으로 연결한다.

## 4. 결과 검증·제출

수집기가 출력한 두 경로를 사용한다.

```bash
sha256sum --check \
  ~/FDS_FUP01_02_Receipt_*/FDS_FUP01_02_Remediation_Receipt_v1.0.tar.gz.sha256
tar -tzf \
  ~/FDS_FUP01_02_Receipt_*/FDS_FUP01_02_Remediation_Receipt_v1.0.tar.gz
```

압축파일과 `.sha256`을 함께 제출한다. `COLLECTION_REPORT.json`의 FUP-01 상태가 다음 중 어느 것인지 확인한다.

- `READY_FOR_IMPORT`: rollback 상태 5개와 Refinalization 원본을 모두 수령
- `ROLLBACK_COLLECTED_REFINALIZATION_PENDING`: rollback 상태는 수령했지만 Refinalization 원본은 계속 대기

## 완료 기준

- FUP-01: 5개 보존 파일의 바이트·해시·권한 검증과 기대 SHA-256이 일치하는 Refinalization 원본 수령
- FUP-02: 구 매니페스트 보존, 승인본 05h/05j 실제 해시 확인, 파일명 alias 고정, 신규 수신회차 매니페스트 검증
- 두 항목의 증적 편입 승인과 PR 병합은 별도 독립 검토 Gate로 유지
