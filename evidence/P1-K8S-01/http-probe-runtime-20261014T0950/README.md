# 실제 engine HTTP Probe 1회 — 2026-10-14 09:50 KST

이권욱 / CODEX_ASSISTED. 운영 실행 결과와 관측 한계를 함께 편입하는 기록이다. 독립 증적 리뷰와 관련 AC 최종 인수는 별개다.

## 기준·허용·병합

- 사용자 `221, 86 차단사항 없으면 병합 후 착수`, 이어서 `11:15까지 세 조건 모두 확보` 확인. 콘솔 대기, Harbor/H6·APP/DB/MON 변경/다른 거래 writer 비중첩, db01 사전·사후 콘솔 조회 가능을 확인했다.
- [evidence#221](https://github.com/321Team/fds-project-evidence/pull/221): 이재환(`supreme33-kr`)의 exact HEAD `fb931f5a59032607bd051206c192a77168c5752c` 승인 + CI 성공 후 09:46:35 병합 `851c3827f69160a6299c859f2cca3a32dab41054`. 기존 HA PASS·복원 기록이다.
- [infra-kubernetes#86](https://github.com/321Team/infra-kubernetes/pull/86): exact HEAD `d53ce00f318785b97577d41c07d8309ff581c2a8` 독립 승인 + CI 성공 후 09:46:39 병합 `e60e022333a51a9a1690649ef170c0bda92ad9b9`.
- 적용 실행창은 PR86 최신 본문의 09:45~09:55 실제 시작, 10:20 복구·수집 종료다. 저장소 README/SQL의 과거 시간 예시는 소비하지 않았다. APP은 10:25~10:35 실제 시작·11:15 종료의 별도 단계다.
- 실제 engine HTTP 한 사례만 포함한다. DB 장애, 전체 engine0, Push/Deploy, drain/Eviction, Pod 강제삭제, 추가 SIGSTOP, 자동 재실행은 없다.
- 실제 source `engine_stop.py` SHA256 `8b9fe37dd0bcdbd09e0c7d5e7fb41eaa9e25d47fb56223bbab6273081251cc32`; 리뷰된 Git blob과 공급·수신 바이트 일치. binding도 Git blob `387d0d0990049b748c897ee999a5253b6e52bb66542cff598270d490b001165b` 그대로 공급했다.

## 실행·판정

| 항목 | 실제 원본에서 확인 |
|---|---|
| 사전 | 09:47 API3/engine3 Ready, restart0, 각 Worker1/1, MON23/23·앱6, edge ready200·업무 metrics404, 고정 프로세스 식별값 일치 |
| 주입 | worker02의 원 container PID1(host PID1290996), 09:50:42.482 SIGSTOP 1회 |
| readiness | 실제 readyz/livez HTTP timeout, 원 process state T. 09:51:07.392 최초 관측에서 동일 Pod Ready=false·업무 Endpoint ready=false |
| liveness | 대상 UID에 묶인 kubelet Unhealthy liveness 이벤트 3회, 09:51:34 Killing `failed liveness probe, will be restarted` |
| 종료/재시작 | 09:52:04.268 원 프로세스 종료 감지(81.786초); 실행기 rc0. 원본은 이미 종료되어 CONT0, 새 프로세스 신호0 |
| 같은 Pod | UID `e349b045-870f-4061-a677-3007efe479e9` 유지, containerID `7b24cf…`→`737b90…`, restart0→1; 기존 컨테이너 exit137 |
| 복구 | 09:52:15.407 최초 관측에서 Ready/Endpoint true. 별도 실제 HTTP 60초 정상, MON23/23·정확한 앱6 집합 60초 정상 |
| 영향 경계 | 비대상5 Pod/Node 관측 정상, 비대상 restart0, image·Deployment generation/spec 불변, 각 Worker API1/engine1 유지 |
| MON | 주입 중 23개 중 대상 `10.244.69.193:9090` 하나만 up0; 의도한 동일 프로세스 정지 영향으로 기록 |

`verify_result.py`는 원본을 읽어 위 대응을 재현한다. 실행기 rc0만으로 PASS를 판단하지 않는다. 실행 결과 판정은 `HTTP_PROBE_RUNTIME_PASS_WITH_RECORDED_OBSERVATION_LIMITS`; 관련 티켓 인수·종결/Phase1 전체 완료를 뜻하지 않는다.

## 관측 정정과 한계 — 실패 원본 보존

1. control01→Pod 직접 HTTP는 **주입 전부터** timeout이었다. 이 경로의 결과는 장애 성공 증거로 쓰지 않는다. 주입 전 worker02→동일 Pod의 200을 확인하고 그 경로에서 실제 실패를 수집했다. control01의 Pod/Endpoint/Node/Events API 관측은 연속 수집했다. 보안 설정 변경은 없다.
2. worker HTTP+proc 수집기가 09:52:03 무렵 원 PID 종료 경쟁에서 `ProcessLookupError`로 rc1 종료했다. `worker-http.jsonl/.stderr/.receipt.json`을 보존했다. 실행기의 pidfd 종료 감지와 Kubernetes API 관측은 지속됐다. 실제 HTTP 최초 회복 순간은 이 수집기의 공백 때문에 확정하지 않는다. 원본 PID를 다시 대상으로 잡거나 장애를 반복하지 않고 `http-recovery`의 읽기 전용 60초 관측으로 회복을 확인했다.
3. kubelet journal 조회는 시간대 없는 인자, 명시 UTC, epoch 인자를 각각 남겼으며 모두 No entries였다. kubelet service는 active/StandardOutput=journal이지만 journal 미수신 원인은 미확인이다. liveness 원인은 같은 UID·현재 시각의 **Kubernetes kubelet Events**로 입증한다. journal을 확보했다고 표시하지 않는다.
4. 공급 전 로컬 binding 파일의 CRLF와 Git LF 차이로 바이트 대조가 한 번 멈췄다. JSON 내용 동일을 확인하고 **Git 원본 bytes**를 공급했다. 실행기 bytes는 처음부터 동일했다. 이때 원격 공급/주입은 시작되지 않았고 실제 공급 1회·주입 1회다.
5. read-only 관측기·회복 보충은 중앙 순수 검증기 예외로 실행했다. `REVIEW=NOT PERFORMED (Pre-check/pure observer)`이며 운영 실행기의 독립 리뷰와 구분한다. 관측기 오류 수정으로 운영 적용 코드를 바꾸거나 재주입하지 않았다.

## 원본·재현·보존

- 기존 strict SSH `fds-ansible01 → svc_ansible → sudo worker02/control01` 경로. 키·환경변수·Secret 값 수집0, 인증/방화벽/SELinux 예외0.
- 원격 `/var/tmp/p1-http-probe-source-20261014-0945`와 `/var/tmp/p1-http-probe-20261014-0945`: root0700, 파일0600. 원본/claim 유지, 삭제·재사용 금지. 수신 원본은 `remote-originals-receipt`의 서버 경로/해시/모드/Base64와 `remote-originals/` 바이트를 대조한다.
- `observer.jsonl`: 2초 주기 K8s API와 사용하지 않는 control01 HTTP; `worker-http.jsonl`: 주입 전 정상·주입 중 실제 HTTP 실패/원 PID 상태. source·시각·strict SSH argv·rc·해시는 각 receipt에 있다.
- `mon-during`, `mon-stable`, `http-recovery`, `final-app-state`, `recovery-edge`, `final-target-http`, `kubelet-journal-*`은 해당 별도 수집이다. 최초 실패 자료를 덮어쓰지 않았다.
- 재현: `python -I -B verify_result.py <이 수집회차 경로>`. 검증기만 실행한다. `apply_once.py`, `verify_and_stage.py` 등 실행 기록용 운영 파일은 재실행하지 않는다.
- SHA256SUMS는 자기 자신을 제외한 이 수집회차 파일을 고정한다. 해시 일치는 무결성 확인이며 Runtime 판정·독립 인수의 대체물이 아니다.

## 남은 일

- 최종 APP 거래 회귀는 이 수집 시점 `NOT_RUN`, DB RUN0행·사후 실제22/23행 조회는 아직 미실행. 07:46 사용자 schema 조회는 현재 RUN0행 증거가 아니다.
- APP 전송 직전 새 DB0행·Pod/MON/metric baseline을 받은 뒤 승인된 10:25~10:35 창에서 기존 `rg.py` 1회. 새 기준선은 Probe restart 뒤 수집한다.
- DB#11은 사용자의 `최종 앱 회귀 후 판단` 유지. W4 전체 HTTP5xx `NOT_MEASURED` 유지. 이 결과로 MON 나머지5종/복합 AC/전체 Phase1을 종결하지 않는다.
- 새 증적 편입의 독립 리뷰·병합은 별도 대기다.
