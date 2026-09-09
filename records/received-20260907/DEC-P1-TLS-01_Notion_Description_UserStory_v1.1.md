# DEC-P1-TLS-01 — Harbor / Edge TLS Trust Decision

# 🎯 User Story

보안·인프라 담당자로서 Harbor 이미지 Push/Pull과 `edge01` 서비스 접근에 사용할 TLS 신뢰 체계를 확정한다. 이를 통해 Runner·Worker·관리 Client가 인증서 검증 우회 없이 승인된 서버와 암호화 통신하고, Harbor Robot Account 인증을 신뢰된 TLS 연결 위에서 수행하도록 한다.

---

# 📍 최종 결정안

P1 TLS 신뢰 방식은 **프로젝트 전용 Private Root CA + Harbor/edge01 서비스별 Leaf 인증서 + Consumer별 CA Trust 배포**로 고정한다.

| 구성요소 | Endpoint | 인증서 | Consumer |
|---|---|---|---|
| Harbor | `10.1.93.54:443` | Harbor 전용 Server Leaf | Self-hosted Runner, Kubernetes Worker, 승인된 관리자 Client |
| edge01 | `10.1.93.50:443` | edge01 전용 Server Leaf | 승인된 외부·관리 Client |
| Project Private Root CA | 서비스 Endpoint 없음 | Leaf 인증서 서명 및 Trust Anchor | 승인된 Consumer Trust Store |

- Harbor와 `edge01`은 인증서와 Private Key를 공유하지 않는다.
- Consumer에는 CA 공개 인증서만 배포한다.
- Root CA Private Key와 Server Leaf Private Key는 Consumer에 배포하지 않는다.
- 본 결정은 Server Authentication TLS를 기준으로 하며 Client Certificate 기반 mTLS는 적용하지 않는다.

---

# 📌 Scope

## In Scope

- 프로젝트 전용 Private CA와 서비스별 Leaf 인증서 구조
- Harbor와 `edge01` 인증서 용도 분리
- DNS SAN 및 IP SAN 기준
- TLS 최소 버전과 인증서 검증 우회 금지
- Runner·Worker·관리 Client의 CA Trust 배포
- Private Key 보관·권한·백업·폐기 원칙
- 인증서 만료 감시·갱신·Rollback
- Positive·Negative Test 및 Evidence 기준
- D-SEC-01 Harbor Robot Account 원칙과의 책임 경계 및 실행 순서
- P2 전환 시 공통 Certificate Contract와 플랫폼별 적용 방식 분리

## Out of Scope

- Public CA 구매 또는 외부 인증기관 계약
- HSM/KMS 또는 전용 온라인 CA 서버 구축
- Client Certificate 기반 mTLS
- Harbor 내부 Component 간 mTLS
- OCSP/CRL 서비스 구축
- ACME 기반 완전 자동 갱신
- Harbor Robot Account Secret 값 결정 및 실제 발급
- P2 ROSA Route/Ingress 인증서 실제 구축
- 명시되지 않은 P1/P2 기능과 Scope Out 기능

Scope Out은 P1 교육·개발·PoC 범위에 한정한다. 실제 금융 Production에서는 조직 PKI, HSM/KMS, 키관리 이중통제, 폐기 및 감사통제를 별도로 설계해야 한다.

---

# 🔎 Decision 비교표

| 후보 | 장점 | 제약 및 판단 | 검토 결과 |
|---|---|---|---|
| Public CA | 일반 Client의 별도 Trust 배포 부담이 작음 | 사설 IP와 내부 이름에 직접 적용하기 어렵고 외부 도메인·검증 체계가 필요 | P1 제외 |
| 서비스별 Self-signed Leaf | 발급 절차가 단순 | 인증서 교체 시 Consumer별 Trust 재배포가 필요하고 Trust가 서비스별로 분산 | 제외 |
| Private CA + 서비스별 Leaf | Root Trust 1회 배포, 서비스별 키 격리, 갱신·Rollback 용이 | Root CA Key 보호와 Consumer Trust 배포 필요 | **채택** |
| cert-manager/Vault/ACME | 자동 발급·갱신과 확장성 | P1에서 추가 플랫폼과 운영 복잡도 발생 | P2 재검토 |
| HTTP/insecure/skip-verify | 초기 연결이 단순 | 서버 신원 검증과 공급망 보호 무력화 | 금지 |

---

# 📋 핵심 요구사항

- [x] Harbor `.54:443`과 `edge01 .50:443`에 별도 Leaf 인증서와 Private Key를 사용한다.
- [x] 프로젝트 전용 Private Root CA가 두 Server Leaf 인증서를 서명한다.
- [x] P1-DNS-01에서 확정된 FQDN을 DNS SAN으로 기록한다.
- [x] IP Endpoint를 실제 사용하는 동안 Harbor `.54`와 `edge01 .50`을 각각 IP SAN으로 기록한다.
- [x] CN이 아닌 `subjectAltName`의 DNS-ID/IP-ID로 서비스 신원을 검증한다.
- [x] TLS 1.2 이상만 허용하고 양측이 지원하면 TLS 1.3을 사용한다.
- [x] `insecure-registry`, `skip_verify`, `curl -k` 등 인증서 검증 우회를 정상 구성과 Evidence에서 금지한다.
- [x] Root CA와 Leaf Private Key를 Git, Manifest, Notion, 로그 및 Evidence에 저장하지 않는다.
- [x] CA 공개 인증서 Trust 배포를 Ansible 또는 승인 Runbook으로 재현한다.
- [x] 인증서 갱신·만료·Rollback 절차와 Owner를 명시한다.
- [x] TLS 오류와 Robot Account 인증·권한 오류를 구분해 검증한다.

---

# 🧾 Certificate 및 Trust 기준

## Certificate Matrix

| 구분 | Endpoint | DNS SAN | IP SAN | Key Owner | Consumer |
|---|---|---|---|---|---|
| Harbor Leaf | `10.1.93.54:443` | P1-DNS-01 확정 FQDN | `10.1.93.54` — IP Endpoint 사용 기간 | P1-HBR-01 구현 Owner | Runner, Worker, 승인된 관리자 Client |
| Edge Leaf | `10.1.93.50:443` | P1-DNS-01 확정 FQDN | `10.1.93.50` — IP Endpoint 사용 기간 | edge01 구현 Owner | 승인된 외부·관리 Client |
| Project Root CA | 서비스 Endpoint 없음 | 해당 없음 | 해당 없음 | DEC-P1-TLS-01 Lead | 승인된 Trust Store |

확정되지 않은 FQDN을 임의로 생성하지 않는다. P1-DNS-01 결과를 Certificate Matrix에 반영한 후 Leaf 인증서를 발급한다.

## 발급 기준

- P1 호환성 기준으로 RSA 3072-bit와 SHA-256 이상을 사용한다.
- Server Leaf에는 `serverAuth` Extended Key Usage를 적용한다.
- Harbor와 `edge01` 간 Private Key 재사용을 금지한다.
- Root CA 유효기간은 3년, Leaf 유효기간은 180일을 P1 기준값으로 사용한다.
- Leaf 갱신은 만료 30일 전 착수한다.
- 유효기간은 P1 교육·PoC 기준이며 실제 금융 Production의 법정·조직 기준을 의미하지 않는다.

## 보관 기준

- Root CA Private Key는 Harbor, `edge01`, Kubernetes Cluster 및 Consumer에 저장하지 않는다.
- Root CA Private Key는 암호화된 승인 저장매체 또는 보호된 관리자 저장소에 보관한다.
- Harbor Leaf Key는 `harbor01`, Edge Leaf Key는 `edge01`의 승인 경로에 최소 권한으로 저장한다.
- Private Key 파일은 서비스 실행계정과 승인 관리자 외 읽기를 차단한다.
- Backup에는 암호화, 접근권한, Owner 및 복구 Test 기준을 적용한다.
- Evidence에는 Subject, SAN, Issuer, SHA-256 Fingerprint 및 유효기간만 기록하고 Private Key와 Secret을 포함하지 않는다.
- CA 공개 인증서는 Secret이 아니므로 승인된 Source에서 버전 관리할 수 있으나 Fingerprint로 무결성을 확인한다.

## Consumer별 Trust 배포

| Consumer | Trust 적용 | 구현 책임 | 검증 기준 |
|---|---|---|---|
| Self-hosted Runner | OS Trust 및 사용 중인 Docker/BuildKit Registry Trust | P1-CICD-01 | 인증서 우회 없이 Harbor Login/Push 성공 |
| Kubernetes Worker | OS Trust 및 실제 설치된 containerd의 Registry Trust | P1-HBR-01 / P1-K8S-01 | Pod Image Pull 성공, `skip_verify` 미사용 |
| Linux 관리자 Client | OS System Trust | 승인 Runbook | Harbor/edge HTTPS 검증 성공 |
| Windows 관리자 Client | Local Computer의 승인된 Root Trust Store | 승인 Runbook | Browser/Client HTTPS 검증 성공 |
| harbor01 | Harbor Leaf/Key 및 Chain | P1-HBR-01 | Portal/API/Registry HTTPS 성공 |
| edge01 | Edge Leaf/Key 및 Chain | DEC-P1-ENTRY-01 후속 구현 | HAProxy 문법 검증 및 HTTPS 성공 |

Runtime별 Trust 경로는 실제 설치 버전과 설정을 확인한 후 적용한다. 특정 containerd 또는 Docker 설정 경로를 버전 확인 없이 고정하지 않는다.

---

# 🔐 D-SEC-01 및 Harbor Robot Account 연계

`DEC-P1-TLS-01`과 `D-SEC-01` 6번은 서로 다른 보안 계층을 담당하며 내용상 중복되지 않는다.

| 구분 | 책임 |
|---|---|
| DEC-P1-TLS-01 | Harbor 서버 인증, 전송구간 암호화, 인증서 SAN 및 CA Trust 배포 |
| D-SEC-01 6번 | Harbor Robot Account 신원, 최소 권한, Secret 보관·마스킹·회전·폐기 |
| P1-HBR-01 | TLS 인증서와 Robot Account를 Harbor·Runner·Worker에 적용하고 통합 검증 |

## Robot Account 고정 기준

- Worker용 Robot Account는 프로젝트 범위의 `Pull Repository` 권한만 부여한다.
- CI/CD용 Robot Account는 Harbor 제품 제약에 따라 `Push Repository + Pull Repository` 권한을 부여한다.
- Harbor는 Push 권한을 Pull 권한 없이 단독 부여할 수 없으므로 CI/CD 계정을 “Push only”로 표현하지 않는다.
- Worker용 계정과 CI/CD용 계정은 분리하고 Secret을 공유하지 않는다.
- Delete, Project 관리 및 기타 불필요 권한을 부여하지 않는다.
- Robot Account Secret은 본 TLS 티켓의 Certificate/Private Key와 별도 수명주기로 관리한다.

## 실행 순서와 Gate

Robot Account의 권한 설계, 이름·Owner·만료주기 결정 및 계정 발급은 TLS 구성과 병행할 수 있다. 다만 실제 자격증명 사용과 통합 Evidence에는 다음 Gate를 적용한다.

1. Harbor Leaf 인증서와 Chain을 설치한다.
2. Runner·Worker·관리 Client에 승인된 CA Trust를 배포한다.
3. 인증서 Chain, SAN, 유효기간 및 미신뢰 CA 차단을 검증한다.
4. 신뢰된 TLS 연결에서 Robot Account 로그인과 Push/Pull을 검증한다.
5. TLS 오류와 잘못된·만료된 Robot Account Secret 오류를 구분해 Evidence를 남긴다.

이는 `DEC-P1-TLS-01`이 Robot Account 설계·발급 전체를 차단한다는 의미가 아니다. Harbor 로그인·Push/Pull Runtime Test와 완료 Evidence에 대한 실행 Gate다. `edge01` TLS는 Harbor Robot Account와 직접적인 의존관계가 없다.

---

# ♻️ 갱신 및 Rollback

## 갱신 순서

1. 신규 Leaf 또는 신규 CA/Leaf Chain을 별도 승인 경로에 준비한다.
2. SAN, Chain, Fingerprint 및 유효기간을 검증한다.
3. CA가 변경되면 구·신 CA를 함께 신뢰하도록 Consumer Trust를 먼저 배포한다.
4. Harbor 또는 HAProxy에 신규 Leaf/Key를 반영한다.
5. 설정 문법 검증 후 Reload 또는 승인된 재기동을 수행한다.
6. Runner Push, Worker Pull 및 Client HTTPS를 재검증한다.
7. 승인된 중첩기간과 Rollback 가능기간 이후 구 CA/Leaf를 폐기한다.

## Rollback 순서

1. 직전 승인 Leaf/Key/Chain과 설정을 복원한다.
2. Harbor 또는 HAProxy 설정을 검증하고 Reload한다.
3. 구 CA Trust가 Consumer에서 제거되지 않았는지 확인한다.
4. Runner Push, Worker Pull 및 Client HTTPS를 재검증한다.
5. 실패 원인과 복구 결과를 Evidence에 기록한다.

Rollback 과정에서도 `insecure-registry`, `skip_verify` 또는 인증서 검증 우회를 사용하지 않는다.

---

# 🚚 P2 이식성

Certificate/Trust Contract와 플랫폼별 적용 방식을 분리한다.

| 구분 | P1 | P2 ROSA |
|---|---|---|
| 서비스 신원 | FQDN/IP SAN | Route/Ingress FQDN SAN |
| Edge 인증서 | edge01 HAProxy Leaf | ROSA/OpenShift Route/Ingress 인증서 |
| Registry Trust | On-Prem Harbor Private CA | Harbor 유지 시 ROSA 추가 Trust 연계 |
| Trust 배포 | Ansible/승인 Runbook | OpenShift/ROSA 지원 Trust 방식 |
| Private Key | P1 Host별 최소 권한 보관 | P2 Platform Secret 또는 Managed Certificate 기준 |

P2에서는 P1 Root CA Private Key를 Cluster로 이관하지 않는다. 온프레미스 Harbor를 계속 사용할 경우 CA 공개 인증서 Trust만 P2 플랫폼의 지원 방식으로 연결한다.

---

# 🏦 적용 수준

본 구성은 현재 보유 자원 내에서 금융권 주요 TLS 통제를 재현하는 교육·개발·PoC 환경에 적용한다.

> 금융권 주요 보안통제를 제한된 자원에서 재현한 Mini FDS 교육·PoC 플랫폼

Private CA, 서비스별 Leaf/Key 분리, SAN 검증, TLS 1.2 이상, Trust 배포 자동화, 갱신·Rollback 및 Negative Test를 적용한다. 다만 HSM/KMS, 조직 PKI/CPS, 키관리 이중통제, OCSP/CRL, 불변 감사로그 및 정식 인증서 운영조직이 없으므로 실제 금융 Production 또는 규제 준수 완료 환경으로 간주하지 않는다.

---

# ✅ Acceptance Criteria

- [x] Private CA와 Harbor/edge01 별도 Leaf 구조가 승인된다.
- [x] 인증서 알고리즘·Owner·유효기간·배포경로가 확정된다.
- [x] 확정 FQDN과 실제 사용 IP가 Certificate Matrix의 SAN과 일치한다.
- [x] Runner·Worker·관리 Client의 CA Trust 배포방법이 정의된다.
- [x] TLS 1.2 이상과 인증서 검증 우회 금지 기준이 승인된다.
- [x] Root/Leaf Private Key 보관·백업·폐기·Evidence 마스킹 기준이 승인된다.
- [x] 실패·만료·SAN 불일치·Trust 제거·Rollback Test가 정의된다.
- [x] D-SEC-01 Robot Account 원칙과 TLS 책임 경계가 기록된다.
- [x] Worker Pull 계정과 CI/CD Push+Pull 계정 분리 기준이 기록된다.
- [x] Robot Account 설계 병행과 Runtime Test 실행 Gate가 구분된다.
- [x] P1-HBR-01/P1-CICD-01의 Endpoint 및 Trust 경로와 일치한다.
- [x] P2 Certificate/Trust Adapter 전환 원칙이 기록된다.

---

# 🧪 검증 및 증적

| TC | 대상 | 조건 | 예상 결과 |
|---|---|---|---|
| TLS-01 | Runner → Harbor | 정상 CA, Chain 및 SAN | 인증서 우회 없이 HTTPS 연결 성공 |
| TLS-02 | Runner → Harbor | 정상 TLS + 유효한 CI/CD 계정 | Login 및 Push 성공 |
| TLS-03 | Worker → Harbor | 정상 TLS + 유효한 Worker 계정 | Image Pull 성공 |
| TLS-04 | Runner/Worker → Harbor | 미신뢰 CA | 인증 단계 전에 TLS 연결 실패 |
| TLS-05 | Runner → Harbor | 정상 TLS + 잘못되거나 만료된 Secret | TLS 연결 후 인증 실패 |
| TLS-06 | Worker 계정 → Harbor | Push 시도 | 권한 부족으로 Push 실패 |
| TLS-07 | CI/CD 계정 → Harbor | Delete 시도 | 권한 부족으로 Delete 실패 |
| TLS-08 | Client → edge01 | 정상 CA 및 SAN | HTTPS 응답 성공 |
| TLS-09 | Harbor/edge01 | SAN 불일치 | 인증서 검증 실패 |
| TLS-10 | Harbor/edge01 | 만료 인증서 또는 만료 시점 검증 | 연결 실패 또는 사전 만료 탐지 |
| TLS-11 | Harbor/edge01 | TLS 1.0/1.1 시도 | TLS 협상 실패 |
| TLS-12 | Harbor/edge01 | 직전 승인 인증서 Rollback | 서비스와 Trust 검증 복구 |

필수 Evidence:

- Certificate Decision Record
- Certificate/SAN/Trust Matrix
- CA 및 Leaf Fingerprint·유효기간 기록
- Consumer별 CA Trust 배포 결과
- TLS Positive·Negative Test 결과
- Robot Account 인증·권한 Positive·Negative Test 결과
- TLS 오류와 인증 오류가 구분된 통합 Test 결과
- Rollback Runbook 및 Test 결과
- Evidence Path: `docs/evidence/DEC-P1-TLS-01/`

Evidence에는 Private Key, Robot Account Secret, Token 및 인증정보 원문을 포함하지 않는다.

---

# 🔗 Dependency

- **Blocked By:** D-NET-01 — DONE
- **Blocks / Next:** P1-HBR-01의 Harbor HTTPS 활성화·CA Trust 배포·Secure Push/Pull 통합 검증; P1-CICD-01의 Secure Registry 통합 검증
- **Related Ticket:** D-SEC-01 6번, P1-DNS-01, P1-SEC-01, DEC-P1-ENTRY-01
- **Milestone:** G1 Infrastructure Ready

## 의존성 해석

- P1-DNS-01은 Leaf 발급에 사용할 확정 FQDN을 제공한다.
- Robot Account 권한 설계와 발급은 DEC-P1-TLS-01과 병행할 수 있다.
- 실제 로그인·Push/Pull Runtime Test와 완료 Evidence는 Harbor 인증서 설치 및 Consumer CA Trust 배포 완료 후 수행한다.
- `edge01` TLS 적용은 Harbor Robot Account와 독립적으로 진행한다.
- TLS 적용 실패 시 HTTP 또는 insecure 방식으로 우회하지 않는다.

---

# ⚖️ Decision / Risk Control

- **Related Decision IDs:** D19
- **Decision Control:** D19 설계 승인은 PASS다. 인증서 설치·CA Trust 배포와 Positive/Negative Runtime Evidence가 완료되기 전에는 Production-like TLS 구현 완료를 주장하지 않는다.
- **Related Risk IDs:** RISK-06; RISK-08
- **Preventive Control:** Private CA, 서비스별 Leaf/Key 분리, SAN 검증, TLS 1.2 이상, 인증서 검증 우회 금지, Robot Account 분리
- **Detective Control:** 만료 점검, Fingerprint/SAN 확인, TLS 및 인증·권한 Positive/Negative Test, 오류 로그 분류
- **Recovery Control:** 구·신 CA 중첩 Trust, 직전 인증서/설정 복원 및 Consumer 재검증

RISK-06은 Harbor/Edge TLS 신뢰 실패의 직접 Risk다. RISK-08은 GitHub/Runner 외부 의존성 Risk이므로 Test에서 TLS, DNS·Route, GitHub 연결 및 Robot Account 인증 오류를 구분한다.

---

# 📝 Completion Record

- **Result:** PASS — Private CA + 서비스별 Leaf + Consumer별 CA Trust 및 D-SEC-01 연계 기준 승인
- **Status:** Done
- **Exit Criteria:** Harbor와 edge01의 인증서 발급·SAN·CA Trust 배포·갱신·Rollback 방식을 확정하고 Consumer별 검증방법 승인
- **Approval Result:** PASS
- **Approval Date:** 2026-08-31
- **Completed Date:** 2026-08-31
- **Reviewer / Approver:** 이하영 / 이하영
- **Evidence Path:** `docs/evidence/DEC-P1-TLS-01/`

---

# 📚 참고 기준

- [Harbor 2.15 — Configure HTTPS Access](https://goharbor.io/docs/2.15.0/install-config/configure-https/)
- [Harbor 2.15 — Create Project Robot Accounts](https://goharbor.io/docs/2.15.0/working-with-projects/project-configuration/create-robot-accounts/)
- [RHEL 10 — Using Shared System Certificates](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/securing_networks/using-shared-system-certificates)
- [containerd — Registry Host Configuration](https://github.com/containerd/containerd/blob/main/docs/hosts.md)
- [RFC 9525 — Service Identity in TLS](https://datatracker.ietf.org/doc/html/rfc9525)
