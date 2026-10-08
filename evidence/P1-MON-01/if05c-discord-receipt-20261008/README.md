# IF-05C Discord 수신 보완 — 2026-10-08 KST

작성: 이권욱(GWONUK), CODEX_ASSISTED. 책임 [MON #17](https://github.com/321Team/fds-project-baseline/issues/17), 소비·교차검증 [SEC #19](https://github.com/321Team/fds-project-baseline/issues/19), [증적 PR157](https://github.com/321Team/fds-project-evidence/pull/157).

## 판정

사용자가 제출한 Discord 화면과 붙여넣은 본문에서 `FDSMonitoringPipelineTest`의 **FIRING과 RESOLVED 두 알림 수신을 확인**했다. 기존 08:57 수신 보고만 있던 상태를 수신자 측 화면·본문 증적으로 보완한다. Discord 채널/API를 직접 조회한 결과가 아니며, 메시지 링크·ID와 Resolved 개별 수신 시각은 미제공이다. 해당 제한과 독립 REVIEW=PENDING을 유지한다. AC 승인·티켓 종결은 선언하지 않는다.

## 파일과 출처

- `discord-firing-resolved.png`: 사용자가 이 채팅에 첨부한 PNG 원본 바이트. 재인코딩·크기 변경·편집 없이 복사하고 원본과 SHA256/크기를 대조했다.
- `user-supplied-message-text.txt`: 사용자가 붙여넣은 두 알림 본문을 UTF-8/LF/마지막 개행으로 저장했다. Discord API export 또는 원 전송 바이트로 표시하지 않는다.
- `RECEIPT.json`: 수신 출처, 포장 시각, 수신 파일 hash, 화면 관찰, 서버 증적 참조 hash, 대조 결과 및 미확인 항목.
- `SHA256SUMS`: 이 회차 파일 바이트를 확인한다. 이미지 내용의 진위나 AC 인수를 hash만으로 증명하지 않는다.

## 기존 실행과의 대조

기준은 [기존 실행 증적](https://github.com/321Team/fds-project-evidence/tree/2bc20a030ebd00e89fc7bb5317c4fafad05bd810/evidence/P1-MON-01/if05c-runtime-20261008)이다. 기존 폴더의 당시 `NOT_VERIFIED`, 사용자 보고, 서버 원본과 오류를 변경하지 않았다.

| 관측 | 수신자 증적 | 서버 증적 |
|---|---|---|
| 알림 식별 | 두 알림의 이름·라벨·설명·요약 동일 | `firing.json`의 rule/labels/annotations와 일치 |
| Firing | 붉은 FIRING 카드, 발신자 옆 08:57 | 08:57:32 KST Firing 관측, 발송 counter 1 |
| 해소 | 녹색 RESOLVED 카드, 조건 `vector(1) == 0` | 08:58:24 원복, 08:59:31 후속 inactive·대상 알림 0·발송 counter 2 |
| 발송 오류 | 화면 두 알림 수신 | Discord 실패 counter 0 |

화면 상단 08:59는 휴대전화 상태 표시줄 시각이며 Resolved 메시지의 개별 수신 시각이 아니다. 화면에는 달력 날짜·시간대가 없다. 2026-10-08 KST 시험 연결은 이번 증적 요청에 대한 사용자의 후속 제출, 앞선 08:57 보고, 일치하는 알림 내용·조건과 서버 시간선을 종합한 대응이다. 화면만으로 날짜·시간대 또는 유일한 실행 ID가 확정된다고 주장하지 않는다.

## 유지하는 한계와 다음 단계

실제 서버 시험을 반복하거나 설정을 변경하지 않았다. 원 실행의 정리 오류 `rc=3` 및 별도 읽기 점검 `rc=0`, 원복 완료, 미실행 수정 후보는 기존 판정을 유지한다. 두 수신 메시지의 내용 미확인 항목은 사용자 제출 증적으로 보완됐으며, 개별 메시지 링크·Resolved 정확한 시각은 여전히 미확인이다. 이 제한의 인수 영향은 담당자·독립 리뷰어가 AC에 맞춰 판단한다.

리뷰어는 PNG와 본문, `RECEIPT.json`의 서버 참조 및 기존 실행 원본을 대조한다. 새 Runtime은 필요하지 않으며, 증적 독립 검토·AC 판정은 별도다.
