# P2-IAC-01 — vpn 재실행 무변경(AC-5) — 2026-10-12~13

출처 티켓: [infra-terraform#13](https://github.com/321Team/infra-terraform/issues/13) (P2-IAC-01 Sub-task 6/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35) · 수정 [infra-terraform PR #30](https://github.com/321Team/infra-terraform/pull/30)

#11 vpn Apply([6120492825](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6120492825), 8 added, 2026-10-12 17:18 KST) 뒤 vpn **재실행 Plan** 원본이다. 같은 source로는 Relay 반복 교체 결함이 나왔고(STOP), PR #30으로 고친 뒤 병합 source로 `No changes`를 확인했다. 모든 회차 Plan만 실행, Apply·AWS 변경 없음, 비용 없음.

## 회차 (5회, 모두 편입)

| 회차 폴더 (`runs/`) | 시작 KST | source | 결과 |
|---|---|---|---|
| `evidence-vpn-replan-20261012-175115/` | 10-12 17:51:15 | `36c18e2a` (Apply 원본) | **CHANGES_STOP** — Plan RC 2 `Plan: 2 to add, 0 to change, 2 to destroy.` |
| `evidence-vpn-pr30-20261012-181108/` | 10-12 18:11:08 | PR #30 HEAD `192401e` (`main.tf`만 교체) | NO_CHANGES_PASS — Plan RC 0, `terraform test` 22/22 (병합 전 확인) |
| `evidence-vpn-replan-merged-20261013-164729/` | 10-13 16:47:29 | 병합 `6847d906` | STOP — assume-role 형식 오류(MFA 7자리 입력). Plan 전 중단. **편입 전 가림 1건, 폴더 안 `REDACTION.md`** |
| `evidence-vpn-replan-merged-20261013-164843/` | 10-13 16:48:43 | 병합 `6847d906` | STOP — `Invalid length for parameter TokenCode, value: 5`. Plan 전 중단 |
| `evidence-vpn-replan-merged-20261013-164948/` | 10-13 16:49:48 | 병합 `6847d906` | **NO_CHANGES_PASS** — 공식 회차, [#13 보고](https://github.com/321Team/infra-terraform/issues/13) |

## 실행 정보 (공통)

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 — 본인 사용자(`user/321team-hayeoung`, 콘솔 MFA)로 사전 조회, 본인 MFA로 `assumed-role/FDS-IaC-Operator/321team-hayeoung` 전환. root 미사용 |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866`. 작업 폴더 `~/iac11-vpn-20261012-020352`(#11 vpn Apply와 같음) |
| 입력 | `vpn.plan.tfvars.json` SHA256 `bc658c60569a106fc77a062dda2e983d1775862f54f329ef2f28840996683ee3` — vpn Apply와 동일(스크립트 대조) |
| 도구 | Terraform 1.16.4 / AWS provider 6.66.0, `init -lockfile=readonly` |
| source 처리 | Apply에 쓴 `source/`(10파일 `36c18e2a`)는 바꾸지 않음. 18:11·10-13 회차는 별도 폴더에 복사 후 `main.tf`만 `871c0bbad90f145cf153d0694f3f4ec126ea089123a79e2ec3f636c3a80bf5f6`로 교체 — 병합 `6847d906`의 `terraform/vpn` 10파일과 파일별 해시 동일 |
| 스크립트 | 17:51 `iac13_vpn_replan.py` `e51d8425…`, 18:11 `iac13_vpn_pr30_check.py` `465793a8…`, 10-13 `iac13_vpn_replan_merged.py` `6c909f77…` — 각 회차 폴더에 실행본 사본 |

## 결과

| 확인 | 17:51 (수정 전) | 18:11 (PR #30) | **16:49 (병합 공식)** |
|---|---|---|---|
| Plan RC / 요약 | 2 / `2 to add, 0 to change, 2 to destroy` | 0 / `No changes` | **0 / `No changes. Your infrastructure matches the configuration.`** |
| 변경 | `aws_instance.relay`·`aws_eip_association.relay` 교체, 출력 `relay_handoff` | 없음 | 없음 |
| `terraform test` | — | 22 passed | 22 passed |
| state VersionId 전후 | `hCkkiQGd6UgAygqS.aPaRpyOw69jkm8n` 동일 | 동일 | 동일 (LastModified = Apply 08:18:15Z) |
| lock 전후 / managed | 없음 / 8 | 없음 / 8 | 없음 / 8 (+ data 5) |
| Plan / JSON SHA256 | `be6a37e1…` / `7a7a2e11…` | `4e5fe237…` / `2dfb8384…` | `4a45535ad1334fe03cd56a95202225e1e19fc05747de39e19c8af26d2fdc8b49` / `1732a7e0fda2c6da4abcc0cf0792d84612d1a561024c83da8885f1a6aa065303` |

### 교체 원인 (17:51)
`aws_instance.relay`의 `associate_public_ip_address`가 코드 `false`, 실제 `true`(별도 `aws_eip_association`이 EIP `3.36.239.132`를 붙인 뒤 provider가 읽은 값). ForceNew라 같은 source의 Plan마다 Relay 교체가 나왔다. EIP 연결 교체는 그 결과. 발췌: [`replace-detail-175115.console.txt`](replace-detail-175115.console.txt). 수정: PR #30 `lifecycle { ignore_changes = [associate_public_ip_address] }`(생성 시 값은 `false` 유지).

### "Terraform 밖 변경" 표시 4건 (18:11·16:49 공통, 계획 동작 아님)
`aws_eip.relay`(EIP 연결 속성), `aws_instance.relay`(EIP로 생긴 공인 IP, root 디스크 `tags null→{}`), `aws_security_group.relay`(별도 규칙 자원의 egress TCP 443 / ingress UDP 4500·500 — 승인 규칙과 일치), `aws_ssm_document.session_preferences[0]`(`permissions`·`tags` `null→{}`). 속성 출력: [`drift-detail-181108.console.txt`](drift-detail-181108.console.txt). 16:49 회차는 같은 4개 주소(`execution-summary.json`).

## 작업창 기록 (사실대로)

- 17:51: [#13 작업창 공지 6120894960](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6120894960) 뒤 실행, 종료 [6120975636](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6120975636).
- 18:11: **사전 공지 없이 실행**, 사후 기록([#13 6121322473](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6121322473)). [권욱 판단](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6121461041)대로 lock 전후 없음·state 버전 불변을 중간 writer 부재 증명으로 쓰지 않는다.
- 10-13 16:49: 카톡 팀방 공지는 실행 직전(하영). **GitHub 공지 [6140918472](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6140918472)는 16:51:00 KST로 Plan 종료(16:50:58) 2초 뒤** 게시되어 GitHub 기준 사전 공지가 아니다.

## 수신 방식과 원본 대조

- CloudShell **Actions → Download file**로 5개 tar.gz를 묶은 `iac13-vpn-replan-evidence.tar`(81,920 B, PC SHA256 `b4e4e2412854fbbfc5ab46a4b88203365f3da232ef7339b3ca556696f7535752`)를 받았다(검증기간 `FDS-Validation-CloudShellTransfer`, 하영 첫 실제 다운로드). 묶음 tar의 CloudShell 쪽 해시는 받지 않았다 — NOT_VERIFIED.
- 대신 안의 회차별 tar.gz 5개 SHA256이 **각 실행 직후 CloudShell `RESULT`에 출력된 값과 모두 일치**: `175115` `88caf5ea…b2bab0`, `181108` `eb987234…dcd76`, `164729` `052169dd…c13e3`, `164843` `c62e1fa5…45edd`, `164948` `9b86139d…924065`.
- 회차 폴더 내부 `SHA256SUMS`: 30/30, 32/32, 7/7, 7/7, 32/32 일치(164729는 가림 전 기준, 가림 뒤 해당 1줄만 갱신). tar.gz 자체는 Git 밖 비공개 보관.
- **비공개 원본 위치:** 팀 고정 공유 경로 `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\iac13-vpn-replan-evidence.tar` (2026-10-13 17:05 KST 하영 업로드, 공유 경로 파일 SHA256 `b4e4e241…7535752` = PC 값). 가림 전 원본이 들어 있으므로 공유 폴더 밖으로 옮기지 않는다.

## 넣지 않은 것과 민감정보

- Plan 파일·Plan JSON(`show-json.stdout`): state 사본 포함이라 스크립트가 증적 폴더 밖에 저장. 해시만 기록.
- state 원문: 내려받지 않음(`head-object` 메타만). assume-role 출력은 저장 전 Credentials 제거, argv의 MFA 코드는 `REDACTED`.
- **가림 1건:** 16:47:29 회차 `assume-role.stderr`에 AWS가 입력 MFA 코드(형식 오류로 거부·만료)를 되돌려 출력 → 값만 가림. 원본·가림 뒤 해시는 그 폴더 `REDACTION.md`.
- 검사: `AKIA/ASIA`+16자, `SecretAccessKey`·`SessionToken` 값, `PRIVATE KEY`, `aws_secret_access_key` **0건**. 계정 ID·ARN·자원 ID·공인 IP는 식별자.

## 이 편입이 뜻하지 않는 것

- vpn 한 스택의 재실행 무변경 확인이다(network는 [`network-replan-20261012/`](../network-replan-20261012/)). rosa-prereq는 Apply 뒤 별도.
- #13·#35 종결, AC-5 전체 PASS, G4 PASS, vpn 재Apply·#37 route 활성화 승인이 아니다.

## 파일

- `runs/evidence-vpn-*/` — 회차별 명령 stdout/stderr, `execution-summary.json`(argv·시각·RC·판정), 실행 스크립트 사본, 내부 `SHA256SUMS` (164729는 `REDACTION.md` 포함)
- `replace-detail-175115.console.txt`, `drift-detail-181108.console.txt` — 콘솔 복사본(원본 파일 아님)
- `SHA256SUMS` — 이 폴더 전체 해시

AI 사용: CLAUDE_ASSISTED. 실행·편입 작성자 이하영(자기 승인 아님). 독립 리뷰: 이권욱(이 재실행의 작성·실행 미참여. PR #30 리뷰어였으나 이 증적의 생산자는 아님).
