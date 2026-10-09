# P1-CICD-01 — infra-ansible PR75 CI 및 Runner 정리 원본

2026-10-09 KST · CODEX_ASSISTED · 이권욱. [PR75](https://github.com/321Team/infra-ansible/pull/75) rollback 대상 범위 수정의 CI 회차다. worker02 canary·DNS 복구·운영 엔진 전환은 실행하지 않았다.

- Source `5d56818f273a0131b451fe2db4b0cbc276b03971`, Run37885828619/attempt1, Job113675501405.
- Runner60 `ansible-ci-a625cad22fa549bba10c6df31c64d1bb`, Job 2026-10-09T14:23:23+09:00 ~ 2026-10-09T14:31:16+09:00.
- CI_RESULT PASS. 고정 엔진별 syntax 수: `{"2.16.19": 37, "2.21.3": 37}`. fixture 단계 7개 rc0.
- CI unit discovery는 2.16.19에서 실행한다. 새 rollback scope 검사의 2.21.3 결과는 PR75의 별도 [controller 검증 원본](https://github.com/321Team/infra-ansible/tree/5d56818f273a0131b451fe2db4b0cbc276b03971/docs/change/validation/issue9-rollback-scope)에 있다. CI의 모든 unit을 양쪽 엔진에서 수행했다고 확대하지 않는다.
- GitHub 원본 ZIP `ci-artifact-11597531267.zip` SHA256 `ab782da1bd91eb87fbb81310e84fe1dd6917d49c06d2102e70dc3b0d1539c90e`: API digest·내부 manifest 대조. 명시적 cache 제외는 VERIFIED_RESULT의 manifests에 기록하며 존재 파일로 계산하지 않는다.
- 호스트 원본 archive SHA256 `768411d6977883cfbfcb4c0722dbc3afb69c610844023ec07dfd74be5bdcbc66`. sidecar·바깥 16개/내부 9개 manifest 및 Job↔Runner id/name을 대조했다.
- operator.rc0, container/proxy/workspace REMOVED, repository Runner0, runner.py 부재, 수신 token packet/incoming 부재, admin packet 폐기를 확인했다. 원본 archive는 재압축하지 않았다.

첫 인증은 14:15:05 성공했으나 assistant가 후속 release를 하지 않아 14:18:05에 180초 대기 만료됐다. 첫 시도에는 Runner 공급이 없었다. 사용자 재착수 후 새 operator에서 14:22:33 인증, 14:23:06 fresh 점검·release를 거쳐 **기존 동일 Job 한 건**이 실행됐다. 새 CI 회차나 중복 Runner를 만들지 않았다. 사용자 단독 창은13:20~15:00이며 Harbor는 제외했다. 임시 감지기의 PC/서버 시각 차이는 재확인으로 처리했고, 실제 release의 엄격한 신선도·동일 HEAD·중복 공급 검사는 유지했다.

원본은 이 증적 경로에 보존한다. 비밀정보 문자열 검사는 한정된 패턴 검사이며 모든 민감정보 부재의 증명이 아니다. 토큰 파일 경로와 토큰 값은 구분하며 값·암호·개인키를 편입하지 않는다.

상태: CI=SUCCESS / RUNNER_CLEANUP=VERIFIED / INDEPENDENT_EVIDENCE_REVIEW=PENDING / WORKER02_RUNTIME=NOT_RUN / OPERATIONAL_ENGINE_TRANSITION=NOT_RUN. 코드 리뷰·병합·운영 GO와 전체 AC 완료는 별도다.
