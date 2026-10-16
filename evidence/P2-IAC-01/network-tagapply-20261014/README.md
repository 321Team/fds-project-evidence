# P2-IAC-01 — network subnet ROSA LB 역할 태그 Plan·Apply — 2026-10-13~14

출처 티켓: [infra-terraform#11](https://github.com/321Team/infra-terraform/issues/11) (P2-IAC-01 Sub-task 4/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

ROSA HCP 생성 preflight가 확인하는 subnet 역할 태그 2개를 network root에서 추가한 회차의 원본이다([#35 요청 6118992451](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6118992451), [태그 소유권 리뷰 6119267125](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6119267125)). 비용 없음(태그만).

| 회차 | 결과 보고 | 독립 검토 |
|---|---|---|
| Plan 2026-10-13 | [#11 6143615282](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6143615282) | [6144035652](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6144035652) (원본 검증·제한 Apply GO) |
| Apply 2026-10-14 | [#11 6160026041](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6160026041), 원본 전달 [6160075162](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6160075162) | [6160427524](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6160427524) (`TAG_APPLY_EVIDENCE=ACCEPTED`, `VERIFY_PLAN=NO_CHANGES`) |

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이하영 — 본인 사용자(`user/321team-hayeoung`, 콘솔 MFA)로 사전 조회, 본인 MFA로 `assumed-role/FDS-IaC-Operator/321team-hayeoung` 전환 후 Terraform 실행. root 미사용 |
| 환경 | AWS CloudShell, ap-northeast-2, 계정 `774055931866`. 작업 폴더 `~/iac11-tagplan-20261013-101518` |
| source | infra-terraform `f1f8adf66d3b3c9348ebb919fe0dbb4f8fa54fe2`(PR27 병합 이후) `terraform/network` 6파일 — `source-manifest.json` |
| 도구 | Terraform 1.16.4 / AWS provider 6.66.0, `init -lockfile=readonly`, workspace default |
| backend | S3 `fds-tfstate-774055931866-ap-northeast-2` / `phase2/network/terraform.tfstate`, encrypt·use_lockfile=true (Apply 회차 init 후 대조 `backend_after_init`) |

## 회차 (2회, 모두 편입)

| 회차 폴더 | KST | 결과 | 내용 |
|---|---|---|---|
| `runs/evidence-tagplan-20261013-191626/` | 2026-10-13 19:16:26–19:17:46 (Plan 19:17:22–19:17:32) | `TAG_PLAN_READY_FOR_REVIEW` | Plan RC 2 `0 to add, 2 to change, 0 to destroy.` `plan-judgement.json`: 두 subnet 모두 `tags`·`tags_all`만 변경, unexpected 0. state VersionId·ETag 전후 동일 |
| `runs/evidence-tagapply-20261014-120837/` | 2026-10-14 12:08:37–12:10:22 (Apply 12:10:00–12:10:06) | `TAG_APPLY_AND_READBACK_PASS` | Apply RC 0 `0 added, 2 changed, 0 destroyed.` 사후 readback 14/14, 검증용 Plan RC 0 `No changes.` |

스크립트: Plan `iac11_network_tagplan.py` SHA256 `2d58741c18ec460e4df65aa1cb67dbafd1c7cc5e8238a0800b880336ac055a88`, Apply `iac11_network_tagapply.py` SHA256 `4acac3932343e7b6c48c48140111541878402b18f95d7f1e0a97d551da22b4e3`. 각 회차 폴더에 실행본 사본.

**이 폴더에 없는 회차(AWS 호출 0):**
- 2026-10-13 19:15:19 Plan 첫 시도: CloudShell 셸의 `TF_DATA_DIR` 환경변수를 스크립트 안전검사가 감지해 AWS 호출 전 STOP. `env -u TF_DATA_DIR`로 재실행한 것이 위 Plan 회차다. 해당 원본은 CloudShell에만 있다.
- 2026-10-14 11:53 시작 기록은 A3 작업 미종료로 실행 없이 철회했다([정정 6159907710](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6159907710)). 새 시작 기록 [6159977143](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6159977143) 후 위 Apply 회차를 실행했다.

## 결과

| 확인 | 값 |
|---|---|
| saved Plan | `tagplan-20261013-191626.tfplan` SHA256 `9d65852fa85ce28a1f11dba353e41ecc415b4855d92474efa334d5fb24328a81` (Apply 전 재확인) |
| Plan JSON | SHA256 `59d2a14048c4b835c91d92aa1c8787dc3b37ebe46e80451422ec28bf939a1512` |
| `private_a` `subnet-044ced60c3c705ac6` | `kubernetes.io/role/internal-elb = "1"` 추가, 기존 태그·CIDR·공인 IP 자동할당·AZ ID 불변 |
| `public_transport_a` `subnet-0fbc846bde668f0f3` | `kubernetes.io/role/elb = "1"` 추가, 나머지 불변 |
| `private_b`·`private_c` | 태그·속성 불변 |
| route / Relay | RT 4개 전후 동일·`10.1.93.0/24` 없음 / SG `sg-0f1e8a5dbecabccee` 규칙 동일·`i-05e4b63d31d8d5ac5` running |
| state | Apply 전 VersionId `m4zM3let2zBojqhe0Jj_h.qGyCflfMe2`·lineage `64258b91-83ed-bf3d-89fc-1d11eac31351`·serial 2 → 후 VersionId `YsrVyYugX33IFWD.TnMStibrWZJDQRmZ`·같은 lineage·serial 3 |
| 잠금 | 두 회차 모두 종료 후 lock 없음 |

`resource_drift` 5건(`aws_eip.nat`, `aws_route_table.subnet` ×4)은 Plan 회차에서 확인한 생성 시점 기록 차이다(EIP의 NAT 연결값, RT의 standalone route 반영. private→`nat-0f0fa5d5de405fa71`, transport→`igw-003f907eafcc6bfb9`). 같은 내용이 [network-replan-20261012](../network-replan-20261012/README.md)에 있다. CloudTrail로 변경 주체를 조회한 것은 아니다.

## 수신 방식과 원본 대조

- Plan 회차: CloudShell에서 tar.xz(`41607c0c7400351d3bb2d288fd3b3dc1d3ba70583e72154a1dae1b822dd7277e`, 41,120 B)를 번호 붙은 base64 549줄로 화면 복사해 PC 복원, 해시 일치. 회차 tar.gz `evidence-tagplan-20261013-191626.tar.gz` SHA256 `18c275ef6628211afb4329144cbbb6da93a9973ca224c69d78b05fe49915e1d2`.
- Apply 회차: CloudShell **파일 다운로드**로 받아 팀 공유 경로에 복사. `evidence-tagapply-20261014-120837.tar.gz` SHA256 `543eac6ea1d015f6c54024b9443fc81284aeb096755f27bc35ba5019f33e046a`(19,417 B) — CloudShell 값 = 공유 경로 사본 재해시 = 로컬 사본.
- 회차 폴더 내부 `SHA256SUMS`: Plan 44/44, Apply 53/53 일치. tar.gz 자체는 Git에 넣지 않고 하영 비공개 경로·팀 공유 경로에 보관.

## 넣지 않은 것과 민감정보

- saved Plan 파일과 전체 Plan JSON(`show-json.stdout`)은 prior state 사본이 들어 있어 넣지 않았다. 비공개 묶음 `iac11-network-tagplan-20261013.zip`(SHA256 `0ca8f630608190e3541b19612c0a4b9066672d6655601f76c4f5741ff46e1c53`)으로 권욱에게 전달·검증됐다.
- state 원문은 수집하지 않았다. Apply 회차는 `state pull`을 메모리에서 lineage·serial만 읽고 stdout을 저장하지 않았다(`state-pull-*.stdout` 없음).
- `assume-role.stdout`은 Credentials를 저장 전 제거한 사본이다. MFA 코드 없음. 실제 값 패턴(AKIA/ASIA 키, SecretAccessKey·SessionToken 값, PRIVATE KEY) 검사 0건.
