# P2-IAC-01 — 중앙 bootstrap S10 Retain 실제 템플릿 대조 — 2026-10-11

출처 티켓: [infra-terraform#8](https://github.com/321Team/infra-terraform/issues/8) (P2-IAC-01 Sub-task 1/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

[이권욱 #8 리뷰](https://github.com/321Team/infra-terraform/issues/8#issuecomment-6109083464)의 "S10 원본 연결" 요청에 대한 보완 증적이다. 기존 [`bootstrap-acceptance-20261009/`](../bootstrap-acceptance-20261009/)는 바꾸지 않는다.

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 (`arn:aws:iam::774055931866:user/321team-hayeoung`, 본인 콘솔 MFA 로그인) — `01-identity.json` |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866` (스크립트가 계정 불일치 시 중단) |
| 시각 | 2026-10-11 21:49:04–21:49:07 KST (12:49:04Z 시작) — `summary.txt` |
| 실행 스크립트 | `issue8-s10-retain-readback-v1.sh` SHA256 `4809ba9621a19ee79096ba050852d71bd87cdd6f85bf99c28c2522ac384926d9` (스크립트가 실행 시 자기 해시를 `summary.txt`에 기록) |
| 대상 stack | `arn:aws:cloudformation:ap-northeast-2:774055931866:stack/FDS-Central-Bootstrap-v1/79b25940-c211-11f1-ab33-0a7d3f30f8ff` |
| 대조 소스 | baseline merge `40ac664b83485745ab86b5018b8e19c386484cc8` `phase2/permissions/20261007-central-bootstrap/bootstrap-stack.candidate.json` |
| root 사용 | 없음 |
| AWS 변경 | 없음. `sts get-caller-identity`, `cloudformation describe-stacks`, `cloudformation get-template`만 사용 |

스크립트 전달: CloudShell 파일 업로드 권한이 없어 heredoc 붙여넣기로 만들었다. CloudShell `sha256sum` 결과가 위 해시와 같음을 확인했다.

## 명령별 RC (`summary.txt`)

| 단계 | 명령 | RC |
|---|---|---|
| 1 | `aws sts get-caller-identity` | `IDENTITY_RC=0` |
| 2 | `aws cloudformation describe-stacks --stack-name <exact StackId>` | `DESCRIBE_STACKS_RC=0` |
| 3 | `aws cloudformation get-template --stack-name <exact StackId> --template-stage Original` | `GET_TEMPLATE_RC=0` |
| 4 | 저장된 `03-get-template.json`에서 `jq` 요약 | `SUMMARY_JQ_RC=0` |

AWS 조회 결과를 먼저 파일로 저장한 뒤 RC를 기록하고, 판정은 저장된 파일에서 따로 계산했다. 파이프 마지막 명령의 RC로 앞 조회 성공을 대신하지 않는다.

## 결과

| 항목 | 값 |
|---|---|
| stack 상태 | `CREATE_COMPLETE`, termination protection `true` |
| Original 템플릿 자원 | `RelayProfile`, `RelayRole`, `StateBucket`, `StateBucketPolicy` (4개, 기대값과 일치) |
| Retain | **4/4 `DeletionPolicy=Retain`, `UpdateReplacePolicy=Retain`** → `S10_RETAIN=PASS` |
| 승인 소스와 대조 (리뷰 준비 중 로컬 계산) | `03-get-template.json`의 `TemplateBody`와 승인 소스 JSON을 키 정렬·공백 제거 형태로 비교 → **동일**. canonical SHA256 양쪽 `fb43728c6abc615cf43a34a0b83fa4b3f1e46b8022556e8653cc39e99d2f58ce` |

→ #8 대조표 S10을 "부분 일치"에서 **"일치"** 로 정정한다. 23항목: 일치 22, 부분 일치 1(R6), 불일치 0.

## 수신 방식과 원본 대조

- CloudShell 결과 폴더 `/home/cloudshell-user/issue8-s10-retain.GVQbfR`는 다운로드 권한이 없어 직접 받지 못했다. 스크립트가 원본 파일 내용을 화면에 출력했고, 사용자가 화면 출력을 복사해 전달했다.
- 복사본으로 만든 파일을 CloudShell 원격 `SHA256SUMS`(화면 출력, `cloudshell-SHA256SUMS.txt`)와 대조했다. **8개 중 7개 바이트 일치**(`sha256sum -c` OK).
  - 일치: `01-identity.json`, `03-get-template.json`, `04-retain-summary.json`, `summary.txt`, 빈 파일 3개(`*.stderr`, SHA256 `e3b0c442…b855` = 0바이트)
  - 미수신: `02-describe-stacks.json` (화면에 출력하지 않음). 이 파일에서 뽑은 StackId·상태·termination protection 값은 `summary.txt`에 있다.
- 원격 `SHA256SUMS` 자체는 화면 출력 복사본이므로, 원격 폴더를 직접 재해시한 증거로 쓰지 않는다. 위 "바이트 일치"는 "전달받은 내용이 원격 원본 해시와 같다"는 뜻이다.
- 파일에 자격증명·토큰·MFA 코드는 없다. 계정 ID·ARN·UserId는 식별자다.

## 이 편입이 뜻하지 않는 것

- Original 템플릿에 Retain이 적혀 있다는 확인이다. 실제 자원 설정 전체의 무변경(drift 없음) 증명이 아니다.
- #8·#35 종결, AC-4 전체 PASS, Plan/Apply GO가 아니다.
- R6 전체 유효 PassRole 범위(vpn Apply 전 #11), Audit·Network 역할 실요청 거부(#9/#37)는 이 제출물에 없다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 이 문서 |
| `issue8-s10-retain-readback-v1.sh` | 실행 스크립트 (CloudShell 실행본과 같은 해시) |
| `summary.txt` | 실행 요약: identity·시각·RC·판정 (원격 원본과 바이트 일치) |
| `01-identity.json` | `sts get-caller-identity` 결과 (원격 원본과 바이트 일치) |
| `03-get-template.json` | `get-template --template-stage Original` 결과 (원격 원본과 바이트 일치) |
| `04-retain-summary.json` | 자원별 Type·DeletionPolicy·UpdateReplacePolicy 요약 (원격 원본과 바이트 일치) |
| `01-identity.stderr`, `02-describe-stacks.stderr`, `03-get-template.stderr` | 각 명령 stderr, 모두 0바이트 (원격 원본과 일치) |
| `cloudshell-SHA256SUMS.txt` | CloudShell 원격 폴더 `SHA256SUMS`의 화면 출력 복사본 (8행) |
| `SHA256SUMS` | 이 폴더 파일 해시 |
