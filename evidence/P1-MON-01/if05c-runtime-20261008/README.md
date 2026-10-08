# IF-05C 전용 시험 알림 실행·원복 — 2026-10-08 KST

실행·작성: 이권욱(GWONUK), AI 사용: CODEX_ASSISTED. 책임 티켓 [P1-MON-01 #17](https://github.com/321Team/fds-project-baseline/issues/17), 보안 증적 소비·교차검증 [P1-SEC-01 #19](https://github.com/321Team/fds-project-baseline/issues/19). 사용자 전용 알림 일시 활성화 착수 지시 범위의 1회 시험이다. 소스·증적 독립 REVIEW=PENDING. 이 자료는 AC 체크·티켓 종결·영구 변경 승인이 아니다.

## 판정과 범위

- RUNTIME: 전용 `FDSMonitoringPipelineTest` 활성화 1회 → Prometheus Firing → Alertmanager 대상 알림 수신 → 원본 복원 → inactive 및 Alertmanager 대상 알림 0을 관측했다.
- Discord 발송 측: notifications counter 0→1→2, 실패 counter 모두 0. 전이와 발송 증가가 일치한다. 사용자는 채팅에서 **08:57 수신**을 보고했으며(`USER_RECEIPT.json`), 원문은 추후 제공 예정이다. Firing·Resolved 각각의 수신 메시지 원문·링크는 **NOT_VERIFIED**다. 발송 측 수치나 이 사용자 보고를 두 메시지의 직접 확인 또는 전체 IF-05C 인수로 확대하지 않는다.
- 원 수집기 `rc=3`: 원복 확인 후 미시작 recovery service 정리 오류. 원본 오류를 보존했고 별도 읽기 전용 후속 점검 `rc=0`에서 원복·비활성·복구 unit 부재를 확인했다. 전체 실행을 PASS/rc0으로 표시하지 않는다.
- 전후 Prometheus Target 23개, down 결과 0개; 고정한 Prometheus/Alertmanager Pod UID·IP·imageID·restartCount·Ready 일치. 다른 Alert rule 정의 hash 동일, 관측 snapshot에서 다른 Alertmanager 활성 알림 0개. 관측 사이의 모든 순간이나 전체 클러스터 무변경을 입증하지 않는다.
- Probe 장애 주입, workload 재시작, Secret/receiver/security policy 변경, 병합·승인·정본 발행은 이 회차에 포함되지 않는다.

## 시각·출처

| 사건 | KST 2026-10-08 | 원본 |
|---|---|---|
| server dry-run 점검 | 08:55:28–08:55:29 | `server-originals/check-events.jsonl`, `preflight-status.json` |
| 실제 실행 시작 | 08:56:15.450975 | `server-originals/status.json` |
| 복구 timer 설정 / 실제 활성화 | 08:56:15.924815 / 08:56:15.995316 | `server-originals/run-events.jsonl` |
| Firing 및 Alertmanager 수신·발송 증가 관측 | 08:57:32.772806 | `server-originals/firing.json` |
| 원본 복원 확인 기록 | 08:58:24.187561 | `server-originals/restore-confirmed.json` |
| 읽기 전용 후속 snapshot | 08:59:31.564805 | `server-originals/post-observation.json` |
| 최종 원본 수신 완료 | 09:00:13.717557 | `drivers/fetched-final-invocation.json` |

서버 `k8s-control01` / `10.1.93.102`, 기존 `fds-ansible01` 경유 `svc_ansible`의 `sudo -n`으로 실행했다. 원본 경로 `/root/if05c-20261008-oo0o4gd4`; `RECEIPT.json`은 20개 파일의 원격 크기·mode·SHA256과 최종 unit 조회를 담는다. Git 사본이 서버 소유권·mode를 재현한다는 뜻은 아니다. 원본 로그 시간은 UTC이며 위 표만 KST로 변환했다.

실제 실행 `runtime.py` SHA256: `554baa1776c061972555367dfa5a5a8461156de651b3646f974738f0454f69bc`.
ConfigMap `monitoring-api/prometheus-p0-test-alert`, UID `fc3593b2-2937-49e0-acc9-8709dd1139a3`.
원본/복원한 `p0-test-alert.yml` SHA256: `c97c60256c4caa64cd9699539eccbb5d60f18907b1c8190cea280e0d7e8fb22c`.
시험 후보 SHA256: `6a8a147ff24934a6054ec55a2e50fe3d46024ba248605cef38cbcbbaacb4e9c6`.

## 실행 전제·순서·중단과 복구

실제 입력은 `server-originals/input.json`, 원본 및 임시 후보는 `original.json`/`candidate.json`이다. 기존 전용 규칙 `expr: vector(1) == 0` 한 곳만 1로 바꿨다. Pod 신원, 원본 CM/마운트 파일 hash, Target 23/0, 규칙 inactive, 기존 시험 알림 부재, 실제 Alertmanager route와 `send_resolved=true`, reload 지원을 확인했다. 준비·실행 명령과 종료 코드는 `drivers/*-invocation.json`, `launch.py`, 서버 command journal에 연결된다.

기록된 순서: `runtime.py check <원본경로>` → dry-run 성공 → `launch.py`의 단일 실행 표식·중복 방지 → `runtime.py run <원본경로>`. loopback-only port-forward로 API를 조회했다. 실제 적용 전에 360초 후 원복용 transient timer를 설정하고, UID/resourceVersion/data 비교 후 patch했다. 마운트 파일의 후보 hash를 기다린 뒤 reload하고 Firing/수신/발송 counter를 관측했다. finally 경로에서 원본 CAS 복구 → 마운트 원본 hash → reload → inactive/Target 상태를 확인했다. 중간 실패·timeout도 원복 경로로 진입하며, 다른 주체가 바꾼 데이터는 덮어쓰지 않는다.

이 폴더는 **완료된 1회 실행의 재현·검토 자료**다. 같은 launch 표식을 삭제하거나 현재 파일을 그대로 재실행하지 않는다. 추가 시험은 새 승인 창에서 최신 UID·Pod·원본·작업 중첩 여부를 확인하고 새 입력/경로로 준비한다. 성공 판정에는 서버 전이·원복뿐 아니라 요구된 외부 수신 증적과 독립 검토가 별도로 필요하다.

## 수집기 정리 오류와 수정 후보

`run-events.jsonl`에 `systemctl stop <unit>.timer <unit>.service`의 rc5와 서비스 미로드 오류가 남아 있다. timer는 중지됐고 아직 실행되지 않은 service는 없었다. 이 예외 때문에 원 실행 내부의 Resolved 관측 루프가 생략됐다. `status.json`의 `restore=CONFIRMED`, `rc=3`, `restore_error=COMMAND_FAILED`, `recovery_timer_left_armed=true`는 당시 내부 상태 그대로다. 마지막 true는 실제 timer 상태를 갱신하기 전에 예외가 난 **잔존 플래그**이며, 실제 unit이 계속 활성이라는 증거가 아니다.

이어 `drivers/observe.py`로 읽기 전용 확인했다. `readonly-followup-events.jsonl`/`post-observation.json`은 원복 hash·inactive·알림 0·counter 2·실패 0·다른 규칙 동일을 확인한다. `RECEIPT.json`과 후속 unit 조회는 timer/service 모두 `LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`임을 보여준다. 원 실행 및 후속 port-forward 자식은 종료·회수됐다. 시험 활성화는 반복하지 않았다.

`local-verification/runtime-v2.py`와 `cleanup.py`는 상태를 읽어 활성 unit만 정리하고 종료 상태를 다시 확인하는 **미실행 수정 후보**다. 서버 배포나 Runtime 검증은 하지 않았다. cleanup MOCK 8/8, CAS guard MOCK 9/9 결과를 보존한다. 실제 실행 소스 `server-originals/runtime.py`는 수정하지 않았다.

## 바이트·분석 검증과 미수신 항목

- `ANALYSIS.json`: 수신 20개 원본 해시, 설치 소스와 로컬 바이트, 전송 명령·소스 hash/rc, 실제 patch 수, 상태 전이·원복·오류 보존 등 50/50 오프라인 대조. 자체 검증이며 독립 리뷰가 아니다.
- `drivers/`는 실제 실행한 준비/전송/조회 소스와 invocation·stdout/stderr를 담는다. `fetched-final.json`의 base64는 원본20개와 `RECEIPT.json`으로 무손실 분리했다. 중간 poll01~03 및 첫 fetched의 반복 snapshot은 로컬에 보존하고 편입본에서는 제외했다. 최종 서버 journal·status 원본을 판정 근거로 사용했다.
- API 전체 원문을 저장한 것이 아니다. journal의 원문 hash와 선택된 응답 필드·알림·counter를 보존했다. 전체 Alertmanager 설정·webhook 자격정보는 편입하지 않았다. 내부 주소·Pod 신원은 private 증적 저장소 범위다.
- `SHA256SUMS`는 이 폴더 바이트 무결성, 루트 대장은 이 manifest를 연결한다. hash는 시험 성공이나 인수의 단독 근거가 아니다.
- 잔여: Discord Firing·Resolved 수신 원문/메시지 링크·시각 연결, 수정 후보 및 증적 독립 리뷰, 담당자의 AC 판정. 기존 PARTIAL/NOT_VERIFIED 이력을 소급해서 지우지 않는다.
