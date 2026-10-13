# Runner 알림 운영 채택 — 2026-10-13

Phase 1 #61의 기존 PR81 병합 코드만 사용한다. 이재환의 PR81 공급·인증·회수 실습과 알림의 실제 발송·수신 인수를 구분한다.

## 확정 입력

- 운영 담당: 이재환(supreme33-kr), 기존 대체·회수 연락: 이권욱(GWONUK).
- 이재환의 점심·근무 외 실제 작업: 해당 회차 실행자가 queue-watch와 감시 Run 실패를 확인하고 기존 팀 카카오톡으로 전달한다. 회차 시작 시 실제 실행자를 기록한다. 작업이 없는 시간의 상시 대기를 지정하지 않는다.
- 수신자: `supreme33-kr,GWONUK`; 장기 대기 기준10분.
- 기존 schedule: 매일 KST09:07~23:37, 30분 간격. 23:37~09:07 공백은 회차 실행자의 수동 관측으로 처리한다. schedule 지연·누락을 포함한 통지시간 보장은 없다.
- 사용자 채택: `제안 채택 — 회차 실행자 담당·500분 유보`.

## 사용량·중단

11:50:08 KST 조직 Billing 원본: Linux803분, 순 청구0달러. Free 조직 월2,000분에서 계산상 잔여1,197분, 다른 CI500분 유보 후697분이다. 이후 다른 저장소·수동 실행과 실제 Job 소요가 차감된다. 저장소별 전용 쿼터가 아니다.

10/13~10/26 하루30건을 모두 1분에 마칠 때420분이라는 값은 예측이며 상한이 아니다. 사전검증12초도 과금 단위로 추가된다. 조직의 Actions0달러·추가사용 차단 설정은 유지했지만 이것이500분을 자동 보존하지는 않는다.

운영 시 일일 사용량 점검 및 새 대량 CI 착수 전, 조직 잔여량에서500분과 다음 확인 전 계획된 다른 CI·감시 소비 및 보고 지연 여유를 뺀다. 여유를 확인할 수 없거나 부족하면 **알림부터 `ANSIBLE_QUEUE_ALERT_ENABLED=false`로 중지**하고 기존 수동 queue-watch를 사용한다. 이미 실행 중인 감시 Run과 댓글도 확인한다. 이 기준은 수동 운영 조건이며 자동 예산 집행을 구현한 것으로 보고하지 않는다. 조직 비용 설정·별도 PAT는 변경하지 않는다.

현 자원 회수기간10/26 종료 시 알림 중지·원본 보관 상태를 확인한다. workflow 자체에는 날짜 만료가 없으며 자동 중지를 구현했다고 보고하지 않는다.

## 이번 검증과 완료조건

1. merged main `ec15dcbd022942add199a8f4718c0f88105e880e`, 알림 비활성 상태에서 `notify=false`1회만 실행.
2. Run38339279651 / Job115106404173 SUCCESS, notify Job SKIPPED. 관측 `NO_ALERT`, `DRY_RUN_NO_COMMENT`, 활성 Run0. artifact ZIP와 내부 JSON 해시 확인.
3. 같은 main과 설정 확인 후 활성화하고 읽기 결과를 저장한다. 활성화 사실은 `ACTIVATION_RESULT.json`으로 확인한다.
4. 다음 **업무상 필요한** 실제 장기 대기에서 감시 Run/댓글/수신자 회신 시각/queue-watch 판단/공급·CI·정리를 연결한다. 이번 사전검증은 실제 발송·사람의 수신·schedule 동작을 증명하지 않는다.
5. PR81은 재실행하지 않는다. O02의 제2운영자 실습은 충족했으나 전체O02·#61은 위 실제 알림 인수와 기존 잔여AC가 충족될 때까지 OPEN이다.

반복 오류·조회 불명확·게시 불명확 시 알림을 중지하고 로그·artifact를 보존해 기존 카카오톡 경로로 전달한다. 서버 정책·Runner·credential 생성은 이 활성화에 포함되지 않는다.

## 원본

- [운영자 수행 회신](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136928532)
- [PR81](https://github.com/321Team/infra-ansible/pull/81), [증적209](https://github.com/321Team/fds-project-evidence/pull/209)
- [사전검증 Run](https://github.com/321Team/infra-ansible/actions/runs/38339279651)
- [운영 런북](https://github.com/321Team/infra-ansible/blob/ec15dcbd022942add199a8f4718c0f88105e880e/docs/runbooks/Ansible-CI-Queue-Alert.md)

CODEX_ASSISTED. 코드 리뷰·증적 편입 승인과 실제 운영 인수를 합치지 않는다.
