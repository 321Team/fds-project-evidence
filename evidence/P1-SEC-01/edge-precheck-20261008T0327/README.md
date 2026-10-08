# Edge C0 사전검증 — 2026-10-08 03:27~03:28 KST

RUN 20261008T0327 / tag check032801. 사용자 직접 SSH/sudo 입력 뒤 수정된 인증 분리 wrapper로 실행. 본 회차는 설정 변경·reload·POST 없음. 이전 평문 표시 신고 회차 zodp0ww2는 일절 회수/편입하지 않았다.

## 실제 판정

- DB: 03:27:48 KST, postgres/fdsdb/read-only=on, 거래 확인 컬럼3 조회 가능, WHERE false로 업무 행 반환0. 결과 rc0. 실제 시험 거래 검증은 아직 아니다.
- control pre:03:27:49~53, endpoint1/1/1·ETP Local·30080 .50/32 Allow·32085없음·MON23/23/EMPTY·조회오류0.
- edge check:03:28:01~05, nginx-t 정상, 현재/Worker 경로200,metrics404,k3s active. 한국어 ps 날짜 해석 실패로 reload 판정rc2. E-K3S err0/found0→TRACE_NOT_READY.
- control trace:03:28:05, Pod3 로그 조회rc0이나 모두0바이트, TRACE_NOT_READY. wrapper HANDOFF_RC=3으로 중단. 암호 재입력이나 동일 check 자동 재시도 없음.

## 원인 대조·수정

1. 실제 edge01의 일반 계정 읽기 조회에서 LC_ALL=C ps/date 변환rc0, worker PID1604 epoch1791248678 확인. 전체 reload 판정이나 실제 새 스크립트 성공으로 확대하지 않는다.
2. Kubernetes Pod3에서 기간 제한 없는 tail8 조회도0바이트. Worker01 실제 CRI 로그0바이트 및 실행 컨테이너 /app/run.py SHA b8370b635058228c7ec2ef6533a428e920c1791c9d10af3126d8ead1ca27db14 확인. 두 번째 Uvicorn metrics Config warning이 공용 INFO 접근 로그를 억제한다. 설치 Uvicorn configure_logging 원문도 대조했다. E-K3S 내부 source는 미회수이므로 같은 원인이라고 단정하지 않는다.
3. 처음 시도한 /venv/bin/python3 기반 Pod exec3건은 rc1이며 원인 stderr는 이 진단 JSON에 보존하지 못했다. 이후 Worker01 CRI/컨테이너 파일 읽기로 source를 확인했다. 이 실패를 성공 조회로 합산하지 않는다.
4. infra-kubernetes#73 HEAD edc495ecb2cf3bfbd1a784cf127c5dc8dbd82780: 날짜와 실패 종료 코드·분석 기록 경합 수정, 기존+신규 회귀30 PASS.
5. fds-msa#23 HEAD67626a521f2d90b0e767674536b44647c01c1df2: 공용 접근 로그 보존, 실제 Uvicorn Config + Server 대역1 PASS. 전체 앱 CI/이미지 빌드·배포·양쪽 새 TRACE는 별도.

## 원본·한계

controller/는 .26ewmukr 회차 원본을 SSH로 회수한 것이다. SOURCE_SHA256SUMS 전부 검증. 인증은 tty에만 출력하고 결과는 인증 후 저장했다. Edge root 내부 전체 로그는 미회수이며, controller가 회수한 해당 결과 stdout/stderr만 보존한다. 진단 JSON은 명시적 선택 필드/코드 원문이며 전체 API·프로세스·환경 수집이 아니다. 암호/환경변수/Secret은 수집하지 않았다.

DB_ACCESS=READY / C0=BLOCKED / TRACE=NOT_READY / APPLY=NOT_RUN. 코드 PR·독립 리뷰·병합·배포와 증적 리뷰는 별도이며 AC/Issue/Phase1 Close 변경 없음. CODEX_ASSISTED.
