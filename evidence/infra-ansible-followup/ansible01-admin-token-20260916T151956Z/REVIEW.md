# 등록 토큰 HTTP403 수신 검토 및 후속 명령 검토

## 확인된 사실

원본 SHA256 b29bd8f0b6d4cd90dceff1d2fe88492a3ab2969af6821868e21bf45a02d87c1d,751bytes. 외부 checksum, 내부 RESULT.json checksum/정확한 두 파일 집합, 정규 파일·크기 제한, 보완 도구와 common.py 해시가 모두 일치했다. 포함된 바이트/기록 대조이며 원격 attestation은 아니다.

실행 기록 2026-09-16 15:19:56.251283–15:19:57.226643 UTC(2026-09-17 00:19:56–00:19:57 KST). UID1000/ansible01, prctl0/errno0, gh 존재 확인 PASS. 저장소 GET rc0/HTTP200, repository_admin_reported=true. 등록 토큰 POST rc1/HTTP403, API_COMMAND_FAILED. 이후 제거 토큰 단계 없음. packet_written=false, runner_registration_attempted=false, actions_executed=false.

## 해석 및 제한

현 재실행은 인증된 저장소 조회 뒤 등록 토큰 요청에서 거절됐다. 계정 검사/prctl/gh 발견은 이 실행의 실패 지점이 아니다. 이전 v1 RuntimeError도 같은 원인이었다고 소급 확정하지 않는다. HTTP403의 응답 메시지/관련 권한·SSO·rate-limit 헤더는 현재 증적에 없어 정확한 거절 사유는 UNKNOWN이다. admin=true가 현재 gh 인증 토큰의 발급 권한을 증명하지 않는다.

공식 API의 repository Runner 토큰 발급은 repository admin 및 적절한 인증 권한을 요구한다. fine-grained token에는 repository Administration(write)가 필요하다. OAuth/classic의 repo 범위, 조직 정책/SSO/rate limit 역시 실제 사용 인증과 오류 내용으로 대조해야 하며 403만으로 하나를 단정하지 않는다.

## 후속 명령 작성 전 검토

다음 명령은 기존 gh auth status의 active github.com 계정/인증 출처/scopes만 조회한다. API POST, 토큰 발급, gh 로그인/refresh, 토큰 원문 출력 옵션을 사용하지 않는다. GH_DEBUG/GH_FORCE_TTY 제거, token 표시 행 삭제, 환경 토큰은 설정 유무만 기록한다. 새 홈 임시 파일0600, 실제 gh 반환코드를 보존한다. 원문 환경값/gh auth token/--show-token은 사용하지 않는다.

이 결과로 gh 환경 토큰과 저장 인증 중 어떤 것이 쓰이는지 확인하고 해당 종류에 필요한 최소 권한만 검토한다. 권한/SSO/정책 변경은 자동 수행하지 않는다. 등록 POST를 정보 없이 반복하거나 Runner prepare를 재실행할 근거는 없다. 기존 Runner v1.1과 PASS_PREPARE 유지, 코드 변경 없음.

공식 근거:
- https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository
- https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api
- https://cli.github.com/manual/gh_auth_status
- https://cli.github.com/manual/gh_help_environment
