# P2-IAC-01 — network 재실행 무변경(AC-5) — 2026-10-12

출처 티켓: [infra-terraform#13](https://github.com/321Team/infra-terraform/issues/13) (P2-IAC-01 Sub-task 6/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

#11 network Apply([6116326502](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6116326502), 20 added, 2026-10-12 10:47 KST)와 **같은 source로 Plan만 다시 실행**해 "바꿀 것 없음"을 확인한 원본이다. 결과 보고: [#13 6118718116](https://github.com/321Team/infra-terraform/issues/13#issuecomment-6118718116). Apply·AWS 변경 없음, 비용 없음.

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 — 본인 사용자(`user/321team-hayeoung`, 콘솔 MFA)로 사전 조회, 본인 MFA로 `assumed-role/FDS-IaC-Operator/321team-hayeoung` 전환 후 Terraform 실행. root 미사용 |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866`(불일치 시 중단). 작업 폴더 `~/iac11-network-20261012-002405`(#11과 같음) |
| source | infra-terraform `81162467bb2f99a099cb7067fbc3f63e1c0dbed8` `terraform/network` 6파일 — 스크립트가 파일별 SHA256 대조(`source_6_files_match_81162467`) |
| 도구 | Terraform 1.16.4 / AWS provider 6.66.0, `init -lockfile=readonly` |
| 스크립트 | `iac13_network_replan.py` — 1회차 SHA256 `2e908bff8d366ce6d524c0fb40481976bc02d86aab77e1166ab0f6ba28816212`, 2~5회차 `e6219ba2e275b6bdd1445b8152e86e7650993d490a64112276b21aed4e56e2c2`. 각 회차 폴더에 실행본 사본 |
| 판정 | `plan -detailed-exitcode`: 0 = No changes(PASS), 2 = 변경(STOP), 그 외 STOP. state VersionId/ETag 전후 비교, lock 전후 확인 |

## 회차 (5회, 모두 편입)

| 회차 폴더 | 시작 KST | 결과 | 내용 |
|---|---|---|---|
| `runs/evidence-replan-20261012-124847/` | 12:48:47 | STOP | 버킷 versioning 조회를 IaC 역할로 시도 → `AccessDenied s3:GetBucketVersioning`(역할에는 `GetBucketLocation`만). Plan 전 중단. 스크립트 수정: 이 조회만 본인 사용자 권한으로 이동(#11 Apply와 같은 방식) |
| `runs/evidence-replan-20261012-125245/` | 12:52:45 | **NO_CHANGES_PASS** | Plan 12:53:29–12:53:38, RC 0 |
| `runs/evidence-replan-20261012-144223/` | 14:42:23 | STOP | assume-role `invalid MFA one time pass code`. Plan 전 중단 |
| `runs/evidence-replan-20261012-144250/` | 14:42:50 | STOP | 같은 MFA 코드 오류. Plan 전 중단 |
| `runs/evidence-replan-20261012-144425/` | 14:44:25 | **NO_CHANGES_PASS** | Plan 14:45:20–14:45:27, RC 0 — #13 보고 회차 |

**정정:** #13 보고(6118718116)의 "시도 3회"는 틀렸다. 실제는 위 5회이며 PASS가 2회(12:52·14:44)다. 12:52 PASS 결과는 실행 당시 보고에 쓰이지 않았고, 이번 원본 수신에서 확인했다.

## 결과 (PASS 2회)

| 확인 | 12:52:45 | 14:44:25 |
|---|---|---|
| Plan RC / 문구 | 0 / `No changes. Your infrastructure matches the configuration.` | 같음 |
| 계획 변경 | 자원 0 / 출력 0 | 같음 |
| Plan 파일 SHA256 | `2309e7b6baf35b72…` | `72338954f47767a2be9e6d394a5ce2679d144935c0b08ddcd1fa1e76a5a00e8e` |
| Plan JSON SHA256 | `119cd34e28a2c7fa…` | `09f1576cd31c13def2a1858c76922ce2adac35a0627c25d72640656b4c1338a7` |
| state 관리 자원 | 20 (+ data 3) | 같음 |
| state VersionId 전후 | `m4zM3let2zBojqhe0Jj_h.qGyCflfMe2` 동일, ETag 동일 | 같음 |
| lock 전후 | 없음 | 없음 |
| 버킷 versioning | Enabled | Enabled |

전체 값은 각 폴더 `execution-summary.json`. Plan 파일 해시가 회차마다 다른 것은 정상(생성 시각 등 포함)이며 판정은 RC·변경 목록으로 한다. 두 PASS 모두 state VersionId가 Apply 시각(01:47:19Z) 그대로다 → 재실행이 state를 쓰지 않았다.

## "Terraform 밖 변경" 표시 5건 — 외부 변경 아님

`resource_drift` 5건(`aws_eip.nat`, `aws_route_table.subnet[private_a/b/c, public_transport_a]`, 모두 update 표시)은 계획 동작이 아니다. 14:44:25 회차 Plan JSON에서 달라진 속성만 출력한 콘솔 복사본이 [`drift-detail-144425.console.txt`](drift-detail-144425.console.txt)다.
- route table 4개: `route`가 `[]` → 같은 코드의 `aws_route`(private 3개 `0.0.0.0/0 → nat-0f0fa5d5de405fa71`, transport `0.0.0.0/0 → igw-003f907eafcc6bfb9`)로 채워짐. route table 자원에 inline route가 없기 때문
- EIP: `association_id`·`network_interface`·`private_ip`(10.20.110.241)가 같은 코드의 NAT Gateway 연결로 채워짐

값은 #11 Apply readback과 같다. Plan은 state를 쓰지 않으므로 다음 Plan에도 표시될 수 있으며 `-refresh-only` apply는 하지 않는다.

## 수신 방식과 원본 대조

- CloudShell 다운로드가 안 되어 5개 tar.gz를 하나의 tar로 묶고, 번호 붙은 base64(100자/줄, 683줄)를 화면에서 복사해 PC에서 복원했다.
- 묶음 tar SHA256 `2ad2eea704268403148108870cf85ab0790c809cbdcadac2dbeced8ea1ead6d5`(51,200 B): **CloudShell 출력값 = PC 복원값**.
- 회차별 tar.gz SHA256(CloudShell `sha256sum` 출력 = PC 값): `124847` `cbdfef96…7bb7e7`, `125245` `5b63fd2f…79623c`, `144223` `ff2e3014…a05605`, `144250` `a3b6b990…0cfb23`, `144425` `a4f4767b…a25104`. tar.gz 자체는 Git에 넣지 않고 하영 비공개 경로에 보관.
- 회차 폴더 내부 `SHA256SUMS`: 13/13, 30/30, 7/7, 7/7, 30/30 일치.

## 넣지 않은 것과 민감정보

- Plan 파일·Plan JSON(`show-json.stdout`): state 사본이 들어 있어 스크립트가 처음부터 증적 폴더 밖에 저장. 해시만 기록.
- state 원문: 내려받지 않음(`head-object` 메타만).
- assume-role 출력: 저장 전에 Credentials 제거(`"redacted": true`). MFA 코드는 `REDACTED`.
- 검사: `AKIA/ASIA`+16자, `SecretAccessKey`·`SessionToken` 값, `PRIVATE KEY`, `aws_secret_access_key` **0건**. 계정 ID·ARN·자원 ID는 식별자.

## 이 편입이 뜻하지 않는 것

- network 한 스택의 재실행 무변경 확인이다. vpn·rosa-prereq 재실행은 각 Apply 뒤 별도다.
- #13·#35 종결, AC-5 전체 PASS, G4 PASS, Apply GO가 아니다.
- 사전 작업창 공지는 하지 않았다. 대신 lock 전후 없음·state 버전 불변으로 다른 writer와 겹치지 않았음을 확인했다(Plan lock 약 9초·7초, `-lock-timeout=60s`).

## 파일

- `runs/evidence-replan-20261012-*/` — 회차별 명령 stdout/stderr, `execution-summary.json`(argv·시각·RC·판정), 실행 스크립트 사본, 내부 `SHA256SUMS`
- `drift-detail-144425.console.txt` — 콘솔 복사본(원본 파일 아님)
- `SHA256SUMS` — 이 폴더 전체 해시

AI 사용: CLAUDE_ASSISTED. 실행·편입 작성자 이하영(자기 승인 아님). 독립 리뷰: 이권욱(이 재실행의 작성·실행 미참여).
