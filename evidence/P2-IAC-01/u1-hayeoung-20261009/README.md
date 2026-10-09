# P2-IAC-01 — 하영 본인 IaC 역할 시험 (U1-I1 + U1-I4 안전 부분) — 2026-10-09

출처 티켓: [infra-terraform#9](https://github.com/321Team/infra-terraform/issues/9) (P2-IAC-01 Sub-task 2/6, Hard Gate 1·2) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)
결과 게시: [#9 댓글 6077985000](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6077985000)

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 (`321team-hayeoung`, 본인 콘솔 MFA 로그인) |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866` |
| 시각 | 2026-10-09 18:06:52 – 18:07:43 KST (`meta.txt`) |
| 대상 역할 | `arn:aws:iam::774055931866:role/FDS-IaC-Operator` — [권욱 부여 결과](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6077294756), infra-terraform PR18 merge `81162467bb2f99a099cb7067fbc3f63e1c0dbed8` |
| 실행 스크립트 | `u1-hayeoung-iac-selftest.sh` SHA256 `903814d03a39587d1cb4fadd2103e1ecd2f04f11fe338158581a375d82b262e1` |
| root 사용 | 없음 |
| AWS 변경 | 없음. STS·Describe·EC2 `--dry-run`·S3 HeadObject만 사용. 생성·수정·삭제 0, 비용 0 |

스크립트 전달: CloudShell 파일 업로드 권한(`cloudshell:GetFileUploadUrls`)이 없어 heredoc 붙여넣기로 만들었고, CloudShell에서 `sha256sum` 결과가 위 값과 같음을 확인했습니다(사용자 콘솔 출력).

## 수신 방식과 한계

- CloudShell 결과 폴더 `/home/cloudshell-user/u1-hayeoung-20261009-090652`(파일 37개)는 다운로드 권한이 없어 **원본 파일을 받지 못했습니다.**
- `cloudshell-readback.txt`는 사용자가 CloudShell에서 `cat`으로 출력한 내용을 복사한 **콘솔 제출 자료**입니다. 대상은 `meta.txt`, `summary.tsv`, `SHA256SUMS`, `P2-role-identity.stdout`, `P5`/`N5` stderr, `N2` cmd입니다. 원본 바이트가 아니므로, 이 파일로 원격 SHA256SUMS를 재검증했다고 주장하지 않습니다. 탭·줄바꿈은 터미널 복사 과정에서 바뀌었을 수 있습니다.
- 원격 `SHA256SUMS`(37행)는 원본 폴더의 해시 기록으로 함께 옮겨 적었습니다.
- MFA 코드 인자는 `.cmd` 명령 기록에서 `REDACTED` 처리합니다. N1/N2 AssumeRole stdout은 `run()`이 먼저 결과 파일에 기록한 뒤 `sed`로 `SecretAccessKey`와 `SessionToken`을 마스킹하는 구현입니다. 따라서 **임시 자격증명 디스크 무저장을 보장한 실행이 아닙니다.** N2는 성공했고, 원격 stdout 원본은 미수신이므로 사후 마스킹 완료 여부를 독립 확인하지 못했습니다. 이 편입본에는 N1/N2 AssumeRole stdout이 없으며, 현재 편입본에서 실제 자격증명 값은 발견하지 않았습니다. MFA 장치 ARN·역할 UserId는 식별자입니다.

## 결과

| case | 내용 | 기대 | 실제 | 판정 |
|---|---|---|---|---|
| N1 | 다른 RoleSessionName(`321team-gwonuk`)+MFA로 assume | 거부 | AccessDenied | PASS |
| N2 | MFA 코드 없이 본인 이름으로 assume | 거부 | 성공 | INFO |
| P1 | 본인 이름+MFA로 assume | 성공 | 성공 | PASS |
| P2 | 역할 세션 identity | `assumed-role/FDS-IaC-Operator/321team-hayeoung` | 일치 | PASS |
| P3 | 서울 DescribeVpcs | 성공 | 성공 | PASS |
| P4 | 소유 태그 CreateVpc `--dry-run` | DryRunOperation | DryRunOperation | PASS |
| N3 | 태그 없는 CreateVpc `--dry-run` | 거부 | UnauthorizedOperation | PASS |
| N4 | us-east-1 DescribeVpcs | 거부 | 거부 | PASS |
| P5 | `phase2/network/terraform.tfstate` HeadObject | 200 또는 404 | 404 (state 미생성) | PASS |
| N5 | `phase2/u1-other/terraform.tfstate` HeadObject | 403 | 404 | 판정 보류 |
| N6 | IAM ListUsers | 거부 | 거부 | PASS |

`summary.tsv` 원문에서 N5는 스크립트 자동판정상 `FAIL`로 찍혀 있습니다. 위 표의 "판정 보류"는 아래 해석에 따른 사람 판정이고, 원문은 고치지 않았습니다.

- **N2 (INFO):** 본인 이름으로 OTP 인자를 생략한 AssumeRole 성공이 제출됐습니다. 콘솔 MFA 문맥을 사용했을 가능성이 있지만, 이 편입본에는 해당 요청의 평가 문맥 원본이 없어 그 원인을 독립 실측한 것으로 단정하지 않습니다. OTP 인자 생략을 실제 MFA 문맥 부재와 동일시하지 않으며, **noMFA 실제 거부는 NOT_RUN**입니다. 장기 Access Key 0개는 기존 조회 기록의 설명이며 이번 제출물에서 새로 검증한 항목이 아닙니다. trust의 MFA=true 조건은 별도 STATIC readback으로 소비하고 실제 STS 거부와 구분합니다.
- **N5 (판정 보류):** 허용 key(P5)와 허용 밖 key(N5)가 같은 404를 반환했습니다(stderr SHA256 동일 `2e1b4221…`). 존재하지 않는 객체의 HeadObject로는 권한 차이를 구분할 수 없을 수 있습니다. 중앙 보완 [PR196](https://github.com/321Team/fds-project-evidence/pull/196)(merge `3ada349cf48e60d8bdc31098c0847644ec24efdc`)이 편입됐습니다. identity 정책상 타 key Get/Put 허용 근거 없음(STATIC+SIMULATION), bucket Allow0·ACL 비활성까지 확인한 별도 자료이며, 이 실행의 N5 RUNTIME 거부는 UNDETERMINED로 유지합니다. 원격37파일의 바이트 미수신 상태도 변경하지 않습니다.

## 이 편입이 뜻하지 않는 것

- 전체 U1 PASS가 아닙니다. I2(Plan)·I3(lock 경쟁)·I5(오류 후 lock 해제), 실제 noMFA 거부는 NOT_RUN입니다.
- 권욱 본인 시험과 Plan 결과(evidence PR #193)를 대신하지 않습니다.
- #9·#35 종결, Plan/Apply GO, Network 역할 부여가 아닙니다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 이 편입 설명 |
| `u1-hayeoung-iac-selftest.sh` | 실행 스크립트 사본 (실행본과 SHA256 동일) |
| `cloudshell-readback.txt` | CloudShell 결과 폴더 콘솔 출력 복사본 + 원격 SHA256SUMS 37행 |
| `SHA256SUMS` | 위 3개 파일의 해시 |

AI 사용: CLAUDE_ASSISTED. 작성·실행자 이하영의 자기 승인이 아니며 독립 리뷰 대상입니다.

## 기록 정정 — 2026-10-09

이권욱(CODEX_ASSISTED)이 기존 리뷰의 보안 처리 이력 정정을 반영했습니다. 실행 당시 스크립트와 콘솔 제출 사본의 바이트는 변경하지 않았습니다. 과거 실행이 메모리 전용 처리였던 것처럼 소급 기록하지 않으며, 이 정정을 위해 AWS 재시험·새 키 발급·권한 변경을 하지 않았습니다. 권욱이 수정에 참여했으므로 기존 권욱 리뷰를 새 수정본의 독립 승인으로 쓰지 않고 재환에게 독립 검토를 요청합니다. 전체 U1·업무 AC·Apply GO 판정은 별도입니다.
