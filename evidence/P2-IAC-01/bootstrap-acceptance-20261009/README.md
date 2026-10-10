# P2-IAC-01 — 중앙 bootstrap 인수 확인 (state backend·Relay profile) — 2026-10-09

출처 티켓: [infra-terraform#8](https://github.com/321Team/infra-terraform/issues/8) (P2-IAC-01 Sub-task 1/6, AC-4 "State와 Secret 접근이 통제된다" 중 State) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 (`321team-hayeoung`, 본인 콘솔 MFA 로그인) |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866` (스크립트가 `sts get-caller-identity`로 계정 확인 후 진행) |
| 시각 | 재조회 2026-10-09 22:56:52–22:57:22 KST, 음성 시험 22:57:37–22:58:00 KST, 진단 ①–③은 그 직후 (정확한 시각 미기록) |
| 도구 | aws-cli 2.37.6 (CloudShell). Terraform은 실행하지 않음 (Terraform 1.16.4 / AWS provider 6.66.0 pin은 코드 대조 대상) |
| 실행 스크립트 | `issue8-bootstrap-readback-v1.sh` SHA256 `e140bb55d3b6127293a1984a9292a9a75e92be8e51a668e465b191705de4edae` · `issue8-state-negative-test-v1.sh` SHA256 `a439653fa217d1d458d335a6ae2a29d6f727047e1594904c988aa7388708e1d2` |
| 대조 소스 | baseline merge `40ac664b83485745ab86b5018b8e19c386484cc8` (bootstrap stack 소스) · infra-terraform `81162467bb2f99a099cb7067fbc3f63e1c0dbed8` (backend·PassRole 정책 소스, 현재 main `cca0388`까지 해당 파일 변경 없음) |
| root 사용 | 없음 |
| AWS 변경 | 없음. STS·CloudFormation Describe/List·S3 Get*/List*/HeadObject·IAM Get/List/Simulate·DynamoDB ListTables만 사용. 생성·수정·삭제 0, 유료 자원 생성 0 |

스크립트 전달: CloudShell 파일 업로드 권한(`cloudshell:GetFileUploadUrls`)이 없어 heredoc 붙여넣기로 만들었다. readback 스크립트는 1회 붙여넣기에 실패해 3조각으로 나눠 만든 뒤 합쳤다. 두 파일 모두 CloudShell `sha256sum` 결과가 위 값과 같음을 확인했다(사용자 콘솔 출력, `cloudshell-readback.txt` [A]).

## 결과

상세 대조는 [`acceptance-table.md`](acceptance-table.md)에 있다.

| 완료 조건 (#8) | 결과 |
|---|---|
| 채택값 ↔ 실제 설정 대조표 (불일치 0 또는 사유) | 23항목 대조: 일치 21, 부분 일치 2, **불일치 0**. bucket policy가 승인 소스와 canonical SHA256 일치(drift 0). 미대조 범위: S10 실제 배포 템플릿의 Retain, R6 전체 부착 정책의 유효 PassRole 범위 |
| state 원문 접근 음성 시험 결과 | 사용자 3명 시뮬레이터 각 40/40 bucket policy `explicitDeny`(제출 결과). 사용자 실요청 1건 "explicit deny in a resource-based policy". **Audit role은 참고 계산(역할 유효 권한 NOT VERIFIED), IaC 대조군은 조건식 참고 평가(역할 허용 RUNTIME 아님).** Network role은 부재로 SKIP |

## 수신 방식과 한계

- CloudShell 결과 폴더 `/home/cloudshell-user/issue8-readback.E9d7ig`, `/home/cloudshell-user/issue8-negative.vlcww3`는 다운로드 권한이 없어 **원본 파일을 받지 못했다.** 원격 폴더의 `SHA256SUMS`도 이 편입에 없다.
- `cloudshell-readback.txt`는 사용자가 CloudShell 화면 출력을 복사한 **콘솔 제출 자료**다. 원본 바이트가 아니므로 이 파일로 원격 결과를 재해시했다고 주장하지 않는다. 진단 ① 출력은 복사 과정에서 명령 앞부분이 잘려 있어, 실행 명령은 안내문 원문을 함께 적었다.
- state 원문은 내려받거나 출력하지 않았다. 진단 ②의 GetObject는 거부됐으며, 출력 대상도 `/dev/null`이었다.
- `cloudshell-readback.txt`에는 자격증명·토큰·MFA 코드가 없다. 계정 ID·ARN·VersionId는 식별자다.

## 자동판정 정정 (원문은 고치지 않음)

`issue8-state-negative-test-v1.sh` 원문 결과는 `NEGATIVE_TEST=CHECK_REQUIRED`(시뮬레이터 4건 FAIL, HeadObject 8건 FAIL)다. 아래는 사람 판정이며, 원인은 스크립트 결함이다.

1. **시뮬레이터 집계 정정.** 스크립트가 `SourcePolicyType`을 `"resource"`와 비교했으나 실제 값은 `"Resource Policy"`라 bucket policy 매칭을 0으로 셌다. 같은 result.json을 다시 요약(진단 ①)하니 4주체 모두 40/40 `explicitDeny`, 매칭에 `Resource Policy:ResourcePolicy`가 포함됐다. 재시뮬레이션은 하지 않았다. 이 정정은 집계 오류만 바로잡으며, PASS로 인정하는 범위는 사용자 3명이다(Audit role·IaC 대조군은 아래 "리뷰 반영 정정").
2. **HeadObject 404 → 판정 불가.** 8개 key 모두 현재 객체가 없다. 없는 객체의 HeadObject는 호출자의 `s3:ListBucket` 보유 여부로 403/404가 정해지므로 Deny 검증에 쓸 수 없다. 대신 실재하는 lock 이전 버전에 GetObject를 수행했다(진단 ②) → resource-based policy explicit deny.
3. 수정 스크립트(v1.1, 비교값만 변경)는 이 편입에 넣지 않았다. 실행하지 않았기 때문이다.

## 리뷰 반영 정정 (2026-10-10)

[이권욱 리뷰](https://github.com/321Team/fds-project-evidence/pull/200#pullrequestreview-5471572816)의 차단 2건을 반영해 설명·판정표만 정정했다. **원본 스크립트 2개와 `cloudshell-readback.txt`는 바이트를 바꾸지 않았다.** 새 AWS 실행은 없다.

1. **판정 범위.** 최초 제출의 "4주체 × 40건 + 실요청 1건 PASS" 합산을 철회한다. AWS `SimulatePrincipalPolicy`는 IAM role에 대한 resource-based policy 시뮬레이션을 지원하지 않는다고 명시하므로, Audit role 결과는 참고 계산(역할 유효 권한 NOT VERIFIED)이다. IaC 대조군은 사용자 정책을 소스로 한 문맥 치환이므로 조건식 참고 평가이며 역할 허용 RUNTIME이 아니다. PASS로 인정하는 범위는 사용자 3명의 시뮬레이션 결과와 사용자 실요청 1건이다.
2. **대조 범위.** S10은 termination protection 관측만 일치하며 실제 배포 템플릿의 `Retain`은 대조하지 않았다. R6은 `iam:PassRole` 문자열을 가진 Allow 문장 1개와 inline 0(진단 ③)을 관측했으나, 전체 부착 정책의 유효 PassRole 범위는 대조하지 않았다. 종합은 "23항목 대조, 불일치 0, 미대조 범위 별도 표시"로 바꿨다.

## 이 편입이 뜻하지 않는 것

- #8·#35 종결, AC-4 전체(Secret 부분 포함) PASS, Plan/Apply GO가 아니다.
- Network role 음성 시험, Audit role 실요청·유효 권한, `FDS-IaC-Operator` 실제 state 읽기·쓰기(허용 쪽 Runtime), 실제 배포 템플릿 대조, 유효 PassRole 전체 범위는 이 제출물에 없다. 허용 쪽 시험은 #9 범위다.
- 10-07 bootstrap 원본(root CloudShell `fds-central-bootstrap-create-j1_eozi9`, `fds-central-bootstrap-verify-22_0s1l3`)의 편입이 아니다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 이 편입 설명 |
| `acceptance-table.md` | 채택값 ↔ 소스 ↔ 실제 대조표와 음성 시험 판정 |
| `cloudshell-readback.txt` | CloudShell 콘솔 출력 복사본 (생성 확인·재조회·음성 시험·진단 ①–③) |
| `issue8-bootstrap-readback-v1.sh` | 재조회 스크립트 사본 (실행본과 SHA256 동일) |
| `issue8-state-negative-test-v1.sh` | 음성 시험 스크립트 사본 (실행본과 SHA256 동일) |
| `SHA256SUMS` | 위 5개 파일의 해시 |

AI 사용: CLAUDE_ASSISTED. 작성·실행자 이하영의 자기 승인이 아니며 독립 리뷰 대상이다(이권욱 우선. 이권욱은 이 시험의 작성·실행에 참여하지 않았다).
