# P2-IAC-01 — vpn(Relay) Apply·readback 원본 — 2026-10-12

출처 티켓: [infra-terraform#11](https://github.com/321Team/infra-terraform/issues/11) (P2-IAC-01 Sub-task 4/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35) · 매핑표 [#35 6182552506](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6182552506) AC-2·AC-3

승인된 vpn saved Plan을 그대로 1회 Apply하고 Relay를 조회(readback)한 원본이다. 지금까지 비공개 공유 경로와 #11 기록에만 있던 것을 증적 저장소에 편입한다. **새 실행 없음.** 💰 이 Apply로 Relay EC2·EBS·EIP 과금이 시작됐다(2026-10-12 17:18 KST).

## 승인·검토 기록

| 항목 | 링크 |
|---|---|
| saved Plan 승인·Apply GO | [#11 6120046778](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6120046778) (`VPN_APPLY_GO=APPROVED_WITH_EXECUTION_PREFLIGHT`, 권욱) |
| 시작 기록 / 실행 결과 | [#11 6120338125](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6120338125) / [#11 6120492825](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6120492825) |
| 원본 전달 | [#11 6120669375](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6120669375) |
| **원본 독립 검토** | [#11 6121082379](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6121082379) — 8개 생성·API readback 수용(권욱). 호스트 bootstrap·Stage-A/G4는 분리 |

## 실행 정보 (`original/evidence-apply/execution-summary.json`)

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 — 새 본인 MFA 세션 `arn:aws:sts::774055931866:assumed-role/FDS-IaC-Operator/321team-hayeoung`, root 미사용 |
| 시각 | 2026-10-12 17:17:05–17:21:08 KST, Apply 17:17:50–17:18:15 |
| source | infra-terraform `36c18e2a3c8353314e3f618db4f0d6db578b2805` `terraform/vpn` 10파일 |
| 적용 Plan | `vpn.tfplan` SHA256 `0bb10dc983b46b0145c94f8e26f553fe2487d175452d6f40a17e3d1116c01e23`, 입력 `vpn.plan.tfvars.json` `bc658c60…` |
| 결과 | RC 0, `Apply complete! Resources: 8 added, 0 changed, 0 destroyed.`, `APPLY_AND_READBACK_PASS`, readback 확인 19/19 |
| 스크립트 | `original/iac11_vpn_apply.py` |

## 이 원본이 받치는 것

- **AC-2 승인 Plan = Apply 결과:** 승인 Plan 8 create → `8 added, 0 changed, 0 destroyed`, state managed 8(`state-list.stdout`)
- **AC-3 Security/Output:** Relay SG ingress UDP 500·4500, egress TCP 443(`rb-sg-rules.stdout`), `source_dest_check=false`·IMDSv2·암호화 EBS(`rb-instance`·`rb-volume`), EIP 연결(`rb-eip`), On-Prem route 0(`rb-rts`), 세션 문서 생성·내용(`rb-ssm-doc*`), `relay_handoff`·`session_document_source` 출력(`output-*.stdout`)
- 재실행 무변경은 [`vpn-replan-20261013/`](../vpn-replan-20261013/) — 이 Apply 이후 같은 source의 Plan에서 Relay 반복 교체 결함이 발견되어 [PR #30](https://github.com/321Team/infra-terraform/pull/30)으로 수정됐다. 이 Apply 자체(8개 생성)는 그대로 유효하다

## 수신과 원본 대조

- 비공개 공유 원본: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\iac11-vpn-apply-20261012.zip` — 2026-10-15 하영이 **공유 사본을 직접 재해시** `ccf7dde70bc4b37bdd65285059f6f6ab21454459d92b57d84ec779900726d943` (75,756 B) = #11 게시값
- 그 ZIP을 그대로 풀어 `original/`에 둠. `MANIFEST.sha256` 77/77(공유 ZIP 기준), `evidence-apply/SHA256SUMS` 73/73 일치
- `iac11-vpn-apply-20261012.tar.gz`(`159c08af2376cb09551c347754d1ffa87640297bcb6fa256b72b2aa2875537df`, 22,935 B)는 CloudShell에서 만든 전달용 묶음으로 `evidence-apply/`와 같은 내용이다. 저장소가 `.tar.gz`를 추적하지 않아 넣지 않았다 — `original/MANIFEST.sha256` 76행에 해시가 있고 원본은 위 공유 ZIP 안에 있다(MANIFEST 대조는 이 1개를 뺀 76/77)
- `original/README-REVIEW.md`는 전달 당시 동봉한 설명(원문 그대로)

## 넣지 않은 것과 민감정보

- state 원문, 전체 Plan 원문, 자격증명(assume-role Credentials는 저장 전 제거), MFA 코드, PSK — 처음부터 묶음에 없음
- 검사: `AKIA/ASIA`+16자, `SecretAccessKey`·`SessionToken` 값, `PRIVATE KEY`, `aws_secret_access_key`, MFA 코드 값 **0건**. `rb-ssm-doc-content`·user_data의 AWS SSM Agent PGP **공개키**는 비밀이 아님. 계정 ID·ARN·자원 ID·Relay EIP는 식별자

## 이 편입이 뜻하지 않는 것

- #11·#35 종결, Stage-A/G4 PASS, 호스트 bootstrap·터널·route 활성화 PASS가 아니다. `stage_a_ready=false` 그대로다.

AI 사용: CLAUDE_ASSISTED. 실행·편입 작성자 이하영(자기 승인 아님). 독립 리뷰: 이권욱(원본 검토자이며 이 실행의 작성·실행 미참여).
