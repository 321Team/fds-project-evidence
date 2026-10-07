# P1-CICD-01 — infra-ansible PR74 실제 CI·Runner 종료 원본

CODEX_ASSISTED · 2026-10-08 KST. 책임 infra-ansible#61/#9. 사용자 정상 실행 계정 TTY sudo 인증 후 기존 v1.3 ephemeral Runner를 한 Job에 공급했다.

- source PR74 HEAD `d8d99efaf2537c74fb8f412fef65b351af08f67a`.
- Run37650225888/attempt1, Job112891337296, Runner59 `ansible-ci-8033ecfeaed44f6a9c98af3e667a0e40`.
- Job 01:32:25~01:40:13 KST, regression 및 artifact upload 모두 SUCCESS.
- syntax core2.16.19 37개 +2.21.3 37개 =74/74. unit/guards/contract 및 두 엔진 B2/DNS fixture7단계 rc0. CI_RESULT PASS, production_apply=false / operational_engine_transition=false.
- ZIP 원본 SHA256 `98c1304721aa2539eb08fad688a206e328648e3a2dfc44e8d2df7edc1f67d019`; GitHub artifact digest와 일치. 바깥 manifest1015항목, fixture682항목 대조. fixture cache3개는 ARTIFACT_SCOPE의 명시적 제외로 대조했으며 파일이 존재한다고 주장하지 않는다.
- host archive SHA256 `22b5569968633157442380d9e2e524e3445bb3d7afd6e80468c8fb4ff72a27f2`, sidecar·바깥16/내부9 manifest 대조. HOME host_rc0, container Succeeded, agentId/name이 실제 Job과 일치.
- operator.rc0 / container·proxy·workspace REMOVED / repository Runner0 / runner.py 프로세스 부재 / 수신 token packet와 incoming 부재. admin packet 폐기 기록 확인. 장기 infra-cicd Runner에는 공급하지 않았다.

원본 ZIP과 host archive를 재압축하지 않고 보존했고 registry에 각각 등록했다. verifier 결과는 해당 bytes·제한된 상태 조회의 결론이며 모든 임시 경로/프로세스 전체 감사로 확대하지 않는다. 로그의 token packet 경로는 값이 아니며 token/비밀번호/개인키를 편입하지 않았다. 제한된 문자열 검사만으로 모든 민감정보 부재를 수학적으로 보장하지 않는다.

기존 [PR153](https://github.com/321Team/fds-project-evidence/pull/153)의 CI_PREPARATION은 공급 전 snapshot이다. 이번 회차는 그 이후 실제 CI 완료·정리 원본이다. worker02 DNS verify·운영 엔진 전환은 미실행이며 PR74 코드 독립 승인·병합도 별도이다.

재현·추적: job-final/run-final/artifact-final의 고정 source·Run·Job과 VERIFIED_RESULT를 연결한다. 원본 GitHub artifact 유효기간과 별개로 이 폴더가 중앙 보존본이다. 실패를 유발하려고 같은 CI/서버 시험을 반복하지 않는다.

상태: CI=SUCCESS / RUNNER_CLEANUP=VERIFIED / INDEPENDENT_EVIDENCE_REVIEW=PENDING / MERGE=NOT_RUN / WORKER02_RUNTIME=NOT_RUN.
