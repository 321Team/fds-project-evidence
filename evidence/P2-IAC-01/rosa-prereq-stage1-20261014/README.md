# P2-IAC-01 — ROSA 계정 준비 A3 Stage 1 Apply + OCM basic — 2026-10-14

출처 티켓: [infra-terraform#12](https://github.com/321Team/infra-terraform/issues/12) (P2-IAC-01 Sub-task 5/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

`terraform/rosa-prereq` **Stage 1 saved Plan을 그대로 1회 Apply**한 회차와, 같은 작업창에서 한 **OCM basic role 생성·연결** 기록이다. 이 폴더에는 **README와 해시만** 둔다. 실행 원본은 조직 식별값이 섞여 있어 팀 공유 경로에 비공개로 보관한다.

## 승인과 작업창

| 항목 | 링크 |
|---|---|
| Stage 1 saved Plan 독립 검토·Apply GO | [#12 6144038031](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6144038031) (10-13 20:00~21:00 창은 미실행으로 경과) |
| OCM basic 고정 원본·GO | [#12 6121083000](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6121083000) |
| 하영 root 단독 실행 위임 (이번 회차 한정) | [#12 6158731670](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6158731670) — 2026-10-14 10:19~12:19 KST |
| 시작 기록 | [#12 6159231628](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6159231628) |
| 완료 기록 | [#12 6159813407](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6159813407) |
| 원본 반출 기록 | [#12 6159881966](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6159881966) |

## 실행 identity (사실대로)

| 작업 | identity |
|---|---|
| AWS IAM 쓰기(OCM manual 1~3), Terraform init/apply/readback/검증 Plan | 교육장 root `arn:aws:iam::774055931866:root`, 실제 실행자 **이하영** (6158731670 위임) |
| ROSA CLI(Red Hat 조직 확인, `rosa link ocm-role`, `rosa list`) | IAM 사용자 `arn:aws:iam::774055931866:user/321team-hayeoung` |
| Red Hat 인증 | 하영 본인 SSO(device code). 토큰 전달·공유 없음 |

- 10:46 KST root에서 `rosa whoami`가 `ERR: Failed to create AWS client: using a root account is not supported, please use an IAM user instead`로 거부되어 위처럼 나눴다. root에서 생긴 rosa 토큰 파일(`/tmp`)은 바로 삭제했다.
- root 로그아웃 11:54 KST(하영 확인). 원본 반출을 위해 root에 다시 들어가 묶기·내려받기만 하고 로그아웃했다(쓰기 없음).

## 고정 입력 (모두 일치 확인)

| 입력 | SHA-256 / 값 |
|---|---|
| source | infra-terraform main `f1f8adf66d3b3c9348ebb919fe0dbb4f8fa54fe2` |
| saved Plan `stage1.plan` | `b6a7184419f7fd3842c0c4e071f68ce05b9619e59d9189d04defc79b8b2d645f` |
| `stage1.plan.json` | `416d4da52e642a608ae43ada0367ea9ae366a53a3818570aa3b5e9489342e421` |
| provider lock | `45e2257b205604e0fd7af33e4685c433952ff545c68727417817f8d2b302cb3d` (AWS 6.66.0, rhcs 1.7.9) |
| Terraform 1.16.4 linux_amd64 바이너리 | `44d3683c2ac9d72b6ca8ad880a2df8dd956dd5e019b1d111cb6a5d914d576b73` |
| ROSA CLI 1.2.53 바이너리 | `a3a57d6adb9a39f7ec8363951999cecde98aa403675c52ef7d7e74e169e7a9e1` |
| OCM trust / permission / manual | `41e99182ef6930049d244ae8ccb652236ced03db55268f0d22bfb0e787e854e2` / `15e869f12307c26bf1f3e9fec20971c99fb655368764be367026677d743acea9` / `386d49677b7fe6039008683c9f6090a2b984f2e550a53c9d258d79bf6c79d31f` |

## 직전 상태 (11:01 KST)

state `phase2/rosa-prereq/terraform.tfstate` ABSENT, `.tflock` ABSENT, account role 3·OCM role·OCM policy ABSENT, `oidc.op1` provider 0. Red Hat 로그인 조직 = 승인 OCM role 이름·trust ExternalId(조직 값 비공개 대조). AWS 관리 정책 기본 버전: ROSAInstallerPolicy v10, ROSASRESupportPolicy v6, ROSAWorkerInstancePolicy v6, AmazonEC2ContainerRegistryReadOnly v3.

## OCM basic — 생성 3 + 연결 1

| 단계 | KST | 결과 |
|---|---|---|
| manual 1 `create-role` (root) | 11:03:11 | rc 0, RoleId `AROA3IOKUF7NGZ4EGW3E7` |
| readback | 11:03:13 | STOP — 글자 그대로 비교. diff는 `Action`·`Principal.AWS`의 1개짜리 배열 ↔ 문자열 표기뿐(ExternalId 조건 포함 동일) |
| 정규화 재확인 + manual 2 `create-policy` (root) | 11:05:26~29 | 역할 재생성 없음, 같은 RoleId, trust == 승인(정규화 구조 비교, 6121083000 4항). 정책 PolicyId `ANPA3IOKUF7NKCB7PU5IC` v1, 문서 == 승인(정규화), 조회 동작 10 |
| manual 3 `attach-role-policy` (root) | 11:05:33~38 | rc 0, attached 1·inline 0·boundary 없음 |
| manual 4 `rosa link ocm-role` (IAM user) | 11:48:12 | rc 0, `rosa list ocm-role` **Linked Yes / Admin No** |

## A3 Stage 1 Apply

| 항목 | 결과 |
|---|---|
| 명령 | `terraform apply -input=false -lock-timeout=60s <stage1.plan>` 1회 (추가 `-var`·`-target`·`-lock=false` 없음) |
| 시각·RC | 11:49:50~11:50:00 KST, rc 0, **9 added, 0 changed, 0 destroyed** |
| account role | Installer `AROA3IOKUF7NNR363U7AX`, Support `AROA3IOKUF7NIANZCXJOW`, Worker `AROA3IOKUF7NPK4ZO7U4Z` — path `/`, max session 3600, `Project=fds-hybrid`·`ManagedBy=terraform`, `rosa_role_type` 정상 |
| managed OIDC config | `2te9vlkhgbi43b770ni4f7nhiasie0fh`, managed=true |
| IAM OIDC provider | `arn:aws:iam::774055931866:oidc-provider/oidc.op1.openshiftapps.com/2te9vlkhgbi43b770ni4f7nhiasie0fh`, client ID `openshift`·`sts.amazonaws.com`, thumbprint `06b25927c42a721631c1efd9431e648fa62e1e39` |
| state 후 | VersionId `N50QJIh0cdFrQvDWFonJJMzFyBYOEJBy`, 14,533 B, lineage `881599c2-fdcb-a84f-8954-328c6b33bdf6`, serial 1, lock ABSENT |

## 사후 검증

| 검증 | 결과 |
|---|---|
| `rosa_prereq_check.py readback --stage 1 --oidc-host oidc.op1.openshiftapps.com/2te9…` | **PASS 16/16** (trust 3 == 승인, attachment 1/1/2, inline 0, boundary 없음, provider url·client ID) |
| 대조기 밖 항목(API 원본) | RHCS config endpoint = IAM provider Url = oidc host, thumbprint 일치, 역할 path·max session·태그 확인 |
| ROSA CLI (11:51, IAM user) | `rosa list oidc-config`에 config ID 있음, `rosa list account-roles` Installer/Support/Worker(4.22) 인식 |
| 검증용 Plan (`-detailed-exitcode`, stage1 스위치) | rc 0, **No changes** |
| DEFERRED 7 (provider url + 역할별 inline·managed_policy_arns) | 위 readback으로 확인 |

## 비공개 원본 (팀 공유 경로, Git에 넣지 않음)

경로: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\` — 아래 해시는 **공유 경로에 있는 파일을 직접 재해시**한 값이다(2026-10-14).

| 파일 | SHA-256 | 크기 | 내용 |
|---|---|---|---|
| `a3ocm-evidence-20261014.tgz` | `9ff7157c591c176c0d0d5cdd9ed5faaafc7b050fa614be30f0dba879f43ef00f` | 8,074 B | root `~/a3ocm/`: ledger.txt, a3-init/apply.log, a3-readback.txt, a3-outputs.json, a3-state-list.txt, a3-verify-plan.txt, ocm-block1~3.out, RESULT-SHA256SUMS + 10-12/13 Subscribe ledger 폴더 |
| `a3ocm-h-evidence-20261014.tgz` | `96f689e68749e5141cdbe38427f8591e644d0e44453fda6d08b4c8d8e6b9321b` | 907 B | IAM user `~/a3ocm-h-20261014/ledger.txt` |
| `a3-1-plan-20261013-103122.tgz` | `a5350476112fe1feee13951e5a61ca391bad35d9b86ff64206e3d7197e595368` | 13,968 B | Stage 1 saved Plan 원본(입력) |
| `fds-rosa-prereq-check-20261009.tgz` | `d35ac44e9d2cdb97389a7b35392d674d4786edbe47b4075be1bdd7498ca0d467` | 4,251 B | ROSA CLI manual 원본(입력) |

- `a3ocm-evidence` 안의 `RESULT-SHA256SUMS` 9개 중 8개 일치. `ledger.txt`만 다르다 — 실행 스크립트가 지문표를 만든 뒤 마지막 줄(`== 20-a3 done …`)을 ledger에 한 줄 더 썼기 때문이며, 반출본 ledger의 마지막 줄이 그 줄이다. 반출 묶음 해시로 고정한다.
- 묶음의 CloudShell 쪽 해시는 기록하지 않았다(NOT_VERIFIED). 공유 경로 사본 해시가 기준이다.

## 넣지 않은 것과 민감정보

- Plan 바이너리·Plan JSON·state·apply 로그·tfvars: Red Hat 조직 External ID(지원 역할 principal)가 들어 있어 Git에 넣지 않는다.
- Red Hat 조직 ID·계정 번호·사용자명·이메일, Red Hat 토큰, MFA 코드: 이 문서와 원본 어디에도 공개하지 않는다(토큰·MFA는 원본에도 기록되지 않음).

## 판정 범위

- 이 폴더는 실행자 기록이다. **실행 증적의 최종 독립 검토는 실행자 외(이권욱 또는 이재환)**가 공유 경로 원본으로 한다.
- Stage 2(operator role 8)는 범위 밖이다. manual 대조 PASS와 Plan GO 요청: [#12 6159931902](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6159931902).
- #12 완료 조건 "account/operator role·OIDC readback" 중 **account role·OIDC 부분**에 해당한다.
