# 다음 확인: ansible01의 실제 gh 인증 출처·범위

현재 등록 토큰 POST는 HTTP403이다. 저장소 조회의 admin=true와 API 인증 token의 허용 범위는 별도다. HTTP403만으로 권한/SSO/정책/rate limit 중 하나를 확정할 수 없으며 현재 증적에는 오류 원문/관련 헤더가 없다.

먼저 같은 ansible01 기존 일반 로그인 셸에서 auth-status.sh를 실행한다. 이 명령은 기존 gh 인증 상태를 읽고 token 표시 행을 종류만 남기도록 변환한다. 토큰은 발급하지 않으며 로그인/refresh/권한 변경을 하지 않는다. 홈에 새0600 txt와 checksum을 남긴다. 기존 발급 도구·Runner 키트 변경은 없다.

`gh auth status --active --hostname github.com`에서 나타나는 인증 출처와 scopes, 두 환경 변수의 설정 유무를 확인한다. GH_TOKEN/GITHUB_TOKEN이 설정되어 있으면 저장된 gh 로그인 인증보다 우선될 수 있다. status 출력의 token 종류는 마스킹 전 prefix가 보일 때만 분류하며 unknown을 임의 추정하지 않는다. scopes가 없거나 unknown이면 사용한 토큰의 GitHub 설정에서 해당 저장소 접근/권한을 확인한다.

| 실제 인증 종류/관측 | 확인 및 수정 범위 |
|---|---|
| Fine-grained PAT | Resource owner321Team, 선택 저장소infra-ansible, Repository permissions의 Administration: Read and write. 조직 승인 필요 여부도 확인 |
| OAuth / classic PAT | repository Runner token API에 필요한 repo scope. 저장된 OAuth 인증일 때만 필요에 따라 gh auth refresh --hostname github.com --scopes repo 사용; 환경 토큰/PAT에 무조건 적용하지 않음 |
| GitHub App token | 해당 저장소 설치 범위와 Administration(write) 권한. 사용자 계정의 admin=true로 App token 권한을 대신하지 않음 |
| 권한 요건이 충족됐는데403 | 해당 오류 메시지/권한·SSO·rate-limit 응답 헤더를 안전하게 선별 확인. 새로운 PAT 발급이나 권한 확대를 반복하지 않음 |

인증을 변경했다면 같은 관리 호스트에서 기존 v1.1.1 토큰 도구를 한 번 실행하여 POST201 및 PASS_TOKEN_PACKET으로 검증한다. 성공하면 packet을 비공개로 cicd-runner01 홈에 전송하고 기존 registration-check로 이어간다. 자격증명 파일은 증적에 포함하지 않는다. Runner prepare를 다시 실행할 사유는 현재 없다.

이번 실행 결과는 2026-09-17 00:19:56~00:19:57 KST의 토큰 발급 실패다. 제거 토큰 단계·Runner 등록·실제 Actions는 미실행이다. 기존 Runner prepare PASS와 분리해서 기록한다.

공식 근거: [등록 토큰 API](https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository), [REST 오류 구분](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api), [gh auth status](https://cli.github.com/manual/gh_auth_status), [gh 환경 변수 우선순위](https://cli.github.com/manual/gh_help_environment), [gh auth refresh](https://cli.github.com/manual/gh_auth_refresh).
