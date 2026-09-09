# ansible01 원본 증적 수집 v1.0

CR-P1-ANS-01-01 병합 후 남은 원본 수신을 위한 절차다. 현재 서버의 증적을 읽어 새 반출 묶음을 만들며, 시험을 재실행하거나 승인 기록을 생성하지 않는다.

## 1. 수집 대상

| 티켓 | 확인된 원본 위치 |
|---|---|
| CR-P1-ANS-01-01 | `/home/server01_ansible/p1-ans-01/docs/evidence/CR-P1-ANS-01-01/` |
| P1-ANS-01 | `/home/server01_ansible/p1-ans-01/docs/evidence/P1-ANS-01/` |
| P1-DNS-01 | `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/P1-DNS-01-FRESH-20260902-R2.zip` 및 `.sha256` |

실행 시 계정 데이터베이스의 `server01_ansible` 홈을 사용한다. 위 티켓 경로가 없으면 해당 누락을 기록한다. 임의로 다른 디렉터리를 검색하거나 원본·Manifest를 생성하지 않는다.

## 2. 실행

[collect-ansible-evidence.py](../tools/collect-ansible-evidence.py)를 다운로드하여 `ansible01`의 `server01_ansible` 홈에 같은 파일명으로 둔다. [SCRIPT_SHA256SUMS](../tools/SCRIPT_SHA256SUMS)의 파일 Hash와 대조할 수 있다.

```bash
sudo python3 ~/collect-ansible-evidence.py
```

수집 계정은 `server01_ansible`, Host는 `ansible01`인지 확인한다. `sudo`는 읽기 제한이 있는 원본의 수집에 사용한다. 원본 파일의 권한·소유자는 변경하지 않는다. 새 출력 폴더만 실제 sudo 호출 사용자 소유의 `0700`, 출력 파일만 `0600`으로 설정한다. 직접 root 로그인 상태에서는 실행하지 않는다.

한 티켓만 우선 수집할 때:

```bash
sudo python3 ~/collect-ansible-evidence.py --ticket CR-P1-ANS-01-01
```

## 3. 가져올 파일

콘솔의 `ARCHIVE=`와 `SIDECAR=`에 출력되는 두 파일을 WinSCP에서 `server01_ansible` 계정으로 가져와 현재 검토 대화에 첨부한다. 임시 폴더명은 실행마다 달라진다.

- `FDS_Evidence_Receipt_v1.0.tar.gz`
- `FDS_Evidence_Receipt_v1.0.tar.gz.sha256`

같은 출력 폴더의 `COLLECTION_REPORT.json`은 묶음에도 포함된다. `cd`에 sudo를 붙일 필요가 없다. 원본 경로에 재귀 `chmod/chown`을 실행하지 않는다.

다운로드한 두 파일을 같은 디렉터리에 두고 Linux에서는 다음과 같이 전송 Hash를 확인할 수 있다.

```bash
sha256sum --check FDS_Evidence_Receipt_v1.0.tar.gz.sha256
```

## 4. 출력의 의미

| 출력 | 의미 |
|---|---|
| issues=0 | 파일 읽기·필터 issues 목록만 0건. missing_required·Manifest 불일치·Refinalization 미수신을 포함한 총 결함 수가 아님 |
| REVIEW EXPORT READY | 새 묶음의 내부 파일 바이트 재대조 완료. 모든 원본의 완비 또는 시험 PASS를 뜻하지 않음 |
| original_manifest.result=MATCH | 수집 바이트가 기존 Manifest의 모든 기재 항목과 일치 |
| unlisted_files | 기존 Manifest에 없는 수집 파일. 신규 수신 Hash와 기존 Manifest 검증 범위를 구분해 검토 |
| MISSING_NOT_VERIFIED / missing_required | 자료 또는 Manifest가 없어 원본 확인이 필요함 |
| MISMATCH | 기존 기록과 불일치. 원본을 덮어쓰거나 Manifest를 재생성하지 않고 원인 확인 |
| SECRET_PATTERN_REQUIRES_LOCAL_REVIEW | 해당 텍스트는 묶음에서 제외. 로컬에서 먼저 확인 |
| REVIEW_REQUIRED / NOT_ASSESSED | 수집 결과는 검토 입력이며 개별 시험 합격·인수 승인을 자동 판정하지 않음 |

CR의 알려진 Index·Manifest·최종 로그 Hash 및 Refinalization Record Hash를 별도로 대조한다. P1-ANS의 05h/05j 파일 존재는 실제 승인 내용의 검토를 대신하지 않는다. 모든 Primary Closure Evidence의 완비 여부는 해당 티켓의 종결 문서 목록과 수신 후 대조한다.

DNS R2 ZIP은 기록된 SHA-256과 일치하는 기존 바이트만 포함한다. ZIP을 풀거나 재압축하지 않는다. Sidecar가 없으면 누락으로 기록한다. 내부 Index·Manifest 검증은 수신 후 별도로 수행한다. ZIP 내부의 자격증명 검사는 이 스크립트에서 수행하지 않으며 수신 묶음은 저장소에 자동 Push되지 않는다.

텍스트 수집은 승인된 티켓 폴더의 명시된 텍스트 확장자로 제한한다. Private Key/PAT/AWS Key의 알려진 패턴을 검사하지만 모든 Secret의 완전 탐지를 보장하지 않는다. 프로젝트 전체, SSH 디렉터리와 환경 설정 파일은 수집 대상이 아니다.

## 5. 수신 후 순서

1. 바깥 tar.gz와 Sidecar를 대조하고 안전한 별도 경로에서 목록·경로·파일 유형을 검토한다.
2. 새 `COLLECTION_SHA256SUMS` 및 기존 CR/P1-ANS Manifest, DNS R2의 기록된 Hash·Sidecar·내부 Manifest를 구분해 검증한다.
3. 누락·불일치·미등재 파일과 05h/05j 내용을 기록한다. 수신 자료에 실제 자격증명이 있으면 원본을 보존하면서 별도 정제본을 검토한다.
4. 검증된 수신회차를 증적 PR에 추가하고 P1-LB Stage A 인수 및 OS/Node Gate에 연결한다.
5. 증적 편입에 대한 독립 검토·최종 승인·병합을 진행한다.

기존 P1-ANS/P1-DNS Done과 CR의 승인·병합 결과는 유지한다. 원본 수신이 끝나기 전에 현장 실행이나 Bootstrap 해제를 완료로 표시하지 않는다.

## 검증 범위

로컬 모의 파일로 11건을 검증했다: 원본 바이트·mode·mtime 보존, Manifest 정상/누락/불일치, 경로 이탈·symlink·FIFO 거부, Secret 패턴 제외, 기록 Hash 대조, DNS 바이트 보존/불일치 제외, 새 묶음 바이트·권한 검증, sudo 소유권 변경 요청 범위. 서로 다른 UID로의 소유권 변경 요청은 mock으로 검증했으며 실제 ansible01 실행은 대기다.

## 2026-09-07 수신 결과

[수신 검토 보고서](../receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md)를 확인한다. FUP-01/02의 보완 원본만 별도 회차로 제출하며 전체 수집 또는 DNS ZIP 재제출은 요구하지 않는다.
