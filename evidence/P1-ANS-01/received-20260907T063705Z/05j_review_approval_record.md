# P1-ANS-01 Reviewer / Approver Record

> 기준일: `2026-08-31`
> Ticket: `P1-ANS-01`
> 상태: `PASS / APPROVED / CLOSED`
> Evidence 배치 경로: `docs/evidence/P1-ANS-01/05j_reviewer_approver_record.md`

---

## 1. 역할 지정

| 항목 | 입력값 |
|---|---|
| Lead / Operational Owner | 이권욱 |
| Security / Operations Reviewer | 이하영 |
| Approver | 이하영 |
| Reviewer / Approver 겸임 | `YES` |
| Technical Completed Date | `2026-08-28` |
| Closed Date | `2026-08-31` |

동일인이 Reviewer와 Approver를 겸임한다. Review Result와 Approval Result는 서로 구분해 각각 명시하며, 역할 지정 또는 의견 작성만으로 승인 완료로 해석하지 않는다.

---

## 2. 접수된 검토 의견

### 이하영 — Security / Operations Review Comment

- VMware 복제 Node 6대의 MAC Address와 `product_uuid` 고유성을 `P1-K8S-01` Preflight에서 확인한다.
- SELinux `Enforcing` 상태의 Container Runtime·kubelet·Calico 호환성, cgroup driver 및 Kubernetes/Calico 필수 포트를 `P1-K8S-01`에서 검증한다.
- SSH 관리 Key의 책임자와 Lifecycle 문서를 확인한다.

Disposition:

- cgroup driver·SELinux Runtime/CNI·Node 고유성·Kubernetes/Calico Port는 `P1-K8S-01`, SecurityContext/PSA와 제한 NodePort Source는 `P1-SEC-01`, API LB 6443 경로는 `P1-LB-01`, Service/Probe 계약은 `P1-APP-01`로 분할 이관한다.
- SSH Key Lifecycle은 `05h_ssh_key_lifecycle_record.md`에 Operational Owner `이권욱`과 발급·보관·회전·폐기·복구 절차로 문서화한다.
- Review Comment와 Lifecycle Record를 검토해 `Review Result=PASS`, `Review Date=2026-08-31`로 확정했다.

### 이재환 — Support Review Comment

- `HO-ANS-02`는 SELinux `Enforcing` 상태의 Container Runtime·kubelet·Calico뿐 아니라 P1-SEC-01의 `SecurityContext`, PSA Restricted 등 보안 Manifest가 실제 클러스터에서 충돌 없이 동작하는지 `P1-K8S-01` 단계에서 재검증한다.

Disposition:

- 실제 Cluster 환경은 `P1-K8S-01`이 제공하고, SecurityContext·PSA Restricted의 허용·거부 판정은 `P1-SEC-01` Acceptance와 Evidence에 연결한다.
- 본 항목은 SSH 기술 통제의 실패 사유가 아니며 Kubernetes 후속 구축의 조건부 Gate다.

---

## 3. 검토·승인 입력란

### Security / Operations Review

| 항목 | 입력값 |
|---|---|
| Reviewer | 이하영 |
| Review Result | `PASS` |
| Review Date | `2026-08-31` |
| Review Comment | `HO-ANS-08 Lifecycle Owner·회전·폐기·복구 통제와 SSH 운영 Evidence를 검토했으며 종결 기준을 충족함.` |
| Reviewed Evidence | `05d`, `05e`, `05f`, `05f2`, `05g~05g6`, `05h`, `99_SHA256SUMS.txt` |

### Approval

| 항목 | 입력값 |
|---|---|
| Approver | 이하영 |
| Approval Result | `APPROVED` |
| Approval Date | `2026-08-31` |
| Approval Comment / Reference | `HO-ANS-08·09 PASS 및 P1-ANS-01 종결 승인. HO-ANS-01~04는 후속 Ticket Acceptance로 이관하며 완료로 간주하지 않음.` |
| Dual-role Acknowledgement | `YES` — Reviewer와 Approver 겸임 사실 확인 |

---

## 4. 상태 전환 기준

| 조건 | 상태 |
|---|---|
| SSH 기술 Evidence PASS | 충족 |
| `05h_ssh_key_lifecycle_record.md` 승인 | 충족 — PASS |
| Operational Owner 확인 | 충족 — 이권욱 / 2026-08-31 |
| Reviewer 결과·일자 명시 | 충족 — PASS / 2026-08-31 |
| Approver 결과·일자 명시 | 충족 — APPROVED / 2026-08-31 |
| 승인본 Repository 반영 및 SHA-256 재검증 | 배포 후속 조치 — 승인 상태와 분리 추적 |
| `HO-ANS-08` | `PASS` |
| `HO-ANS-09` | `PASS` |
| P1-ANS-01 | `Done` — Closed Date 2026-08-31 |

`HO-ANS-08/09=PASS`와 `P1-ANS-01=Done` 전환을 승인한다. 승인본 `05h`, `05j`를 실제 Evidence 경로에 배치하고 `99_SHA256SUMS.txt`를 재생성·검증하는 작업은 배포 체크리스트로 수행한다.
