# 원본 인수자·보존기간 결정 — 2026-10-09 KST

사용자의 “인수자는 연관성있는 담당자에게 선정, 보존기간은 자원 회수기간과 통일” 지시를 반영한다. 이 결정은 PR195에서 전달한 **6개 archive**에 적용하며 팀 전체 보존 정책이나 Harbor 작업을 변경하지 않는다.

| 범위 | 지정 인수자 | 담당 근거 |
|---|---|---|
| K8S 이전17파일 원본 archive | 이하영 (`hayeounglee`) | [P1-K8S-01 #10](https://github.com/321Team/fds-project-baseline/issues/10) Lead/Assignee |
| APP offline 공급 ZIP | 이재환 (`supreme33-kr`) | [P1-APP-01 #15](https://github.com/321Team/fds-project-baseline/issues/15) Lead/Assignee |
| APP TBS metadata·raw69 전송 archive, CI76 artifact·host archive | 이권욱 (`GWONUK`) | [P1-CICD-01 #16](https://github.com/321Team/fds-project-baseline/issues/16), [Runner #61](https://github.com/321Team/infra-ansible/issues/61) Lead/Assignee |

APP raw69 안의 source/OCI/scan 내용은 이재환이 관련 소비자로 확인하고, 이하영의 PR 독립 증적 검토는 유지한다. 보관 책임·소비자 확인·독립 리뷰를 구분한다. 이 배정으로 기존 업무 티켓 담당자 또는 Runner 두 번째 운영자를 변경하지 않는다.

## 보존 종료 기준

**자원 회수기간(현재 계획: 2026-10-23~2026-10-26 KST)의 종료 시점까지 보존한다. 현재 계획상 종료일은 10월26일이며 별도 시각은 미지정이다.** 승인된 자원 회수 일정이 변경되면 같은 종료 기준을 따라 갱신한다. 10/23 일부 자원이 먼저 정리되더라도 이번 묶음의 보존 종료일을 임의로 앞당기지 않는다.

- [#55 최신 정리안](https://github.com/321Team/fds-project-baseline/issues/55#issuecomment-6055015820): 10/23 정리 목표는 Review 전 자동 삭제 허가가 아니며, 10/26 잔여 정리/Sign-off→#57 순서를 유지.
- [#55 현행 Schedule Note](https://github.com/321Team/fds-project-baseline/issues/55): 10/23 Review Action 접수, 10/24~25 비근무, 10/26 잔여 비용/자원 정리·Sign-off.
- [#57 Close 기록](https://github.com/321Team/fds-project-baseline/issues/57#issuecomment-5907904039): 10/26 승인된 Review Action·cloud resource cleanup·Close Sign-off.

이 보존기간 지정으로 자원 회수나 파일 삭제를 실행하지 않는다. 자동 삭제 예약은 없으며 Git에 편입한 증적 기록의 보존 규칙은 변경하지 않는다.

## 인수 상태와 완료조건

**인수자 지정 완료 / 각 인수자의 실제 인수 확인 대기.** 자동화 도구의 복사·해시 대조 결과를 지정 인수자의 확인으로 대신하지 않는다.

각 인수자는 승인된 공유 폴더에서 자기 파일의 접근·목록·크기·SHA256을 확인하고 해당 범위를 PR195 또는 CICD#11에 기록한다. raw archive는 APP_RAW_RECEIPT.json·별도 .sha256, 최초5묶음은 RECEIPT.json·SHA256SUMS.txt를 사용한다. 불일치·접근 실패 시 인수 완료로 표시하지 않고 기존 원본을 유지한다.

최초 receipt의 NOT_CONFIRMED는 수집 당시 이력으로 그대로 보존한다. 이 후속 결정이 담당자·보존기간 미정 상태만 대체하며 실제 인수·독립 리뷰·AC 완료로 확대하지 않는다. 공유 접근 권한 변경·Harbor 작업·서버 Runtime은 없다.
