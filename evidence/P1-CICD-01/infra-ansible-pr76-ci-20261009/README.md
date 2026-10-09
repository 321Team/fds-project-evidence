# P1-CICD-01 — infra-ansible PR76 CI 및 Runner 정리

2026-10-09 KST · CODEX_ASSISTED · 이권욱. [PR76](https://github.com/321Team/infra-ansible/pull/76)의 worker02 DNS 회차 적용/복구 코드에 대한 격리 CI 회차다. 실제 worker02 접속/적용/복구·후보 엔진 전환은 수행하지 않았다.

- Source `0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea`, [Run37895578228](https://github.com/321Team/infra-ansible/actions/runs/37895578228)/attempt1, Job113706062449.
- Runner61 `ansible-ci-d98e4f42b2b6465d98b0448555337ec0`, 2026-10-09T16:42:33+09:00 ~ 2026-10-09T16:51:37+09:00.
- CI_RESULT PASS. syntax38개×2엔진=76개, unit208건(2.16.19), fixture 7단계 rc0. 2.21.3의 DNS51건은 [별도 controller 검증](https://github.com/321Team/infra-ansible/tree/0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea/docs/change/validation/issue9-dns-session)이며 모든 CI unit이 두 engine에서 실행됐다고 주장하지 않는다.
- GitHub 원본 ZIP SHA256 `314acac61f2a6ab240a0054ebc2c4264fdc43ca37a6af833af041b603984e858`: API digest와 내부 manifest 일치. 명시적 cache 제외는 VERIFIED_RESULT에 기록하고 존재 파일로 계산하지 않는다.
- 호스트 원본 archive SHA256 `3549a307b676921360762b091d97e2a1df6c299ef6c8a3e983bb263319b80a79`: sidecar 및 바깥16개/내부9개 manifest, Job↔Runner id/name 일치. 원본 archive는 재압축하지 않았다.
- operator.rc0, Runner/proxy/workspace REMOVED, 등록 Runner0, runner.py 부재, 수신 token packet/incoming 부재, admin packet 폐기를 확인했다.

16:41:58 KST 인증을 자동 감지하고 16:42:16 서버 release 기록으로 기존 대기 Job 한 건에 연결했다. 새 workflow 회차나 중복 Runner를 만들지 않았다. Windows 감지기와 서버 기록의 수 초 시계 차이를 원본 그대로 보존하며, release는 서버측 freshness 점검을 별도로 통과했다. 사용자 작업창13:20~17:00, 시작상한16:46·16:55 취소판단 기준으로 수행했다.

상태: CI SUCCESS / RUNNER_CLEANUP VERIFIED / 독립 증적 리뷰 PENDING / WORKER02_RUNTIME 및 ENGINE_TRANSITION NOT_RUN. 코드 독립승인과 Runtime GO·AC 인수를 구분한다. 비차단 rollback 재적용 생략 권고로 승인 HEAD를 변경하지 않았다. Harbor·Push/Deploy는 포함하지 않는다.

비밀정보 검사는 한정된 패턴 검사이며 모든 민감정보 부재의 증명이 아니다. 토큰 경로와 값은 구분한다. 토큰 값·암호·개인키는 편입하지 않는다.
