# 서버 시작 절차 딥리뷰 — wrapper 작성 전

기준: PR20 `2750634766862d7fe19479acacc4259ee8315061`, Run35139314896/Attempt1 queued.
기존 Runner v1.2·Admin token v1.1.1·Input guard v1.0 ZIP은 변경 없이 재포장한다.
새 Python/Ansible 실행기를 만들지 않고 두 호스트의 Bash 진입점만 추가한다.

- 관리 호스트 ansible01/server01_ansible: 일반 계정·정해진 홈·홈 환경값·호스트를 확인하고 SHA256으로 고정된 Admin ZIP을 신규 홈 경로에 해제한다.
- 토큰 발급 전 gh GET으로 PR20 head와 Run35139314896 attempt1/queued, 같은 저장소/pull_request/source SHA를 확인한다.
  이미 실행·종료·재실행된 Run 또는 바뀐 HEAD는 이 키트에서 중단한다. 실제 Run 진행 상태를 대신 판정하지 않는다.
- API조회/진단 증적은 홈 신규 디렉터리,0600 기본 umask, SHA256SUMS. 관리자 인증 내용이나 token packet을 포함하지 않는다.
- Runner 호스트 cicd-runner01/server01_cicd-runner: 일반 계정/홈/호스트 확인, 고정 ZIP을 신규 홈 경로에만 해제한다.
- token 입력은 홈 바로 아래 파일명만 받는다. 절대경로/슬래시/빈 값/임의 디렉터리는 거절한다. 원문을 eval하거나 shell 코드로 해석하지 않는다.
- 기존 safe_input.py가 실제 형식·소유자·링크·만료·같은 FD에 대한0600 검사를 수행해야 serve로 연결한다.
- PREPARED 경로는 제출된 성공 영수증에 고정한다. launcher의 bundle/image/계정/자원/격리 재검사를 그대로 둔다.
- 모든 chmod/삭제는 새 wrapper에 넣지 않는다. 기존 helper가 검증된 FD만 변경하며 기존 controller가 자기 session만 정리한다.
- 환경변수 HOME을 재정의하지 않는다. 기존 앱 Runner·sudo 정책·방화벽·서비스를 바꾸지 않는다.
- 실행 묶음을 sudo로 시작하지 않는다. 권한 전환은 검증 뒤 기존 sudo bash run.sh serve에만 사용한다.
- Bash 구문, 잘못된 현재 호스트에서 API/생성/등록 전 거절, 고정 payload hash 및 manifest 보존을 확인한다.
- 실제 토큰 발급/serve를 제작 환경에서 모의 성공으로 표시하지 않는다. 토큰은 비공개 파일 전송만 안내한다.
