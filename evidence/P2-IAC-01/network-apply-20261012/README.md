# P2-IAC-01 — network Apply·readback 원본 — 2026-10-12

출처 티켓: [infra-terraform#11](https://github.com/321Team/infra-terraform/issues/11) (P2-IAC-01 Sub-task 4/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35) · 매핑표 [#35 6182552506](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6182552506) AC-2·AC-3·VPC 요구사항

승인된 network saved Plan을 그대로 1회 Apply하고 실제 자원을 조회(readback)한 원본이다. 지금까지 비공개 공유 경로와 #11 기록에만 있던 것을 증적 저장소에 편입한다. **새 실행 없음.** 💰 이 Apply로 NAT Gateway·NAT EIP 과금이 시작됐다(2026-10-12 10:47 KST).

## 승인·검토 기록

| 항목 | 링크 |
|---|---|
| saved Plan 독립 승인 | [#11 6116244757](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6116244757) (권욱) |
| Apply GO | [#11 6115403189](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6115403189) (하영 실행 Lead) |
| 실행 결과 보고 | [#11 6116326502](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6116326502) |
| 원본 전달 | [#11 6116368629](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6116368629) |
| **readback 원본 독립 검토** | [#11 6117337052](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6117337052) — `NETWORK_APPLY_READBACK_REVIEW=ACCEPTED` (권욱) |

## 실행 정보 (`original/evidence-apply/execution-summary.json`)

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 — 새 본인 MFA 세션 `arn:aws:sts::774055931866:assumed-role/FDS-IaC-Operator/321team-hayeoung`, root 미사용 |
| 시각 | 2026-10-12 10:44:50–10:47:35 KST, Apply 10:45:33–10:47:18 |
| source | infra-terraform `81162467bb2f99a099cb7067fbc3f63e1c0dbed8` `terraform/network` 6파일(해시 대조) |
| 적용 Plan | `network.tfplan` SHA256 `e5e775ceb4dcec64b050eaeab0f84d3f6bd0f5765554cdfc61d9f213898383b8` (실행 전 재확인) |
| 결과 | RC 0, `Apply complete! Resources: 20 added, 0 changed, 0 destroyed.`, `APPLY_AND_READBACK_PASS`, readback 확인 20/20 |
| 스크립트 | `original/iac11_network_apply.py` |

## 이 원본이 받치는 것

- **AC-2 승인 Plan = Apply 결과:** 승인 Plan 20 create → `20 added, 0 changed, 0 destroyed`, state managed 20(`state-list.stdout`)
- **AC-3 Route/Output:** private 3 `0.0.0.0/0 → NAT`, transport `0.0.0.0/0 → IGW`, On-Prem `10.1.93.0/24` 0건(의도된 비활성, #37 3단계 전), `network_handoff` 출력(`output.stdout`), `rb-*` 조회 원본
- **VPC 요구사항:** `vpc-039718404350154d9` `10.20.0.0/16`, DNS support·hostnames true
- 재실행 무변경은 [`network-replan-20261012/`](../network-replan-20261012/)

## 수신과 원본 대조

- 비공개 공유 원본: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\iac11-network-apply-20261012.zip` — 2026-10-15 하영이 **공유 사본을 직접 재해시** `4a5f69b018babf3e835782fab754d2bce792cec4b00742e4919b0fdbca714132` (39,293 B) = #11 게시값
- 그 ZIP을 그대로 풀어 `original/`에 둠. `MANIFEST.sha256` 60/60, `evidence-apply/SHA256SUMS` 57/57 일치
- `original/README-REVIEW.md`는 전달 당시 동봉한 설명(원문 그대로)

## 넣지 않은 것과 민감정보

- state 원문, 전체 Plan 원문, 자격증명(assume-role Credentials는 저장 전 제거), MFA 코드 — 처음부터 묶음에 없음
- 검사: `AKIA/ASIA`+16자, `SecretAccessKey`·`SessionToken` 값, `PRIVATE KEY`, `aws_secret_access_key`, MFA 코드 값 **0건**. 계정 ID·ARN·자원 ID·NAT 공인 IP는 식별자

## 이 편입이 뜻하지 않는 것

- #11·#35 종결, Stage-A/G4 PASS가 아니다. 출력의 `stage_a_ready=false`(network만 생성 시점) 그대로다.

AI 사용: CLAUDE_ASSISTED. 실행·편입 작성자 이하영(자기 승인 아님). 독립 리뷰: 이권욱(원본 readback 검토자이며 이 실행의 작성·실행 미참여).
