# Runner 알림 운영 채택 — 2026-10-13

Phase 1 #61의 기존 PR81 병합 코드만 사용한다. 이재환의 PR81 공급·인증·회수 실습과 알림의 실제 발송·수신 인수를 구분한다.

## 확정 입력

- 운영 담당: 이재환(supreme33-kr), 기존 대체·회수 연락: 이권욱(GWONUK).
- 알림은 GitHub #61 멘션 두 명만 사용한다. 카카오톡 전달자·별도 실패 발견자 지정을 제외한다. 기존 운영 담당 이재환이 Actions 감시 Run/로그·artifact와 #61 기록을 확인한다. 실제 근무 외 회차의 기존 수동 queue-watch는 회차 실행자가 유지하며 상시 당직은 지정하지 않는다.
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

반복 오류·조회 불명확·게시 불명확 시 기존 운영 담당이 Actions 실행 결과를 확인하고 알림 중지·로그/artifact 보존 여부를 판단한다. GitHub 게시가 불가능하면 가능한 때 #61에 실제 결과를 연결한다. 별도 외부 연락 경로의 구축·시험은 요구하지 않는다. 서버 정책·Runner·credential 생성은 이 활성화에 포함되지 않는다.

## 원본

- [운영자 수행 회신](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136928532)
- [PR81](https://github.com/321Team/infra-ansible/pull/81), [증적209](https://github.com/321Team/fds-project-evidence/pull/209)
- [사전검증 Run](https://github.com/321Team/infra-ansible/actions/runs/38339279651)
- [운영 런북](https://github.com/321Team/infra-ansible/blob/ec15dcbd022942add199a8f4718c0f88105e880e/docs/runbooks/Ansible-CI-Queue-Alert.md)

CODEX_ASSISTED. 코드 리뷰·증적 편입 승인과 실제 운영 인수를 합치지 않는다.


## 운영 연락 경로 정정 — 2026-10-13 KST

[이재환12:05 정정](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6137285563)과 사용자의 오류 지적을 반영한다. 카카오톡은 운영 입력·필수 대체 연락 경로에서 제외한다. 별도 카카오톡 전달자/실패 발견자 지정·연락망 구축·연락시험을 잔여 요건으로 두지 않는다. 알림 수신은 기존 GitHub #61 멘션 `supreme33-kr,GWONUK` 두 명이다.

감시 실패 확인은 기존 운영 담당 이재환의 업무로 연결한다. 설정 오류나 GitHub 쓰기 실패는 #61에 댓글을 남기지 못할 수 있으므로 기존 Actions 감시 Run·로그/artifact와 게시된 #61 기록을 확인한다. #61만으로 모든 실패를 검출한다고 표현하지 않는다. 새 담당자나 승인 단계를 추가하지 않는다. 실제 근무 외 작업의 수동 queue-watch는 기존 회차 실행자가 수행하며, 평상시 인간 연락 수단을 프로젝트 필수 통제로 확정하지 않는다.

11:59 활성화 전 `ADOPTED_INPUTS.json`은 당시 입력 원본으로 보존한다. 현재 운영 해석은 `OPERATING_INPUTS_CURRENT.json`과 이 정정을 따른다. 코드·repository variables·수신자·500분 유보·실제 CI/정리 결과는 변경하지 않는다. 기존 원본을 소급 수정하거나 완료CI를 재실행하지 않는다. 다음 업무상 실제 알림·수신 확인은 여전히 미완료다.
