## AC05 종료 후 D-03 준비 완료·이번 회차 실행안 — 2026-10-14 20:57 KST

CODEX_ASSISTED · 수행/작성 이권욱. **준비·Runner helper 점검 완료. 이미지 공급 및 실제 D-03 Runtime은 미실행이며 아래 범위는 결정 대기다.**

### 종료 조건과 실제 수행

- 사용자 “ac 05 종료됨”을 수신했다. [AC05 종료 기록](https://github.com/321Team/fds-project-baseline/issues/16#issuecomment-6166968029)과 [증적 PR229](https://github.com/321Team/fds-project-evidence/pull/229)의 원본 회수·20:00:56 KST 공유 창 해제를 확인했다. AC05 증적 편입/최종 인수 대기와 D03 착수 선행조건을 구분한다.
- 고정 코드: [PR34](https://github.com/321Team/fds-msa/pull/34), merge `192c5ab04a5e7469dcb45d19d620d3b71b33f72d`, 독립 승인 HEAD `4e32e71d08c9510461cc5d4774968f53af814bbb`. [독립 승인](https://github.com/321Team/fds-msa/pull/34#pullrequestreview-5514692752)·[CI](https://github.com/321Team/fds-msa/actions/runs/38530506527) 유지. 코드 변경 없음.
- 20:53 KST Runner 직접 조회: cicd-runner01/UID1000/x86_64, Podman6.1.0/rootless=true, Worker0·컨테이너0, 포트18081 미사용, MemAvailable8,870MiB·home 가용40.5GiB. 이 관측은 향후 전용 예약을 대신하지 않는다.
- 20:54 KST `/home/server01_cicd-runner/FDS_D03_Preparation_192c5ab04a5e` 새 경로에 번들 배치. archive SHA256 `29b378e5b1ddfaefcd15bfa6f2d9dd65fdf54d6474418a59210ff043530197e5`, 파일19개/manifest18개·원본source10개 해시 대조 완료.
- 동일 번들에서 staging CLI `_probe`와 실제 loopback helper GET/POST selftest **2 PASS/rc0**. `/home/server01_cicd-runner/FDS_D03_Precheck.ezn5ka16` 원본10파일 회수·해시 일치. 전후 Worker0/컨테이너0/포트미사용 확인. 앱·DB 컨테이너 시험 결과가 아니다.
- 기존 앱 OCI2개 SHA 일치. 20:56 KST 공개 registry 메타데이터 재조회 TLS 검증/익명 rc0: 고정 DB index/config SHA 동일. 이미지 계층 다운로드·load/pull·컨테이너·실제 RUN claim은 아직0.

### 이번에 확정할 범위

1. **회차** `RUN=202610142110`, 실제 Runtime 시작 **10/14 21:10~21:20 KST**, 증적 수집·정리 종료 **21:40 KST**. 승인 후 공급·사전검사를 진행하며 21:20까지 준비 미완료/전용 사용 미확보/형상 불일치면 Runtime을 실행하지 않는다. 자동 재실행 없음.
2. **Runner 전용 사용**: 승인 후 공급 시작부터21:40까지 cicd-runner01의 다른 CI/Podman 작업과 비중첩. 직전 GitHub busy=false·Worker0·컨테이너0·자원/입력 재확인. 공유 Runner 서비스/권한을 임의 변경하지 않는다.
3. **공급**: 기존 transaction-api·fds-engine OCI 각1회 load와 아래 고정 DB digest1회 TLS pull. 새 build/scan, Harbor Push/Deploy, Robot Secret 등록·소비 없음. 공급 명령별 rc/원본 보존, 실패·응답 불명 시 후속 중단하며 자동 재시도하지 않는다. 이미 존재하면 정확 ID/digest 일치부터 확인하고 중복 공급하지 않는다.
4. **DB 시험 사용 판단**: `quay.io/sclorg/postgresql-16-c9s@sha256:d33717fd33c1a4b11afef94568d0c20812a19d62fb8c633fadee1e491e2edd4a`의 커뮤니티 PostgreSQL16.8을 이번 격리 실패 처리 계약 검증에 사용. 운영 db01은16.14이며 차이를 보존한다. 이번 DB의 새 취약점 스캔은 미수행이다. 메타데이터/코드 리뷰를 스캔 통과 또는 전체 P1 예외 승인으로 확대하지 않는다.
5. **Runtime 최대1회**: rootless 임시 DB/API/engine/fixture4개, 외부 네트워크/host 공개포트 없음, 최대7 POST/DB6행, READ timeout·HTTP500·DB INSERT 실패 뒤 동일 PID ROLLBACK·정상 회복 검증. 승인 코드의 memory/CPU/pids/수명900초 제한 유지.
6. **중단·정리**: 첫 예상외 결과에서 남은 POST 중단. 이 RUN의 정확 CID+라벨에 일치하는 컨테이너·임시 인증파일만 회수하고 임시 DB 데이터는 증적 수집 뒤 소멸. claim/원본/cache는 보존. 전체 prune·기존 image 삭제·운영 DB/클러스터 설정 변경 없음. DB ROLLBACK 미관측 판정은 해당 POST 이후 발생할 수 있어 이미 수행한 요청은 그대로 기록한다. 정리 실패 시 정확 잔존 객체를 인계하고 재실행하지 않는다.

### 고정 plan

병합된 번들에서 오프라인 `plan --run 202610142110`을 생성하고, 기존 고정 입력의7개 파일 SHA·이미지·케이스·상한과 전수 대조했다.

- plan SHA256: **`3f2038b9d90fecf727e24f901703df88d7b5b4f8d9bb2005a2b68aa5f660addf`**
- 앱 Source: `affbc69beef9967f7977d09a6fec14f7fb6c0e94`
- API config ID: `sha256:ab34196baf2b878222857be47b200baed0151679a5b19fe15635ba50f77bffee`
- engine config ID: `sha256:b82d35a60e7a7f4a30366a926699fa4b673e69610f64fa0e7f294673ed12f4fc`
- 공급 archive SHA: API `ff3d145047f53b67f44b8a91994d7ab2b72998d9b276184b3c70a2148d52e3cf`, engine `319ab0af288d32a156feb1867193d3b7be0e663f2a17ee3efaa95aa505cd7031`.
- `authorization.pending.json`의 approved/runner_exclusive/lab_db_image_accepted는 모두false다. 사용자 실제 결정이 도착한 경우에만 해당 원문과 이 실행안을 연결해 승인 입력을 별도로 만든다.

근거: [병합된 실행카드의 실행 순서와 진입 조건](https://github.com/321Team/fds-msa/blob/192c5ab04a5e7469dcb45d19d620d3b71b33f72d/docs/p1-d03-isolated-failure-readiness-20261014.md#실행-순서와-진입-조건). 카드에서 새 RUN·시간창·격리 DB 사용/공급·Runner 전용 사용을 별도로 확정하도록 했으므로 AC05 종료 또는 코드 병합만으로 이를 확정하지 않는다.

성공 후에도 격리 Runtime 원본의 독립 증적 리뷰·편입과 D03 처분/APP·E2E 인수는 별도다. `production_runtime_claim=false`, #20 OPEN 유지.
