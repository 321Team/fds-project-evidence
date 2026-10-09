# 업무 metrics 분리 후보 — 격리 이미지 Build/Scan

CODEX_ASSISTED · 이권욱. [fds-msa#27](https://github.com/321Team/fds-msa/pull/27)의 후보 Source `aeb9995d626ffdc24454477038eb82d5d9e4744e`를 기존 GitHub hosted 워크플로로 검증했다. [workflow 원문](https://github.com/321Team/fds-msa/blob/aeb9995d626ffdc24454477038eb82d5d9e4744e/.github/workflows/apko-wolfi-py313.yml)은 base main8eac4c98와 동일하다. Source 입력과 Run head가 같다.

## 회차·출처·결과

- [Run37803786426 / attempt1](https://github.com/321Team/fds-msa/actions/runs/37803786426), job113402610076. Dispatch10/9 **00:48:35 KST**, job00:48:39~00:49:48, SUCCESS. GitHub hosted Ubuntu24.04 격리 실행이며 현장 Runner/Harbor/클러스터 접속이 없다.
- artifact11561454052, `apko-wolfi-py313-aeb9995d626ffdc24454477038eb82d5d9e4744e-1`, ZIP118,278B. API digest와 수신 ZIP SHA256 **078ad7957e68a3417d13d21909e82afcac96913ab8173671b45a81c0eddc5580** 일치. `artifact.json`의 만료10/15 15:48:36Z(10/16 00:48:36 KST) 전에 수신했다.
- 원본 manifest **50/50** 해시 일치 및 추출 파일 전체 coverage 확인. ZIP은 로컬 비공개 수신 경로에 보존하고 Git에는 원본 추출 파일을 편입한다. 이미지 tar 자체는 이 artifact에 없으며 복원 가능한 이미지 전달물로 간주하지 않는다.
- lock 기반 builder/runtime base를 각각2번 빌드해 tar byte 동일성 통과, SPDX SBOM/lock 구성원 대조 통과. **앱 이미지 자체를2번 빌드한 재현성 시험은 아니다.**
- 두 앱 모두 해당 Source의 Dockerfile로 빌드, UID:GID10001:999 및 base layer/entrypoint 대조, import 및 실제 컨테이너 `/livez`200 통과.
- Trivy0.74.0으로 실제 생성한 두 image tar의 OS/library HIGH·CRITICAL 검사: **각각0/0**. 원 report JSON에서 다시 해당 severity 행0개를 대조했다. 서명된 SLSA attestation은 NOT_RUN.

| 앱 | Image config digest (`docker inspect Id`) | Trivy H/C |
|---|---|---|
| transaction-api | `sha256:7ab7a184fa708f29b6c349498803e9ba4e47bebcccd2adedefdf679a6fdc6794` | 0/0 |
| fds-engine | `sha256:a6b616dc788c8b172af8094a06a2988e7cf75f7236c1e71dbeedd76fd74438f0` | 0/0 |

위 값은 **config digest**다. RepoDigests는 비어 있으며 Harbor remote manifest digest 또는 Pod imageID로 대체해 기록하지 않는다. 이 후보 이미지의 배포 인계·현장 재빌드/검사·Push는 별도다.

## Freshness와 시험 한계

현재 Wolfi index와 저장소 lock 사이에는 drift가 있다. 워크플로는 새 index를 임의 채택하지 않고 **저장소 lock으로 빌드**했다. `run.log`에는 `APKO_REPO_LOCKFILES_MATCH=DRIFT_NOT_BLOCKING`, `APKO_LOCK_DRIFT_AGE=WITHIN_LIMIT lock_committed=2026-10-07T06:13:51Z age_hours=33 limit_days=3`가 남아 있다. 이는 기존 기간 제한 내 이번 회차 결과이며 차기 실행의 freshness를 보증하지 않는다. 후속 공급·검사 시 같은 기준으로 다시 판정한다.

별도 [Source validation Run37802774812](https://github.com/321Team/fds-msa/actions/runs/37802774812)에서 API20·engine31개 앱 시험과 도구109개가 통과했다. 이번 이미지 workflow의 실제 기동 시험은 `/livez`만 확인하며 업무metrics404/전용metrics200의 TCP 실측, 실제 DB·Rule E2E·Pod rollout은 수행하지 않았다. ASGI 회귀와 컨테이너 기동 결과를 운영 인수로 합치지 않는다.

현재 infra-cicd config는 과거 승인 Source `adc90410` 고정이다. 새 Source와 oldRun37642123031의 이미지/승인/공급 인계를 섞지 않는다. 새 APP Source/시험 범위 인계·공급 bytes 및 consumer config 리뷰·현장 Test/Build/Scan·Robot/TokenRequest 정책·회차별 Push/Deploy GO는 별도 조건이다. 특히 기존 API contract 명령3파일은 신규 `test_listener_logging.py`1건을 포함하지 않으므로 새 Source 선택 때 시험 매핑도 반영해야 한다(후보 전체51건, 기존 명시 목록이면50건).

## 자료와 재검증

- `original/`: Actions artifact에서 추출한 bytes 그대로. 내부 `SHA256SUMS`50개, SBOM·lock·inspect·빌드/컨테이너 로그·Trivy report/summary·PROVENANCE·COVERAGE_BOUNDARY 포함.
- `run.json`, `artifact.json`, `run.log`: GitHub API 메타데이터 및 실제 job 로그. 로그 안의 실행 예정 shell echo와 실제 결과 출력은 구분해 읽는다.
- `receipt.json`, `receive_candidate.py`: 수신 시각·원 ZIP digest/크기·manifest 검사·이미지별 요약과 실행한 수신 코드. 수신기는 로컬 수신/검증이며 운영 코드가 아니다.
- 바깥 `SHA256SUMS`와 루트 대장은 이번 편입 파일을 묶는다. 안쪽 원 manifest는 그대로 보존했다. 원본50개 검증은 original 폴더 기준이며, 바깥 수신 메타데이터와 혼동하지 않는다.
- 비밀 패턴 검사(private key/GitHub token/JWT)0건. 로그에는 워크플로에 공개된 **가상 localhost 테스트 DB URL candidate:candidate**가 포함돼 있으며 운영 자격증명이 아니다. 원본을 정규화/치환하지 않았다.

독립 증적 리뷰 요청. **CANDIDATE_BUILD_SCAN=PASS / HARBOR_PUSH=NOT_EXECUTED / CLUSTER_DEPLOY=NOT_EXECUTED / DELIVERY_GATE=NOT_VERIFIED / AC=UNCHANGED**. Harbor 자동기동은 타 세션 범위이며 이 실행으로 접근하지 않았다.
