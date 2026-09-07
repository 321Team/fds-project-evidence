# P1-ANS-01 SSH 관리 Key Lifecycle Record

> Record ID: `P1-ANS-01-SSH-KEY-01`
> 기준일: `2026-08-31`
> 대상 Ticket: `P1-ANS-01`
> 문서 상태: `APPROVED / HO-ANS-08 PASS`
> Evidence 배치 경로: `docs/evidence/P1-ANS-01/05h_ssh_key_lifecycle_record.md`

---

## 1. 목적과 적용 범위

이 문서는 `ansible01(10.250.10.10)`에서 Kubernetes 예정 Node 6대의 `svc_ansible` 계정으로 접속할 때 사용하는 전용 SSH 관리 Key의 발급, 보관, 사용 제한, 회전, 폐기 및 복구 절차를 정의한다.

- Controller: `ansible01` / `10.250.10.10`
- 대상: `k8s-control01~03`, `k8s-worker01~03`
- Remote Account: `svc_ansible`
- Key Type: `ED25519`
- 현재 Fingerprint: `SHA256:VPGV/RGA8TrwO/3FC4YPxGzRNhBWuB+9hCzPV5plkws`
- Private Key 경로: `/home/server01_ansible/.ssh/p1_ansible_ed25519`
- Public Key 경로: `/home/svc_ansible/.ssh/authorized_keys`
- 허용 Source: `10.250.10.10`만 허용

Private Key 본문, Passphrase 및 Public Key 원문은 이 문서와 Evidence에 기록하지 않는다.

---

## 2. 책임과 승인

| 역할 | 책임자 | 책임 |
|---|---|---|
| Operational Owner / Key Custodian | 이권욱 | 발급·보관·배포·회전·폐기 실행, Evidence 및 Inventory 정합성 유지 |
| Security / Operations Reviewer | 이하영 | 권한, Source 제한, 회전·폐기 절차 및 Evidence 검토 |
| Approver | 이하영 | 운영 인계 및 Lifecycle 통제 승인 |
| 대상 시스템 책임 Ticket | P1-ANS-01 | SSH 관리 경로와 Key Lifecycle 통제 |
| 후속 사용 Ticket | P1-K8S-01 및 승인된 운영 Ticket | 승인된 Ansible 자동화에 한해 사용 |

Reviewer와 Approver는 동일인이다. 겸임 사실을 승인 기록에 명시하며, 역할 지정만으로 검토 또는 승인 완료로 해석하지 않는다.

---

## 3. 현재 기술 통제

| 통제 | 현재 상태 | 근거 |
|---|---|---|
| Controller `.ssh` 권한 | `700` | `05g_ssh_key_lifecycle_validation.txt` |
| Controller Private Key 권한 | `600` | `05g_ssh_key_lifecycle_validation.txt` |
| Remote `.ssh` 권한 | `700` | `05g_ssh_key_lifecycle_validation.txt` |
| Remote `authorized_keys` 권한 | `600` | `05g_ssh_key_lifecycle_validation.txt` |
| Fingerprint 일치 | Controller와 6대 Node 동일 | `05g_ssh_key_lifecycle_validation.txt` |
| Public Key Source 제한 | `from="10.250.10.10",restrict` | `05g2~05g6` |
| SSH Host 검증 | `StrictHostKeyChecking=yes`, 전용 `known_hosts` | `05e`, `05f`, `05f2` |
| 비대화형 sudo / become | 6대 UID `0` | `05d_sudo_become_validation.txt`, `05g5b` |
| 신규 Session 검증 | 6대 로그인 및 sudo 성공 | `05g5_key_restriction_full_fresh_ssh.txt` |
| 멱등성 | 6대 `changed=0`, 실패 0 | `05g6_key_restriction_idempotency.txt` |

Private Key는 Source Repository, Ticket 본문, Evidence, 관리 대상 Node에 복사하지 않는다. Public Key만 제한 옵션과 함께 대상 Node에 배포한다.

---

## 4. 발급 절차

1. Operational Owner가 승인된 변경 창과 변경 기록을 생성한다.
2. `ansible01`에서 Ticket 전용 ED25519 Key Pair를 생성하고 용도를 식별할 수 있는 Comment를 부여한다.
3. `.ssh`는 mode `700`, Private Key는 mode `600`으로 제한한다.
4. Private Key에서 Public Key와 Fingerprint를 파생해 별도로 확인한다.
5. Public Key는 각 Node의 `svc_ansible` `authorized_keys`에 `from="10.250.10.10",restrict` 옵션과 함께 등록한다.
6. Private Key 또는 Passphrase는 채팅, Notion, Source, Evidence 및 관리 대상 Node에 기록하지 않는다.
7. 배포 후 6대 모두 신규 SSH Session, Ansible Ping 및 become을 검증한다.

Passphrase 적용 여부는 Private Key 자체를 노출하지 않는 별도 보안 확인으로 관리한다. 미적용 상태가 확인되면 암호화된 Secret 저장소 또는 승인된 비대화형 Credential Agent로 전환 계획을 별도 기록한다.

---

## 5. 보관 및 접근 통제

- 원본 Private Key는 `ansible01`의 위 전용 경로에만 보관한다.
- 운영 백업이 필요하면 조직이 승인한 암호화 Secret 저장소에만 보관하고, 접근자는 Operational Owner와 승인된 대체 담당자로 제한한다.
- 일반 파일 공유, 개인 PC, Source Repository, Evidence 디렉터리 및 관리 대상 Node에 Private Key를 복사하지 않는다.
- 접근권한 변경, Owner 변경 또는 Controller 재구축 시 즉시 Lifecycle 검토를 수행한다.
- `known_hosts`와 Client Private Key를 구분한다. Server Host Key 변경은 별도 검증 후 `known_hosts`를 갱신하며 Client Key 회전으로 대체하지 않는다.

---

## 6. 회전 기준과 절차

### 회전 기준

- 정기 회전: 발급일 또는 직전 회전일로부터 `90일` 이내
- 조기 회전: Phase 인계 또는 Operational Owner 변경 시
- 즉시 회전: 유출 의심, 권한 오설정, 무단 복제, Controller 침해, Fingerprint 불일치 또는 감사 실패 시
- 상위 보안정책이 더 짧은 주기를 요구하면 상위 정책을 우선한다.

현재 Key의 기술 검증 기준일은 `2026-08-28`이며, 조기 회전 사유가 없을 때의 최장 검토 기한은 `2026-11-26`이다.

### 회전 절차

1. 변경 기록에 기존·신규 Fingerprint, 대상 6대, 실행자와 승인자를 기록한다.
2. 새 ED25519 Key Pair를 별도 파일명으로 생성하고 권한과 Fingerprint를 확인한다.
3. 기존 Key를 유지한 상태에서 새 Public Key를 1대 Canary에 제한 옵션과 함께 추가한다.
4. ControlMaster를 사용하지 않는 신규 SSH Session으로 로그인, `sudo -n id -u`, Ansible Ping 및 become을 검증한다.
5. Canary 통과 후 나머지 5대에 새 Public Key를 배포하고 동일 검증을 수행한다.
6. Inventory 또는 `ansible.cfg`가 참조하는 Private Key를 새 Key로 전환한다.
7. 전체 Playbook Check와 승인된 Read-only 검증을 수행한다.
8. 6대 모두 새 Key로 정상 접속한 뒤 기존 Public Key를 `authorized_keys`에서 제거한다.
9. 기존 Private Key는 즉시 사용 중지하고 승인된 보안 저장소에 최대 7일 격리한 뒤 복구 필요가 없음을 확인하고 폐기한다.
10. 최종 Fingerprint, Fresh SSH, Ping, become, 멱등성 및 SHA-256 Evidence를 갱신한다.

기존 Key와 신규 Key의 병행 기간은 승인된 변경 창 안에서만 허용하며, 정상 검증 후 불필요하게 유지하지 않는다.

---

## 7. 폐기·긴급 차단 절차

1. 사고 또는 변경 기록을 개설하고 Operational Owner와 Reviewer에게 즉시 통보한다.
2. VMware Console 또는 승인된 대체 관리 경로를 확보한 뒤, 6대 `authorized_keys`에서 해당 Fingerprint의 Public Key를 제거한다.
3. `ansible01`의 해당 Private Key 사용을 중지하고 접근을 차단한다.
4. `sshd` Journal에서 해당 Key Fingerprint, Source IP, 로그인 시간 및 실행 계정을 조사한다.
5. 새 Key를 발급해 Canary → 전체 순서로 복구하고, 기존 Key 인증 실패를 확인한다.
6. Inventory, Runbook, Evidence와 Key Lifecycle Record를 갱신한다.

긴급 대응 중에도 `StrictHostKeyChecking`을 끄거나 임시 Password 인증을 상시 허용하지 않는다. 대체 접속이 필요하면 VMware Console 또는 사전 승인된 Break-glass 계정을 사용하고 사용 후 즉시 회수한다.

---

## 8. 복구 및 Rollback

- 새 Key 전환 실패 시 기존 Key가 아직 승인된 병행 기간 안에 있을 때만 기존 Key로 되돌린다.
- 기존 Key가 유출 의심 상태이면 Rollback에 사용하지 않고 Console 또는 Break-glass 경로로 새 Key를 재배포한다.
- 복구 시에도 6대 Fresh SSH, `sudo -n`, Ansible Ping, become과 Host Key 검증을 재수행한다.
- Rollback 사유, 시간, 실행자, 영향 범위와 후속 조치를 변경 기록에 남긴다.

---

## 9. Evidence 및 완료 조건

| Evidence | 판정 기준 |
|---|---|
| `05e_ssh_host_key_config.txt` | `HOST_KEY_CHECKING=True`, 환경 Override 없음 |
| `05f_known_hosts_inventory.txt` | 파일 권한, 6대 Host Key/Fingerprint, 파일 SHA-256 |
| `05f2_host_key_enforced_ping.txt` | Strict Host Key Checking 강제 상태 `SUCCESS=6` |
| `05g_ssh_key_lifecycle_validation.txt` | Controller/Remote 권한 및 Fingerprint 일치 |
| `05g2~05g6` | Source 제한, Fresh SSH, sudo, Ping/become, 멱등성 |
| `05h_ssh_key_lifecycle_record.md` | 책임자와 발급·보관·회전·폐기·복구 절차 |
| `05j_reviewer_approver_record.md` | 실제 검토 결과·일자와 승인 결과·일자 |
| `99_SHA256SUMS.txt` | 추가된 Evidence를 포함한 무결성 검증 성공 |

`HO-ANS-08`은 2026-08-31 Reviewer 이하영의 `PASS`와 Approver 이하영의 `APPROVED`로 종결한다. 본 승인본을 실제 Evidence 경로에 반영한 뒤 `99_SHA256SUMS.txt`를 재생성·검증하는 작업은 배포 후속 조치로 추적한다. `HO-ANS-09`의 승인 결과는 `05j_reviewer_approver_record.md`에 기록한다.

---

## 10. 확인 기록

| 항목 | 입력값 |
|---|---|
| Operational Owner | 이권욱 |
| Owner Confirmation | `CONFIRMED` |
| Owner Confirmation Date | `2026-08-31` |
| Security / Operations Reviewer | 이하영 |
| Review Result | `PASS` |
| Review Date | `2026-08-31` |
| Approver | 이하영 |
| Approval Result | `APPROVED` |
| Approval Date | `2026-08-31` |
| Dual Role | `YES` — Reviewer와 Approver 동일인 |
| Approval Comment / Reference | `HO-ANS-08 PASS. Operational Owner 이권욱, 90일/Event 기반 회전, 폐기·복구 통제를 승인함. 05j 승인 기록 참조.` |

본 문서는 2026-08-31 검토·승인을 완료했다. Private Key 본문과 Passphrase는 계속 Evidence에 포함하지 않으며, 실제 Repository 반영 시 `99_SHA256SUMS.txt`를 재생성·검증한다.
