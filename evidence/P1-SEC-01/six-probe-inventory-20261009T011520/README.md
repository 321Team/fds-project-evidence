# 실제 워크로드 6종 Probe 적용 상태 — 읽기 전용 조회

CODEX_ASSISTED · 이권욱 수집 지원. **현재 정의/상태 관측 완료, 실제 장애 주입·복구 및 AC 인수는 미실행**이다. [기존 격리 exec Probe #173](https://github.com/321Team/fds-project-evidence/pull/173)과 실제 워크로드의 차이를 연결하기 위한 자료다.

## 대상·시각·방법

- 원격 `k8s-control01`, 기존 PC→fds-ansible01→svc_ansible→sudo -n 관리 경로. 2026-10-09 **01:15:21.843~01:15:22.386 KST**, kubectl API GET18/18 rc0. 상위 SSH/수신 rc0.
- fds-app/monitoring-api/monitoring-node에서 지정 이름6종의 Pod·Deployment/DaemonSet/StatefulSet·Service·EndpointSlice만 projection으로 보존. 컨트롤러6개(Deployment5·DaemonSet1), Pod10개, 연결 EndpointSlice7개. 이름 prefix 필터 밖의 객체·다른 namespace 전체를 조사했다고 주장하지 않는다.
- 각 API의 조회 시각·rc·원 응답 hash·list resourceVersion, 객체 UID/resourceVersion, 선택된 probe/image/상태 필드를 포함. env·명령 원문·Secret/ConfigMap 내용·HTTP header 값과 query string은 전송하지 않는다. 원 API 본문은 보존하지 않아 원 응답 hash 자체를 수신 파일로 재계산할 수는 없다. 수신 projection의 bytes/hash와 분석 재현은 별도로 검증한다.
- 수집 전/매 조회 전 호스트·euid·사용자가 확보한00~09시 창 확인. API10초/프로세스15초 제한. 오류·timeout은 정상 빈 목록으로 처리하지 않는다. 신규 Pod/exec/직접 probe 호출/고장 주입/설정 변경/재시작/Harbor 접근 없음.

## 현재 관측

| 워크로드 | Pod Ready | readiness HTTP | liveness HTTP | startup |
|---|---:|---|---|---|
| fds-engine | 3/3 | 8001 `/readyz` | 8001 `/livez` | 없음 |
| Prometheus | 1/1 | 9090 `/-/ready` | 9090 `/-/healthy` | 9090 `/-/ready` |
| Grafana | 1/1 | 3000 `/api/health` | 3000 `/api/health` | 3000 `/api/health` |
| Alertmanager | 1/1 | 9093 `/-/ready` | 9093 `/-/healthy` | 9093 `/-/ready` |
| kube-state-metrics | 1/1 | telemetry→8081 `/readyz` | http-metrics→8080 `/livez` | 없음 |
| node-exporter | 3/3 | 9100 `/metrics` | 9100 `/` | 없음 |

API에 반환된 주기·지연·timeout·threshold 값은 `analysis.json`과 receipt 원본에 있다. Pod10개의 Probe projection은 각각 selector로 대조한 컨트롤러 template과 동일하며 generation=observedGeneration이다. EndpointSlice의 targetRef UID로 연결한10개 Pod 모두 ready=true/serving=true/terminating=false였다(서비스2개에 속한 engine은 중복 endpoint 행을 가짐).

node-exporter는 hostNetwork=true·hostPort9100이며 worker01/02/03의 누적 restartCount가4/1/1이다. 나머지7개 Pod는0이다. 이번 snapshot에 restart 원인·개별 시각·전후 변화가 없으므로 기존 liveness 실패 주입 또는 자동복구 성공 증거로 세지 않는다. Ready는 수집 시점의 API 상태이며 이 세션이 각 HTTP 경로를 직접 호출한 결과가 아니다.

## 기존 성공과 남은 검증의 연결

| 근거 | 입증하는 범위 | 이번에도 남는 부분 |
|---|---|---|
| #173 격리 exec T0~T3 | 별도 시험 Pod의 Ready/Endpoint 전이, restart0→1, 복구 및 UID 정리 | 실제6종 이미지/HTTP endpoint/의존성/운영 영향으로 일반화하지 않음 |
| 이번 API projection | 실제6종 정의·image/imageID·현재 Ready·Endpoint·누적 restart·컨트롤러/Pod Probe 일치 | HTTP 실패→Ready/Endpoint 배제→복구, liveness 실패→재시작 및 의존성 회귀는 미실행 |
| engine startupProbe 없음 | 현재 선언 상태 | startupProbe 미존재 자체를 새 결함/AC 위반으로 단정하지 않음. 승인된 대상별 요구와 비교 필요 |
| node-exporter hostNetwork | 현재 실행 경로의 차이 | 일반 Pod의 격리 시험/NetworkPolicy 결과를 호스트 경로 보호로 확대하지 않음 |

다음은 SEC Review Owner/APP·MON Lead가 기존 증적을 재사용할 범위와 실제 워크로드에서 추가로 필요한 최소 케이스를 결정하는 단계다. 6종 모두에 새 장애를 주입해야 한다는 요구를 임의 신설하지 않는다. 최종 APP 이미지·해당 회차 대상 UID·관측/중단/복구 조건을 고정한 GO 이전에 기존 #173 승인으로 새 실행하지 않는다.

## 보존·재분석

`receipt/collector.py`, `stdout.json`, `stderr.txt`, `invocation.json`은 수신 파일 그대로다. `run_readonly.py`는 실제 전송기, `analyze_probe_inventory.py`는 로컬 분석기다. 다음 명령으로 `analysis.json`을 재현한다(현재 폴더, Python3):

```text
python analyze_probe_inventory.py receipt/stdout.json
```

수신 source/stdout hash 대조 및 재분석 bytes 일치, 전체 목록 SHA256SUMS와 루트 대장 연결. 해시는 무결성이며 Runtime PASS·원본 진위 인증·독립 리뷰·인수가 아니다. 읽기 전용 수집은 종료됐고 생성한 원격 파일·임시 리소스가 없어 정리/원복 대상이 없다. 사용자 단독 작업창 전체를 반환했다는 기록은 아니다.
