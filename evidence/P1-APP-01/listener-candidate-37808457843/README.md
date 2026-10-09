# 후보 컨테이너 업무·metrics listener TCP 분리 검사

CODEX_ASSISTED · 이권욱. [fds-msa#27](https://github.com/321Team/fds-msa/pull/27) 새 Source **affbc69beef9967f7977d09a6fec14f7fb6c0e94**의 격리 CI 결과다. [이전 증적#176](https://github.com/321Team/fds-project-evidence/pull/176)은 aeb9995의 livez-only 회차로 보존하며 새 Source/검사 결과로 소급하지 않는다.

## 회차와 실측

- [후보 Run37808457843 / attempt1](https://github.com/321Team/fds-msa/actions/runs/37808457843), job113418812497: 2026-10-09 01:23:53 KST dispatch, job01:23:57~01:25:07 SUCCESS. GitHub hosted Ubuntu24.04, 앱 컨테이너 `--network none`, 정상 entrypoint와 /venv/bin/python3 사용.
- transaction-api 검사01:24:37.848~37.858 KST, fds-engine01:24:51.342~51.350 KST. 컨테이너 안에서 loopback TCP HTTP 요청 **각8개/총16개**, 재시도 없이 첫 응답으로 완료했다.

| 앱 | 업무 livez | 전용 metrics | 업무 metrics GET/HEAD |
|---|---|---|---|
| transaction-api | 8000 `/livez`200 | 9091 `/metrics`200, transaction_save_success_total counter 확인 | 8000 `/metrics`, `/metrics/`, `/%6detrics` 각 GET·HEAD **6/6 404**, Location 없음 |
| fds-engine | 8001 `/livez`200 | 9090 `/metrics`200, fds_evaluated_total counter 확인 | 8001 같은3경로 GET·HEAD **6/6 404**, Location 없음 |

전용 응답은 Prometheus text/plain이었다. JSON에는 실제 응답 상태·길이·본문 SHA256을 기록하고 본문은 넣지 않았다. Counter 존재 확인이며 실제 업무 처리에 따른 증가를 TCP로 검증한 것은 아니다.

- 두 앱 Trivy HIGH/CRITICAL **각각0/0**, UID:GID10001:999. 각 base(builder/runtime) 두 번 빌드 tar 동일, SPDX/lock 구성원 대조 PASS. 앱 이미지 자체를2번 빌드한 재현성 시험은 아니다.
- [Source validation Run37808461629](https://github.com/321Team/fds-msa/actions/runs/37808461629)도 같은 HEAD SUCCESS: API20+engine31, 도구115(신규 listener 검사기 회귀6 포함). 검사기 회귀는 로컬 HTTP fixture이며 실제 앱 컨테이너 결과와 구분한다. 기존 Starlette/httpx warning 각1건은 로그에 보존한다.

| 앱 | image config digest (`docker inspect Id`) |
|---|---|
| transaction-api | `sha256:510de009c1ca9ca69e568b33464a8c3336c46e0ec9d8ebff5e1998b9feb865ba` |
| fds-engine | `sha256:601e60dacb22e488e259f54d98491b319fc04672e7e80bd614f776f998351d8e` |

RepoDigests는 비어 있다. 위 값을 Harbor manifest digest나 Pod imageID로 쓰지 않는다. artifact에는 image tar가 없어 배포 가능한 공급 번들로 대체할 수 없다.

## 원본 결속

- artifact11563449559, `apko-wolfi-py313-affbc69beef9967f7977d09a6fec14f7fb6c0e94-1`, ZIP121,877B, API digest=수신 ZIP SHA256 **da6243a90c7975702a844f5a1bb79d3e58389f597dd5da5696ba3b7cdfdf7af6**. 01:26:03 KST 수신.
- 원본 manifest **53/53** 해시 및 전체 파일 coverage 일치. `original/`는 추출 bytes 그대로이며 이번 추가 원본은 검사기1개와 앱별 listener JSON2개다. 실행 검사기 bytes와 Git affbc69 blob을 추가 대조했다. ZIP은 로컬 비공개 수신 경로에 보존한다.
- `run.json`, `artifact.json`, `run.log`, `source-validation.json/log`, `receipt.json`, 실제 수신 코드와 외부 SHA256SUMS/루트 대장을 연결한다. Source validation 로그는 gh 원문 별도 수신이며 Actions artifact 내부 파일 수에 합치지 않는다.
- 로그의 candidate:candidate localhost DB URL은 workflow에 공개된 가상 fixture다. 운영 credential을 사용하지 않았다. private-key/GitHub-token/JWT 패턴 검사0건. 원본은 치환·정규화하지 않는다.

## 범위와 다음 단계

Wolfi index drift는 이번에 **34시간/한도3일**로 통과했다. 차기 공급/현장 실행은 최신 freshness로 다시 판단한다. 서명된 SLSA attestation NOT_RUN.

이번 결과는 새 Source의 **CI 컨테이너 loopback listener 분리**다. 운영 Service/NodePort/NetworkPolicy·전체 replica·DB readiness·실제 거래/Rule E2E·Prometheus 수집은 검증하지 않았다. 운영 배포 전에는 APP Source·시험 범위 인계, 새 offline 공급 bytes/consumer config 리뷰, 현장 Test/Build/Scan, Robot/TokenRequest 정책과 해당 회차 Push/Deploy GO가 별도로 필요하다. 기존 adc90410 인계나 만료된 승인을 재사용하지 않는다.

**CANDIDATE_TCP_ISOLATION=PASS / CLUSTER_ISOLATION=NOT_RUN / HARBOR_PUSH=NOT_EXECUTED / DEPLOY=NOT_EXECUTED / AC=UNCHANGED.** Harbor 자동기동은 타 세션 범위다. PR 발행과 독립 리뷰·병합을 구분하며 리뷰 회수는 사용자 요청대로 작업창 종료 후다.
