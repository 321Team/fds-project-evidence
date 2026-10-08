# Docker syslog 기전 격리 실험 — 2026-10-08 KST

GWONUK / CODEX_ASSISTED. P1-HBR-01 후속 준비이며 운영 Harbor 자동기동 시험이 아니다.
[소스 PR14](https://github.com/321Team/infra-harbor-trivy/pull/14), HEAD
`9e7cf84ced5654dd9cd22808b07fa99c83600c63`, 실제 PR merge tree
`f19365f8e0de9d422fe8f62db3fffdb019762244`. GitHub-hosted Ubuntu/Docker28.0.4,
[Run37707666513/Job113085804845](https://github.com/321Team/infra-harbor-trivy/actions/runs/37707666513/job/113085804845)
09:25:13~09:25:21 KST SUCCESS. 로컬/CI guard 단위시험 각각4/4와 아래 실제 Docker 시험을 구분한다.

| 실제 경우 | 결과 |
|---|---|
| 명시적 IPv4+준비된 IPv4 listener | 컨테이너 exit0, 고유 로그 표식 실제 수신 |
| 명시적 IPv6+IPv4 전용 listener | logging driver `[::1]` connection refused, 시작 실패 |
| localhost+준비된 IPv4 listener | 이 runner에서는 성공·표식 수신. 운영 harbor01의 과거 IPv6 선택 실패와 환경 차이가 있음 |
| 명시적 IPv4+listener 미준비 | connection refused로 시작 실패 |
| 같은 객체, listener 준비 후 명시적 start | exit0·표식 수신. 자동 회복 증거가 아님 |

실제 Docker가 두 실패 조건을 각각 보였다. 따라서 IPv4 주소를 명시하더라도 logger가
준비되지 않은 시점의 기동 실패 가능성을 별도로 다뤄야 한다. 이번 실험으로 운영 Harbor의
발생 당시 logger 준비 시각이나 자동 재시작 정책의 동작을 재구성하지 않는다.

FROM scratch+로컬 정적 표식 출력기, 외부 pull/Harbor 접속/Secret 없음. 시험 객체는
network none/nonroot/read-only/drop ALL/no-new-privileges/restart=no, UUID label과 전체 ID로
정리했다. 결과 rc0/cleanup_errors=[]/회차 label 잔존0. daemon restart·호스트 정책 변경은 없다.
CI는 격리 기전 실험, HARBOR_AUTOSTART=NOT_TESTED, AC04=NOT_EVALUATED,
source/증적 REVIEW=PENDING, MERGE/운영 적용=NOT_RUN.

`artifact-selected/`는 GitHub artifact에서 받은 텍스트6개 원본이다. 수신한 전체7개 파일을
원 manifest와 대조한 후 생성 실행파일 `build/emit`만 Git에서 제외했다. 실행파일은 원
[artifact11520107701](https://github.com/321Team/infra-harbor-trivy/actions/runs/37707666513/artifacts/11520107701)
및 로컬 수신 사본에 보존하며 크기/hash·원 manifest는 `ARTIFACT_RECEIPT.json`에 기록한다.
artifact 유효기간의 기존 30일 표기를 정정한다. `ARTIFACT_API.json` 기준 약 **7일**이며
만료 예정은 **2026-10-15 09:25:11 KST**다. 로컬 원본 경로는 이권욱 PC의
`C:\Users\soldesk\.codex\.chatgpt-projects\g-p-6a85069945708191b56059da202e4461\phase1-work-20261008\harbor-lab-ci-37707666513\syslog-lab-37707666513-1\`이다.
제외된 `build/emit`은 785672바이트, SHA-256
`55d1308a3856ccbebcaf12c249d537d345c52a73447ed51d00d6128ead222eb3`로 로컬 사본을 재대조했다.
이 로컬 경로는 팀 공용 보관소가 아니며, GitHub artifact의 영구 보존을 뜻하지 않는다.
`ci-run.json`/`ci-log.txt`는 Run 출처·검증을 연결한다.

후속 상태: 이번 CI 이후 격리 Full Clone을 확보했고, 별도 [증적 PR159](https://github.com/321Team/fds-project-evidence/pull/159)에
컨테이너 재생성·Docker 재시작 실패·수동 복구를 제출했다. 아래 환경 확보 계획은 당시 이력이며,
이 폴더의 CI를 복제본 시험이나 후보 수정의 Runtime PASS로 바꾸지 않는다.

후속: 운영과 분리된 Harbor 복제 환경 확보, 실제 compose/override 소비 및 logger 준비·실제
로그 저장 기준 결정, 기동 책임·재시도 상한·원복 설계에 대한 HBR Lead 검토, 별도 적용·재시험.
PR12/13 대기는 유지하며 이 실험으로 운영 source의 독립 리뷰나 전체 자동기동 인수를 대체하지 않는다.
