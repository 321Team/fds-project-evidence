# P1-CICD-01 — infra-ansible PR77 CI 및 Runner 정리

2026-10-09 KST · CODEX_ASSISTED · 이권욱. [PR77](https://github.com/321Team/infra-ansible/pull/77)의 GitHub UTF8 출력 처리 수정 및 운영 카드에 대한 격리 CI 회차다. 실제 worker02 DNS 변경, 운영 엔진 전환, Harbor/APP Push/Deploy는 수행하지 않았다.

- Source `0397211b5af619a7bc4593d9457f7f154c2ffd09`, [Run37910454972](https://github.com/321Team/infra-ansible/actions/runs/37910454972)/attempt1, Job113754076550.
- Runner62 `ansible-ci-4db2a2cdf1284ce4a7bea472f1dc372c`, 2026-10-09T19:04:24+09:00 ~ 2026-10-09T19:13:09+09:00.
- CI_RESULT PASS. syntax38개×2엔진=76개, unit 결과 `[210]`(2.16.19), fixture 7단계 rc0. CI unit 전체가 두 엔진에서 실행됐다고 주장하지 않는다. 별도 Windows/Linux queue18건과 독립 리뷰의 macOS18건은 PR77 참조.
- GitHub 원본 ZIP SHA256 `489042ccfad3c6f9cc380f83648680f75138bf2abf0d7c53368c145cb132c193`: API digest와 내부 manifest 일치. 명시적 cache 제외는 VERIFIED_RESULT에 기록하고 존재 파일로 계산하지 않는다.
- 호스트 원본 archive SHA256 `a9e09a618508c791b2df39bd7cd5a0ea9e1be6c639c60113bd8d285ce9b1445a`: sidecar 및 바깥16개/내부9개 manifest, Job↔Runner id/name 일치. 원본 archive는 재압축하지 않았다.
- operator.rc0, Runner/proxy/workspace REMOVED, 등록 Runner0, runner.py 부재, 수신 token packet/incoming 부재, admin packet 폐기를 확인했다.

정상 실행 계정 server01_cicd-runner의 사용자 직접 sudo 인증을 감지한 뒤 fresh 승인/HEAD/Job/labels/기존 Runner/컨테이너/세션을 확인했다. 기존 대기 Job 한 건에만 연결했으며 rerun/새 workflow를 만들지 않았다. 인증·release 실제 시각은 release-invocation.json/release-result.json을 보존한다. 회차 시작상한19:25,20:00 미완료시 취소판단, 사용자 창22:00 종료 기준이다.

상태: CI SUCCESS / RUNNER_CLEANUP VERIFIED / 독립 증적 리뷰 PENDING / 운영자2인·상시 알림·전체 AC 인수 미완료. 새 archive의 보존 담당은 CICD Lead 이권욱이며 PR195 사용자 보존 결정과 같은 자원 회수기간 종료(현재10/26 KST) 기준으로 관리한다. 이 PR의 archive는 1MB 이하·목록/sidecar 검증 후 비공개 Git에 편입하며 기존 공유6개 사본의 실제 인수와 별개다.

비밀정보 검사는 한정된 패턴 검사이며 모든 민감정보 부재의 증명이 아니다. 토큰 경로와 값은 구분한다. 토큰 값·암호·개인키는 편입하지 않는다.
