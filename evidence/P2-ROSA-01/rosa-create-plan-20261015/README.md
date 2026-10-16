# P2-ROSA-01 — ROSA HCP 생성 saved Plan 수집 (3 create / 0 change / 0 destroy) — 2026-10-15

출처 티켓: [infra-rosa#4](https://github.com/321Team/infra-rosa/issues/4) (P2-ROSA-01 Sub-task 2/6) · 원티켓 [fds-project-baseline#38](https://github.com/321Team/fds-project-baseline/issues/38) · 선행 증적 [A3 Stage 1](../../P2-IAC-01/rosa-prereq-stage1-20261014/README.md) · [A3 Stage 2](../../P2-IAC-01/rosa-prereq-stage2-20261015/README.md)

`terraform/rosa-runtime`의 **생성 saved Plan 1회 수집**과 그 검사 결과의 기록이다. **Apply(클러스터 생성)는 하지 않았다.** 이 폴더에는 **README와 해시만** 둔다. saved Plan·Plan JSON·tfvars 사본·실행 로그는 팀 공유 경로에 비공개로 보관한다.

## 승인과 검토

| 항목 | 링크 |
|---|---|
| 입력 Freeze (이름 `fds-rosa-hcp`, OpenShift `4.22.17`) | [#4 6162036371](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6162036371) |
| 이전 회차 (Plan 전 STOP, 이번 Plan과 별개) | v6 12:51 `tf-zip-sum`(`/tmp/tfbin` 소실) [6184026192](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6184026192)·원본 수용 [6184675043](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6184675043) / v6 재시도 14:46 `env-unzip` rc141(`unzip -v \| head` SIGPIPE) [6185443806](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6185443806) |
| 키트 v7 제출 (1줄 수정) | [#4 6185508910](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6185508910) |
| **v7 Runtime GO** — Plan 1회, 2026-10-15 15:15~16:15 KST | [#4 6185738037](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6185738037) |
| 시작 기록 | [#4 6185850378](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6185850378) |
| 결과 보고 (HOLD, 검사기 1건 STOP) · v8 검사기 오프라인 재검사 요청 | [#4 6186026168](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6186026168) |
| 이권욱 검토에서의 c Plan / v8 취급 | [#4 6188332430](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6188332430) — "기존 c/v8 검토 수용" 유지, D3 "동일 c Plan의 기존 로컬 수용 유지" (아래 "검사" 절의 범위 참고) |

## 실행 identity

| 작업 | identity |
|---|---|
| v7 precheck (`10-h-precheck.sh`) | IAM 사용자 `arn:aws:iam::774055931866:user/321team-hayeoung`, Red Hat 하영 본인 로그인 (조직은 해시로만 결속) |
| saved Plan 수집 (`20-create-plan.sh`) | 본인 MFA 역할 `arn:aws:sts::774055931866:assumed-role/FDS-IaC-Operator/321team-hayeoung` (하위 셸 안에서만 자격증명 export — 실행자 보고) |
| 사후 state/lock 조회 | 같은 역할 ARN의 caller 기록. 새 MFA 세션·`s3api head-object` 2회만 수행했다는 범위는 실행자 보고(아래 출처 한계 참고) |

root는 쓰지 않았다.

## 고정 입력 (모두 일치 확인)

| 입력 | SHA-256 / 값 |
|---|---|
| 키트 v7 `SHA256SUMS` | `a7a3d9868bab0666614787f24838b3c53cc12e7f2399ce76b9faeb0f682c4c18` (전달 `kit.tgz` `e1e1045e454a0414ad68ded0d142f412e93ef176855f7b496157c148bf7caa01`) |
| 실행 checkout | `14-src-commit.out`의 `f1f8adf`(GitHub 해석 `f1f8adf66d3b3c9348ebb919fe0dbb4f8fa54fe2`), `15-src-tree.out`의 `terraform/rosa-runtime` tree `14e7ad41c1680e5ee8f008cf5a343d1223bb360d`; `16-src-clean.out` 출력 없음·rc 0 |
| 당시 검토 기준 main | `038c490e79f80237b43f6bb04cef34edd26bc820`. 실행 checkout과 저장소 커밋은 다르지만 실행 component tree 및 saved configuration 5개 Git blob은 승인본과 일치한다는 기존 검토를 재사용 |
| provider lock | `45e2257b205604e0fd7af33e4685c433952ff545c68727417817f8d2b302cb3d` |
| Terraform 1.16.4 linux_amd64 (`tf-zip-sum`·`tf-bin-match` rc 0) | `44d3683c2ac9d72b6ca8ad880a2df8dd956dd5e019b1d111cb6a5d914d576b73` |
| 최종 tfvars | `195f0ea7a16b1cb6fc21a1bbf4520666fc49e1d258ca27ce70777dbeae7fa72a` |
| registry CA JSON | `4d86507ecd81789e376669940f68b2dbb27f5989e6fd4315238c9f61a2401da4` |
| backend | `fds-tfstate-774055931866-ap-northeast-2` / `phase2/rosa-runtime/terraform.tfstate`, workspace `default` |

## precheck (IAM 사용자, 15:20:14~15:20:37 KST)

`rosa-create-precheck-20261015T062014Z-ubvcUP` — **`result=PASS`**, 파일 65, manifest `ae0f44eb8a90014a3675cd55ecf2f4828934d3d8e6d581ef1accf2e12d34cfe9`.
caller·`rosa whoami` 계정·조직 해시 rc 0, `4.22.17` hosted-cp 제공, `fds-rosa-hcp` 기존 cluster 없음, account role 3, operator role 승인 이름 정확히 8, OIDC config `2te9vlkhgbi43b770ni4f7nhiasie0fh`.

## saved Plan (MFA 역할, 15:21:10~15:22:20 KST)

`rosa-create-plan-20261015T062110Z-616d99` — 파일 104, manifest `6548faea4cdf8fa963b94141248d5fa19ad127bf5db58384e0caafe393c87ef0`.

| 단계 | 결과 |
|---|---|
| kit-verify·env 6(`env-unzip` rc 0)·caller | rc 0 |
| live subnet | 두 subnet·같은 VPC·az1·역할 태그·잔여 IP — OK |
| state / lock (Plan 전) | **ABSENT (404)** / **ABSENT (404)** |
| init → workspace | rc 0 / `default` |
| `terraform plan -detailed-exitcode -var-file=<tfvars> -var=execution_enabled=true -out=create.plan` | **rc 2**, `Plan: 3 to add, 0 to change, 0 to destroy.` |
| `show -json` | rc 0 |
| `create.plan` | `5a2b4471cf5c2dd3ebfbc7985803883ab6362c8462a8098bfb9da29bfdfb0c83` (13,975 B) |
| `create.plan.json` | `63383056fcbf3e48a2000f7de38e05eacf53430e92c0f8bcc01fec43a3a7d5db` (31,189 B), `terraform_version` 1.16.4, timestamp `2026-10-15T06:22:12Z` |

### Plan 내용 (JSON에서 직접 확인)

| 위치 | 내용 |
|---|---|
| `resource_changes` managed | `rhcs_cluster_rosa_hcp.this` · `rhcs_hcp_machine_pool.workers` · `rhcs_hcp_default_ingress.default` — **모두 `["create"]`**, update/delete/replace 0 |
| `resource_changes` data | 0 (Plan 때 읽은 data는 `prior_state`에 있음) |
| `prior_state` data | `data.aws_caller_identity.current`, `data.aws_subnet.rosa["private_a"]`, `data.aws_subnet.rosa["public_transport_a"]` — **정확히 3** |
| `prior_state` managed | 0 (첫 생성) |
| cluster | `fds-rosa-hcp`, `4.22.17`, `private=false`, worker m5.xlarge × 3, 300 GiB, IMDSv2 required, subnet `[public_transport_a, private_a]`, AZ `ap-northeast-2a`, machine/pod/service CIDR `10.20.0.0/16`/`10.128.0.0/14`/`172.30.0.0/16`, host prefix 23, `delete_protection=true`, admin user 없음, wait 2개 true |
| machine pool | `workers`, replicas 3, subnet private_a, `max_surge=1`/`max_unavailable=0` |
| default ingress | `listening_method=external` |

## 검사

| 검사기 | 결과 | 비고 |
|---|---|---|
| v7 `create_plan_check.py` (현장 실행) | `result=STOP checks=52 stop=1` | 유일한 STOP: `data sources: address set == approved 3 ... -- got []`. 검사기가 data를 `resource_changes`의 no-op으로 기대한 **설계 결함**이다(위 표처럼 실제 data는 `prior_state`에 있음). 실행 rc 1 → 사후 state/lock 단계는 실행되지 않음 |
| v8 `create_plan_check.py` (`SHA256SUMS` `922e955e5c92f61ab8d6c41644865dd05b6617822e3732ef1b7de727eba22be7`) | data 검사 2건을 `resource_changes`에 data 0 + `prior_state` data = 승인 3으로 수정, 검사 수 52 유지 | 작성 PC에서 같은 JSON에 v7/v8을 같은 인자로 실행: CA 원본이 작성 PC에 없어 빈 CA로 대체 → **v7 = data + CA 2 STOP, v8 = CA 1 STOP**(data 검사만 바뀜). 실제 CA 포함 52/52 판정은 이권욱 검토의 "c/v8 검토 수용"([6188332430](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6188332430))에 근거하며, **CloudShell에서 v8 재검사를 따로 실행하지는 않았다** |

v8의 52/52는 이 고정 JSON과 승인 CA에 대한 로컬 검사 결과다. `complete=false`·`checks=unknown`을 자동 차단하지 않는 기존 검사 범위 한계가 있으며, 실제 c JSON의 `complete=true`·조건 검사 6개 aggregate/instance pass는 기존 원본 리뷰에서 별도로 확인했다. 다른 Plan의 자동 수용 근거로 일반화하지 않는다.

## 사후 state/lock (15:27:15 KST, 읽기만)

v7 실행기가 검사 STOP으로 사후 단계에 가지 않아, 실행자는 GO의 "backend 도달 후 실패 시 기존 허용 읽기 범위로 잔존 state/lock 기록"에 따라 새 MFA 세션에서 따로 조회했다고 보고했다. 아래 대상 key는 그 실행 보고에 따른 연결이며, 원본 오류문 자체에는 bucket/key가 없다.

| 대상 | 결과 |
|---|---|
| `phase2/rosa-runtime/terraform.tfstate` | rc 254, **404 Not Found** |
| `phase2/rosa-runtime/terraform.tfstate.tflock` | rc 254, **404 Not Found** |
| 기록 | `rosa-create-plan-postcheck-20261015T062715Z`, manifest `c202fa1d6dcaf62f76271e41b805c3742f99c9698a93e0651793786b076d38e0` |

기존 원본 검토는 사후 묶음 9파일과 두 404/rc254를 확인했다. 다만 `.cmd`, caller RC, END ledger가 없어 정확한 bucket/key·인자와 응답의 독립 결속은 미확인이다. assumed-role ARN은 caller 근거이며 새 MFA 입력·하위 셸 인증 정리·서버 측 만료를 모두 증명하지 않는다. 실행 ledger의 고유 host 식별도 비어 있다. 이 한계를 보존하며 새로운 조회 결과로 과거 실행을 소급 입증하지 않는다.

## 비공개 원본 (팀 공유 경로, Git에 넣지 않음)

경로: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\` — 아래 해시는 **공유 경로의 파일을 직접 재해시**한 값이다(2026-10-16).

| 파일 | SHA-256 | 크기 | 내용 |
|---|---|---|---|
| `rosa-plan-evidence-20261015-c.tgz` | `b08cd6007e8279b3fbc95bb125456a6e172954bd5385945383256caadd10afeb` | 48,516 B | 위 세 실행 폴더(precheck `ae0f44eb…`, Plan `6548faea…`, postcheck `c202fa1d…`). CloudShell 원본과 공유 사본 해시 일치(보고 [6186026168](https://github.com/321Team/infra-rosa/issues/4#issuecomment-6186026168)). Plan 폴더 안에 `create.plan`·`create.plan.json`·tfvars 사본·raw 로그 |
| `rosa-create-plan-kit-20261015-v7\` | `SHA256SUMS` `a7a3d986…4c18` | — | 실행 키트 |
| `rosa-create-plan-kit-20261015-v8\` | `SHA256SUMS` `922e955e…22be7` | — | 수정 검사기 키트 |

## 넣지 않은 것과 민감정보

이 README에는 추적용 AWS 계정 ID, IAM 사용자·역할 ARN, subnet·VPC ID, OIDC config ID가 포함된다. Red Hat 조직 internal/external ID·계정 번호·이메일은 넣지 않는다(키트는 조직을 해시로만 비교).

- 수행한 검사: 이 README에 대해 Red Hat 조직 ID·계정 번호·이메일 형식 문자열 검색 0건.
- saved Plan·Plan JSON·tfvars·raw 로그와 위 비공개 묶음은 Git에 넣지 않는다. 토큰·MFA 코드는 기록하지 않았다(숨김 입력·하위 셸 — 실행자 보고). 묶음에 대한 AWS key·JWT·개인키 형식 검색 0건(제한 검사).

## 판정 범위

- 이 폴더는 **생성 Plan 수집 증적 편입**이다. 고정 c Plan의 3 create 내용 및 v8 로컬 수용은 유지한다. 원 v7 실행 결과는 STOP/rc1로 보존하며 회차 전체 PASS로 바꾸지 않는다.
- 시작 전 실제 writer·VPN/복구 작업 비중첩과 v7 창의 명시적 최종 반납은 이번에 연결한 자료로 완료를 확정하지 않는다. 사후 404의 대상 결속 한계와 함께 회차 전체 인수의 확인 필요 항목이다. 기존 c/v8 수용은 이 잔여를 해소하거나 현재 backend/자원 상태를 보증하지 않는다.
- 클러스터 생성(Apply)·Create GO·Basic Ready·#4 종결 판정은 별도다. Apply 키트 검토(v3/v3.1)와 D1(역할 세션 시간) 판단도 이 폴더 범위 밖이다.
