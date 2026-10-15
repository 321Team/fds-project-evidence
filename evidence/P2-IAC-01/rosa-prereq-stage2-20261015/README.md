# P2-IAC-01 — ROSA 계정 준비 A3 Stage 2 Apply (operator role 8) — 2026-10-15

출처 티켓: [infra-terraform#12](https://github.com/321Team/infra-terraform/issues/12) (P2-IAC-01 Sub-task 5/6) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35) · 앞 회차 [Stage 1 증적](../rosa-prereq-stage1-20261014/README.md)

`terraform/rosa-prereq`의 **Stage 2 saved Plan을 그대로 1회 Apply**한 회차의 기록이다. 생성 대상은 operator role 8개와 그 정책 연결 8개다. 이 폴더에는 **README와 해시만** 둔다. 실행 원본에는 state 원문과 조직 식별값이 들어 있어 팀 공유 경로에 비공개로 보관한다.

## 승인과 검토

| 항목 | 링크 |
|---|---|
| saved Plan 수집 | [#12 6161681082](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6161681082) |
| 실행 키트 v4 기술 검토(이권욱) | [#12 6164637050](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6164637050) — v2·v3 지적(B1·B2, R1·R2) 해소 |
| v4 변경분 독립 확인(이재환) | [#12 6164819513](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6164819513) |
| 10-14 작업창 GO (미사용으로 만료) | [#12 6164878057](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6164878057), 미사용 보고·재요청 [6181672488](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6181672488) |
| **실행 GO + 하영 root 위임(이번 회차 한정)** | [#12 6181760266](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6181760266) — 2026-10-15 10:00~12:00 KST |
| 시작 기록 | [#12 6182038666](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6182038666) |
| 완료 보고 | [#12 6182253342](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6182253342) |
| 실행 증적 독립 검토(이권욱) | [#12 6182426340](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6182426340) — **결과 수용**(명시된 범위 한정) |

## 실행 identity (사실대로)

| 작업 | identity |
|---|---|
| 사전 점검 `29`, drift 조회, Terraform init/apply/readback/검증 Plan(`30`) | 교육장 root `arn:aws:iam::774055931866:root`, 실제 실행자 **이하영** (6181760266 위임) |
| ROSA CLI postcheck(`h-s2-post.sh`) | IAM 사용자 `arn:aws:iam::774055931866:user/321team-hayeoung`, Red Hat 하영 본인 로그인 |

- ROSA CLI 1.2.53은 root를 거부하므로(Stage 1 회차에서 확인) ROSA 확인은 IAM 사용자로 나눴다.
- root 로그아웃 약 10:19 KST — **실행자 보고**. 별도 logout audit는 이 묶음에 없다.

## 고정 입력 (모두 일치 확인)

| 입력 | SHA-256 / 값 |
|---|---|
| source | infra-terraform `f1f8adf66d3b3c9348ebb919fe0dbb4f8fa54fe2`의 `terraform/rosa-prereq` (checker는 main `038c490` 병합본 — 역할 구분) |
| saved Plan `stage2.plan` | `0c230a8713085c20f23f9487c2a005af534c57b5ea95ca3dc20b59ab9fd2b57a` |
| `stage2.plan.json` (검토본 = 현장 `show -json`) | `d39ad430e372dd7ef86a57bdbbb5c9309c284e7235f51789e7b3e6d9a776fe20` |
| provider lock | `45e2257b205604e0fd7af33e4685c433952ff545c68727417817f8d2b302cb3d` (AWS 6.66.0, rhcs 1.7.9) |
| Terraform 1.16.4 linux_amd64 | `44d3683c2ac9d72b6ca8ad880a2df8dd956dd5e019b1d111cb6a5d914d576b73` |
| 실행 묶음 `s2-run-20261014-v4.tgz` | `fd2abf1e2f3c1ddb291cadb94c806401d84695754dcc58e449a1b21001925f93` |
| `29-s2-pre.sh` / `30-s2-apply.sh` / `h-s2-post.sh` | `29728b3ff07b1a7a36e604f5b367fef38378fec95fb9998dddb6a2e2e2660d9b` / `3d7028a9d9d9e74dc2ce0429ab6bf368010a06ec433545feea5578f2cd760c77` / `1975288be60f68438e47f635d5802ee6868f31e42d3aaa192223200c6f61a2b5` |
| 키트 MANIFEST / v4 SHA256SUMS | `dfcf53dc190372486856748abe98597417bee0854b36f097374a423f0110f99b` / `a3674ed47b620998765649357d7e8750473566ee96e90992ae84e7854a64e48b` |
| `~/a3ocm/common.sh` (Stage 1 회차 검토본 재사용) | `a27b631d325721a7fcdcc406b4dcfb97af0b615b88b1385303435ed5fb6e156c` |

## 직전 상태 (10:00~10:04 KST, 읽기 전용)

| 항목 | 결과 |
|---|---|
| `29-s2-pre.sh` | **PASS** 10:00:41~10:02:34, pre manifest `e50c95d1090ae8d44faa6b275c9b92a3294a3d84fd70475ac823d1c17151b703` |
| backend | workspace `default`, state `phase2/rosa-prereq/terraform.tfstate` VersionId `N50QJIh0cdFrQvDWFonJJMzFyBYOEJBy`, lineage `881599c2-fdcb-a84f-8954-328c6b33bdf6`, serial 1, managed 9, lock ABSENT |
| IAM | operator role 8 ABSENT(NoSuchEntity), account role 3·OCM role/policy EXISTS, `oidc.op1` provider 1, AWS 관리 정책 기본 버전 v10/v6/v6/v3 |
| drift 원문 (GO 3·4항) | `drift-20261015T010342Z` manifest `dec709126243cee9f8cd29ef41b274dfc3d4f2542778dba2b8efa61851cb89af`. checker `readback --stage 1` PASS 17/17. OCM 정책 문서 = 승인본, OCM trust는 1개짜리 배열↔문자열 표기 정규화 후 ExternalId 포함 동일 |
| 비중첩 | 10:00 하영 확인 — 재환 O01(오프라인 판독)만 진행, 다른 AWS/IAM/backend writer·부하 시험 없음(실행자 확인, 검토자 실측 아님) |

정정 기록: drift 조회의 첫 ExternalId 단독 비교는 jq 문법 오류로 양쪽이 빈 값이 되어 `YES`를 출력했다. 이 결과는 무효로 처리했고 근거로 쓰지 않는다.

## A3 Stage 2 Apply

| 항목 | 결과 |
|---|---|
| 명령 | `terraform apply -input=false -no-color -lock-timeout=60s <stage2.plan>` **1회** (추가 `-var`·`-target`·`-lock=false` 없음) |
| 시각·RC | 10:12:08~10:12:15 KST, `apply rc=0 (pipeline 0 0 0)`, **16 added, 0 changed, 0 destroyed** |
| 판정 줄 | `apply=0 readback=0 extra_mismatch=0 evidence_bad=0 verify_plan=0`, `30` 최종 rc 0 (10:13:42) |
| state 후 | VersionId `PPT5FG.G_F2f7R15BmmeLR_DtuCCP_zt`, lineage 동일, serial **2**, state list 25 (saved Plan 전체 25 주소와 일치 — 검토자 대조) |
| lock | apply 전·후, 검증 Plan 후 모두 ABSENT |

### 생성된 operator role (prefix `fds-rosa-`)

| 역할 | RoleId |
|---|---|
| openshift-ingress-operator-cloud-credentials | `AROA3IOKUF7NPNHSJRMMU` |
| openshift-cluster-csi-drivers-ebs-cloud-credentials | `AROA3IOKUF7NADIUMZUYB` |
| openshift-cloud-network-config-controller-cloud-credent | `AROA3IOKUF7NJMMC5UBEI` |
| openshift-image-registry-installer-cloud-credentials | `AROA3IOKUF7NNXY4S3UQV` |
| kube-system-kube-controller-manager | `AROA3IOKUF7NA3ZVFNFRT` |
| kube-system-capa-controller-manager | `AROA3IOKUF7NGSHYQ7RNK` |
| kube-system-control-plane-operator | `AROA3IOKUF7NFMRINZV27` |
| kube-system-kms-provider | `AROA3IOKUF7NO2N6KQUC2` |

## 사후 검증

| 검증 | 결과 | 묶음 안 형태 |
|---|---|---|
| `rosa_prereq_check.py readback --stage 2 --oidc-host oidc.op1.openshiftapps.com/2te9vlkhgbi43b770ni4f7nhiasie0fh` | **PASS 48/48** (account 3 + operator 8 trust·boundary 없음·attachment·inline 0, OIDC url·client ID) | `readback.txt` |
| 역할 API 원문 | 8개 × get-role/list-attached/list-inline 모두 rc 0, path `/`, max session 3600, 정책 1개씩, inline `[]`, `Project=fds-hybrid`·`ManagedBy=terraform` | `role-readback/` 48개 (`.json`·`.stderr`) |
| 검증용 Plan (`-detailed-exitcode`, `create_operator_roles=true`) | rc 0, **No changes** | `verify-plan.txt` |
| ROSA CLI postcheck (10:19:36~10:21:37, IAM user) | `rosa list operator-roles --prefix fds-rosa` rc 0, **8/8**. `rosa list oidc-config`에 `2te9vlkhgbi43b770ni4f7nhiasie0fh` → postcheck PASS | post 묶음 |
| 정리 | `private.tfvars`·`/tmp/a3ocm-ocm.json` 없음, `RHCS_TOKEN` 해제, TF 임시 디렉터리 삭제(10:18:34) | ledger (실행자 보고) |

## 비공개 원본 (팀 공유 경로, Git에 넣지 않음)

경로: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\` — 아래 해시는 **공유 경로에 있는 파일을 직접 재해시**한 값이다(2026-10-15).

| 파일 | SHA-256 | 크기 | 내용 |
|---|---|---|---|
| `s2-apply-result-20261015T011655Z.tgz` | `a59ccac0f0687f43d2b6f8821afabb6a5ab629f2c4dfbb238b64697274d0c791` | 38,835 B | root `~/a3ocm/s2`(Plan 묶음 제외): ledger, init/apply/readback/verify 로그, outputs, state-list, role-readback 48, `RESULT-SHA256SUMS`(`531eaa6e…3889`, 55/55), `pre-…/`(manifest `e50c95d1…b703`), `drift-…/`(manifest `dec70912…89af`), OCM trust 비교 원문 2 |
| `s2-post-a3-s2-h-20261015-011936.tgz` | `bfb2a398b8470778d75b028e02b3262aaa63588e0c1492d62dad6588f6991424` | 1,159 B | IAM user postcheck ledger·operator-roles·oidc-config, 내부 `SHA256SUMS` `c7220495b8f593d55f0ee6d3638c3bce8d95b1021f9f2dc781e2706842456ded` (3/3) |
| `s2-run-20261014-v4.tgz` | `fd2abf1e2f3c1ddb291cadb94c806401d84695754dcc58e449a1b21001925f93` | — | 실행 입력(29·30·MANIFEST·checker·Plan tgz·post) |

- `RESULT-SHA256SUMS` 55개는 결과 묶음의 모든 파일을 덮지 않는다. pre·drift는 각자의 manifest, 스크립트·비교 메모는 바깥 묶음 해시와 승인 사본 대조로 고정한다(6182426340 1항).
- root CloudShell 홈에 남은 첫 압축본 `s2-apply-result-20261015T011550Z.tgz`(116,996 B, tar 옵션 순서 오류로 생성, Plan 묶음 포함)는 **비정본**이다. 공유 경로에 두지 않았고 전달·인수 근거로 쓰지 않는다. 다음 적법한 유지보수 기회에 그 파일만 정리한다.

## 넣지 않은 것과 민감정보

이 README에는 추적용 AWS 계정 ID, IAM 사용자·역할 ARN, RoleId, state VersionId·lineage가 포함된다. Red Hat 조직 internal/external ID, 지원 역할 principal의 조직 식별 부분과 이메일은 공개 기록에서 제외하며 원본은 승인된 비공개 공유 경로로만 보관한다. 자격증명·토큰·MFA 코드는 기록하지 않는다.

- 수행한 검사: 이 README에 대해 Red Hat 조직 internal/external ID, Red Hat 계정 번호·사용자명, 이메일, 지원 역할 principal 숫자의 문자열 검색 0건.
- Plan 바이너리·Plan JSON·state 원문·apply 로그·tfvars와 위 비공개 묶음은 Git에 넣지 않는다. 묶음에 토큰이 없다는 것은 실행 스크립트 설계(숨김 입력, EXIT 정리)에 따른 **실행자 보고**다.

## 판정 범위

- 독립 검토 [6182426340](https://github.com/321Team/infra-terraform/issues/12#issuecomment-6182426340): **Stage 2 IAM 실행 결과 수용**(역할 8/8 Plan 일치, manifest 55·85·32·3 PASS). 사용자 identity·본인 Red Hat 로그인과 root 로그아웃은 실행자 보고와 검토된 guard에 근거한다.
- #12 완료 조건 "account/operator role·OIDC readback" 중 **operator role 부분**에 해당한다(account role·OIDC는 Stage 1 폴더).
- 이 폴더는 증적 편입이며 AC-3 전체·G4 전체·#12 종결 판정은 별도다. ROSA 클러스터 생성(infra-rosa#4)은 범위 밖이다.
