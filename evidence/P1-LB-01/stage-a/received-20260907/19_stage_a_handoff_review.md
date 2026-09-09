# P1-LB-01 Stage A Handoff Review

Version: v1.3 · 개정일: 2026-09-07 · 문서 상태: READY FOR RECEIVER REVIEW

## Record

| Field | Value |
|---|---|
| 인계 / 인수 | P1-LB-01 → P1-K8S-01 |
| Lead / Support Receiver | 이권욱 / 이하영 |
| 검토 작성 주체 | Codex — 첨부 원본 및 사용자 콘솔 보완 출력 검토; 담당자 승인 대체 아님 |
| 근거 정본 | v3.1.16 상태 기록, Stage A Guide v1.5, Secure Transfer Control v1.0 |
| 수신 묶음 | P1-LB-01_Stage_A_Review_Input_v1.1.tar.gz |
| 수신 묶음 SHA-256 | `62c64dfbd0cc672c96e4b1fbfa0c71a406e0c86d991b663c0ee02a47b82236a3` |
| 원본 반출 시각 | 2026-09-07 11:37:47 KST — Export Status 기록 |
| 기술 원본 작성 시점 | 2026-09-03 실행 기록, 일부 설정·Journal은 2026-08-31 이력 포함 |
| 정본 논리 경로 | docs/evidence/P1-LB-01/stage-a/ |
| Git Commit / 실제 인수 일시 | 검토 대상 Git Commit은 PR 본문에 고정 기록 / 실제 인수 일시 Pending |

## Integrity

- 수신 ZIP이 아닌 **tar.gz**의 SHA-256과 Sidecar가 일치한다.
- 내부 PACKAGE_SHA256SUMS 22개 항목(기술 원본 21개 + Export Status) 전부 일치한다.
- Export Status의 원본 Hash·파일 크기 21/21개가 수신 파일과 일치한다.
- Evidence 16/17/18의 SHA-256은 기존 Secure Transfer Control에 기록된 비교값과 3/3 일치한다.
- Evidence 18a에 기록된 16/17/18/18b/18c의 Hash는 수신 파일과 5/5 일치한다.
- 원본 묶음에는 19번 인수 기록과 99번 Manifest가 없다. 이 문서는 수신 후 새로 작성한 검토 기록이며 실제 인수 승인은 Pending이다.
- 99_SHA256SUMS.txt는 현재 검토 기록·원본·수신 메타데이터·콘솔 보완 정리본을 대상으로 생성한 신규 Manifest다. 실제 목록은 Manifest를 따른다. 9월 3일의 미제출 Manifest를 복원하거나 소급 검증한 것이 아니다.
- 2026-09-07 보완 3건은 사용자 콘솔 제출본으로 수용했다. 서버 보완 .txt/.sha256 파일 자체의 Hash 검증을 수행했다고 표시하지 않는다. 출처와 시각은 supplements/20260907_console_supplement_review.md에 기록했다.
- 수신 파일의 확인한 자격증명 패턴에서 Private Key/PAT/AWS Access Key 원문은 발견되지 않았다. 공개키 Fingerprint는 증적에 보존한다.

## Stage A checks

| 항목 | 원본 근거 | 이번 검토 |
|---|---|---|
| Host / OS | 01: k8s-api-lb01, CentOS Stream 10 | 일치 |
| IP / Route | 02~04: .109/24, Default .254, 10.250.10.0/24 via .58 | PASS |
| DNS 설정 | 04: .52,.53, fds.internal, ignore-auto-dns=예 | 설정 일치; DNS 재시험 아님 |
| HAProxy 구문 | 06: exit_code=0, 2026-09-03T12:00:38+09:00 | PASS |
| TCP / TLS pass-through | 07: mode tcp, bind .109:6443, LB 인증서 종료 없음 | PASS |
| HAProxy 서비스 | 08: enabled, active (running) | 수집 시점 PASS |
| Listener / Cockpit | 09: HAProxy .109:6443, :9090 Listener 없음 | 수집 시점 PASS |
| CP Backend 정의 | 07: .102/.103/.104:6443, check 설정 | PASS |
| Allowlist | 10: Node 6대 + Runner .20 + monitor01 .30의 /32 규칙, zone-wide ports 비어 있음 | 수집 Runtime 규칙 PASS |
| SELinux Boolean | 11: haproxy_connect_any → on | PASS |
| SELinux Enforcing | 2026-09-07 콘솔: getenforce=Enforcing, sestatus 현재/설정 enforcing | PASS — 조회 시점 |
| AVC | 12: <no matches> | 수집 범위 내 검색 결과 확인; Enforcing 증명 아님 |
| Bootstrap 전 Backend | 13/15: 3대 DOWN, Connection refused | Stage A의 당시 기대 결과와 일치; Stage B PASS 아님 |
| Node Positive | 16: .102/.103/.104/.105/.107/.108의 TCP handshake | 6/6 PASS |
| Runner Positive | 17: 10.250.10.20 → .109:6443 | PASS |
| 비승인 Source Negative | 18: 10.250.10.10 → .109:6443 TIMEOUT | 승인된 시험 기준상 PASS_BLOCKED |
| 전송 인증·Host Key | 18a~18c: Publickey-only, StrictHostKeyChecking, Host Fingerprint 일치 | PASS |
| Source별 키 구분 | 18b/18c 서로 다른 Fingerprint, 18a와 일치 | PASS |
| LB 임시 공개키 제거 | 18a: authorized_transfer_key_count_after_revoke=0 | PASS |
| LB Inbox 정리 | 18a: protected_inbox_file_count_after_cleanup=0 | PASS |
| Source 개인키 폐기 | 2026-09-07 콘솔: 두 Source 지정 개인키·공개키 ABSENT, 과거 PASS_REVOKED 및 Fingerprint 일치 | 2/2 PASS — 지정 경로 범위 |
| 인수 승인 | 실제 이하영 인수 기록 미포함 | Pending |

## 해석 및 검토 범위

1. 08/14의 2026-08-31 Journal에는 최초 Stats Socket 경로 오류와 No route to host가 남아 있다. 이후 기동 성공 및 09/13/15의 2026-09-03 결과를 함께 검토했으며, 과거 로그만으로 현재 수신 시점의 신규 장애라고 판정하지 않는다.
2. Stage A의 3대 Backend DOWN은 당시 Bootstrap 전 검증 범위다. Backend UP·인증 API·Failover는 P1-LB-01 Stage B에서 수행한다.
3. LB의 authorized_keys 제거와 Source의 개인키 파일 폐기는 서로 다른 항목이다. 전자의 0건 기록으로 후자를 PASS 처리하지 않는다.
4. 과거 Stage A 기술 PASS 기록은 유지한다. 요청한 보안 보완 3건은 2026-09-07 콘솔 제출본으로 PASS 판정했다. 서버 보완 파일의 원본 Hash 검증과 콘솔 검토는 구분한다.
5. LB-A-01 IP 중복검사 원본 및 Firewall Permanent 출력은 이 묶음에 포함되지 않았다. 수신 파일만으로 별도 재검증 PASS를 선언하지 않으며, 인수자는 기존 Stage A 승인 근거와 추적성을 확인한다. 기존 전체 테스트 재실행은 이번 보완 요청에 포함하지 않는다.
6. 원본 21개는 변경하지 않는다. 추가 확인은 새로운 시각의 Supplement로 보존하며 9월 3일 수행 결과로 소급 기록하지 않는다.

## 보완 검토 결과

| ID | 항목 | 근거 | 판정 |
|---|---|---|---|
| LB-HO-OBS-01 | SELinux 실제 모드 | 2026-09-07 12:02:59 KST: Enforcing, 현재/설정 enforcing, Boolean on | PASS |
| LB-HO-OBS-02 | Ansible 임시 개인키 폐기 | 2026-09-07 12:03:22 KST: 개인키/공개키 ABSENT; 09-03 18:29:11 폐기 기록과 Fingerprint 일치 | PASS |
| LB-HO-OBS-03 | Runner 임시 개인키 폐기 | 2026-09-07 12:03:14 KST: 개인키/공개키 ABSENT; 09-03 18:28:28 폐기 기록과 Fingerprint 일치 | PASS |

상세 원문 필드·서버 경로·시각·검증 한계는 `supplements/20260907_console_supplement_review.md`를 참조한다. 기존 수집과 보완 조회를 다시 실행할 필요는 없다.

## Decision

| Field | Value |
|---|---|
| Receipt / Transfer Integrity | PASS |
| Listener / Source Access Functional Review | PASS — 제출 원본 범위 |
| Requested Security Supplement Review | PASS 3/3 — 사용자 콘솔 제출본 근거 |
| Stage A Handoff | READY FOR RECEIVER REVIEW — 자료 작성 완료, 증적 편입 검토 및 실제 인수 승인 Pending |
| P1-LB-01 Status | In Progress |
| P1-K8S-01 Status | In Progress; 문서·읽기 전용 Preflight 가능 |
| kubeadm init/join | HOLD — Stage A 인계 및 OS/Node·Runtime Gate 확인 필요 |
| 이하영 Support / Receiver Approval | Pending; 본 초안은 승인 서명이 아님 |
| 이권욱 Final Approval | Pending |
| Stage B | Pending |

## GitHub 등록 상태

2026-09-07 사용자가 기준선과 증적의 별도 관리를 요청하여 목적지를 `321Team/fds-project-evidence` Private 저장소로 정리했다. 준비 브랜치는 `evidence/initial-import-20260907`이다. 사용자의 저장소 생성 및 GitHub App 접근 추가 완료 후 Private 설정과 쓰기 접근을 확인했다. 이 브랜치에서 최초 편입 검토를 진행하며, 실제 등록 Commit·검증 결과는 PR 본문에 고정 기록한다. 기존 baseline 업로드 시도의 자동 승인 거절과 전용 저장소 연결 대기는 해소된 과거 이력이다.

이 문서는 증적 인수 검토용이다. 저장소 준비와 자료 편입 요청은 이하영 인수 승인, 이권욱 최종 승인, main 병합 또는 Runtime Gate 해제를 대체하지 않는다. 기존 원본 21개와 Export Status는 바이트 그대로 보존했다.

## Release Note

| Version | Date | 변경 내용 |
|---|---|---|
| v1.0 | 2026-09-07 | 원본 21개 수신·무결성 검증, 기능 검토, 19번 인수 초안 작성, SELinux/Source 개인키 폐기 증적 누락과 Gate 경계 기록 |
| v1.1 | 2026-09-07 | SELinux 및 두 Source 임시 키 폐기 보완 3건 PASS, 콘솔 제출 출처 구분, 인수 검토 준비 상태로 갱신 |

| v1.2 | 2026-09-07 | baseline 원본 업로드 계획을 증적 전용 저장소 준비로 변경; 원격 등록·수신 승인 Pending 유지 |

| v1.3 | 2026-09-07 | 증적 전용 저장소 Private·쓰기 접근 확인 및 편입 검토 후보 등록; 실제 인수·최종 승인 Pending 유지 |
