# 중앙 bootstrap 인수 대조표 — 채택값 ↔ 소스 ↔ 실제 (2026-10-09)

출처 티켓: [infra-terraform#8](https://github.com/321Team/infra-terraform/issues/8) (P2-IAC-01 Sub-task 1/6, AC-4 State 부분)

## 0. 대조 기준

| 구분 | 출처 |
|---|---|
| 채택값 | [#35 Lead 결정 2026-10-06](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6015740112) |
| 소스 | baseline merge `40ac664b83485745ab86b5018b8e19c386484cc8` `phase2/permissions/20261007-central-bootstrap/bootstrap-stack.candidate.json` (승인 source `e1cac2d39174821c839f2df6068fab16211bf872`) |
| 10-07 기록 | [#35 verify 수신 2026-10-07 14:45 KST](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6031821748) — root CloudShell 사용자 실행 출력 수신(`PASS_USER_READBACK`) |
| 이번 재조회 | 2026-10-09 22:56:52–22:58:00 KST, `321team-hayeoung` 본인 CloudShell. 원문은 `cloudshell-readback.txt` |
| Terraform 코드 | infra-terraform main `81162467bb2f99a099cb7067fbc3f63e1c0dbed8` (backend 파일은 현재 main `cca0388`까지 변경 없음) |

판정: **일치** = 채택값·소스·이번 재조회가 모두 같음.

## 1. State bucket

| # | 항목 | 채택값 | 소스 | 이번 재조회 | 판정 |
|---|---|---|---|---|---|
| S1 | 계정·리전 | 774055931866 / ap-northeast-2 | stack 리전 ap-northeast-2 | StackId `arn:aws:cloudformation:ap-northeast-2:774055931866:stack/FDS-Central-Bootstrap-v1/79b25940-c211-11f1-ab33-0a7d3f30f8ff` | 일치 |
| S2 | bucket 이름 | `fds-tfstate-774055931866-ap-northeast-2` | 동일 | 동일, LocationConstraint ap-northeast-2 | 일치 |
| S3 | 암호화 | SSE-S3(AES256), 전용 KMS 없음 | `SSEAlgorithm: AES256` | AES256, KMS 키 0 | 일치 |
| S4 | Versioning | 사용 | `Enabled` | `Enabled` (MFADelete 미설정) | 일치 |
| S5 | Block Public Access | 사용 | 4항목 true | 4항목 true | 일치 |
| S6 | ACL 비활성 | 사용 | `BucketOwnerEnforced` | `BucketOwnerEnforced` | 일치 |
| S7 | TLS 강제 | 사용 | `DenyInsecureTransport` | 정책 문장 1개 + http 실요청 AccessDenied (RC 254) | 일치 |
| S8 | state 원문 접근 제한 | state/lock 원문·버전 읽기·변경은 `FDS-IaC-Operator` + 중앙 bootstrap/복구 주체만 | `DenyStatePayloadAndMutationOutsideApprovedPrincipals`: 객체 8개(state 4 + `.tflock` 4), 허용 `role/FDS-IaC-Operator`, `root` | 동일(객체 8, 허용 주체 2). 음성 시험 §4 PASS | 일치 |
| S9 | 다른 암호화 방식 차단 | (SSE-S3만) | `DenyExplicitNonAES256`, `DenySSECustomerKeys` | 두 Sid 존재 | 일치 (추가 보호) |
| S10 | 삭제 보호 | Retain·termination protection | 4자원 `Retain` | `CREATE_COMPLETE`, TerminationProtection=true, 4자원 `CREATE_COMPLETE` | 일치 |

**bucket policy drift 0:** 실제 정책의 canonical SHA256(`jq -S -c`) `135c46330475ca85401f23ebbf74bb3ade68641f8399e02b84afed111cce6cdd`이 위 소스 StateBucketPolicy를 같은 방식(키 정렬·압축 JSON + 개행)으로 계산한 값과 같다. 10-07 기록의 semantic SHA `5c907aea…`는 계산 방식이 달라 직접 비교하지 않는다.

## 2. Backend 코드 (AWS 설정이 아닌 Terraform 코드 값)

| # | 항목 | 채택값 | 코드 | 판정 |
|---|---|---|---|---|
| B1 | prefix | `phase2/` | `terraform/backends/*.hcl.example` 4개 key 모두 `phase2/…` | 일치 |
| B2 | state key 4개 | network / vpn / rosa-prereq / rosa-runtime `terraform.tfstate` | 4개 정확히 일치 | 일치 |
| B3 | 잠금 | native `use_lockfile=true`, DynamoDB 없음 | backend 4개 + network/vpn/stage-a `versions.tf` 모두 `use_lockfile = true`. AWS 재조회: lock 성격 DynamoDB 테이블 0 | 일치 |
| B4 | `encrypt` | true | 4개 모두 true | 일치 |
| B5 | workspace | default만 | stage-a README "Keep the default workspace" | 일치 |
| B6 | 계정 고정 | — | `allowed_account_ids = ["774055931866"]` | 일치 (추가 보호) |
| B7 | 정책 대상 = backend key | — | bucket policy 객체 8개 = key 4 + `.tflock` 4 | 일치 |

## 3. Relay role / instance profile / PassRole

| # | 항목 | 채택값 | 소스 | 이번 재조회 | 판정 |
|---|---|---|---|---|---|
| R1 | Role | `FDS-Relay-SSM`, path `/` | 동일 | `role/FDS-Relay-SSM`, path `/`, MaxSession 3600 | 일치 |
| R2 | trust | EC2 서비스 | `ec2.amazonaws.com` sts:AssumeRole | 동일, 조건 없음, 문장 1개 | 일치 |
| R3 | 정책 | `AmazonSSMManagedInstanceCore` 출발점 | 그 정책 1개 | 관리형 1개(기본 버전 v2), inline 0 | 일치 |
| R4 | Instance profile | `FDS-Relay-SSM`, path `/`, role 1개 | 동일 | `instance-profile/FDS-Relay-SSM`, path `/`, Roles `[FDS-Relay-SSM]` | 일치 |
| R5 | Terraform은 참조만 | data source | `terraform/stage-a/bootstrap-references.tf` `data "aws_iam_instance_profile"` | (코드 대조) | 일치 |
| R6 | PassRole | `role/FDS-Relay-SSM` 1개 + `iam:PassedToService=ec2.amazonaws.com` | infra-terraform `iam/full-policy-draft-20261009/policies/FDS-IaC-State-PassRole.json` `PassApprovedRelayToEC2` | `FDS-IaC-Operator` 연결 관리형 정책의 Allow PassRole 문장 1개, 대상·조건 일치. inline 정책 0 | 일치 |

## 4. state 원문 접근 음성 시험

| 대상 | 방법 | 결과 | 판정 |
|---|---|---|---|
| 사용자 `321team-gwonuk` / `321team-jaehwan` / `321team-hayeoung` | `simulate-principal-policy` + 실제 bucket policy, 5 action × 8 객체 | 각 40/40 `explicitDeny`. 매칭: bucket policy(`Resource Policy`) + 그룹 `FDS-Human-ReadOnly-Guard-v1` (이중 차단) | PASS |
| role `FDS-ReadOnly-Audit` | 위와 같음 | 40/40 `explicitDeny`, 매칭: bucket policy | PASS |
| role `FDS-Network-Operator` | — | role 부재 | SKIP (생성 후 재시험) |
| 대조군: `FDS-IaC-Operator` 문맥 | 위와 같음 | bucket policy 매칭 0 (거부는 호출자 그룹 Guard에서만 발생) | PASS (bucket policy가 허용 주체를 막지 않음) |
| 실요청: `321team-hayeoung` | 실재하는 `phase2/network/terraform.tfstate.tflock` 이전 버전(`WzOG96YyncySp7vjR3aoMKCzrro2aHwg`) GetObject, 출력 폐기 | RC 254 AccessDenied `s3:GetObjectVersion` … "with an explicit deny in a resource-based policy" | PASS |
| 실요청: 현재 8개 key HeadObject | 객체 미존재 | 8건 모두 404 | 판정 불가 (아래) |

- **스크립트 자동판정 정정.** `issue8-state-negative-test-v1.sh` 원문은 `NEGATIVE_TEST=CHECK_REQUIRED`이며 원문은 고치지 않는다. 원인은 두 가지 스크립트 결함이다. (1) 응답의 `SourcePolicyType` 실제 값 `"Resource Policy"`를 `"resource"`와 비교해 bucket policy 매칭을 0으로 셌다. 같은 result.json을 다시 요약한 진단 ①(`cloudshell-readback.txt` [D])로 정정했고, 재시뮬레이션은 하지 않았다. (2) 없는 객체의 HeadObject는 호출자의 `s3:ListBucket` 보유 여부로 403/404가 정해져 Deny 검증에 쓸 수 없다. 대신 실재하는 이전 버전으로 실요청 1건을 수행했다([E]).
- 시뮬레이터 결과는 정책 평가 설명이며, 실요청은 사용자 1명·객체 1건 범위다. Audit role 실요청과 Network role 시험은 수행하지 않았다.

## 5. 참고 관측

1. **network lock 이력.** `phase2/network/terraform.tfstate.tflock`에 이전 버전 1개(VersionId `WzOG96YyncySp7vjR3aoMKCzrro2aHwg`, 2026-10-09 17:57:44 KST 생성)와 현재 삭제표시 1개가 있다. 이는 이권욱의 network 실제 Plan(`evidence/P2-IAC-01/network-plan-20261009`, 17:57:05–17:57:57 KST)의 정상 native lock 생성·해제와 VersionId·시각이 일치한다. state 객체는 0개다.
2. **목록 조회는 막지 않는다.** Deny는 8개 객체 원문·변경에만 걸린다. 채택값 "공통 서비스·metadata 조회는 유지"와 같다.
3. **보호는 정확한 8개 이름에만 걸린다.** `phase2/` 아래 새 key는 bucket policy 변경이 함께 필요하다.
4. **Agent 관리형 정책은 AWS가 바꿀 수 있다.** 이번 기본 버전 v2. Relay 배치 전에 다시 확인한다.

## 6. 요약

| 구분 | 결과 |
|---|---|
| 대조 항목 | 23 (S1–S10, B1–B7, R1–R6) 모두 일치, **불일치 0** |
| 음성 시험 | PASS (시뮬레이터 4주체 × 40건 + 실요청 1건). Network role SKIP |
| 완료 조건 | ① 채택값 ↔ 실제 설정 대조표(불일치 0) ✔ ② state 원문 접근 음성 시험 결과 ✔ |

AWS 변경 0. 원티켓 #35 AC-4 판정은 이 표로 변경하지 않으며 독립 리뷰 대상이다.
