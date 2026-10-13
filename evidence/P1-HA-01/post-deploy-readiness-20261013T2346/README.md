# 새 Deploy 이후 단일 Worker HA 준비

이권욱 · CODEX_ASSISTED · 2026-10-13 23:46~23:49 KST 조회. **PREPARATION, Runtime 변경 0회.** 읽기 결과와 실행 제안을 구분한다. 사용자 `권장 순서대로 진행`에 따라 증적 병합과 다음 단계를 준비했다. 새 시간창·콘솔·비중첩과 실제 HA 변경 허용은 아직 받지 않았다.

## 1. 연결과 현재 사실

- 새 [Push PR218](https://github.com/321Team/fds-project-evidence/pull/218)은 독립 승인된 9647a83 그대로 23:42:15 KST 병합했다(merge7e6bb13).
- [Deploy PR219](https://github.com/321Team/fds-project-evidence/pull/219), actual Run38412128227/1, source147f760, APP affbc69. 두 앱의 성공·원본은 독립 승인2364024에 고정되어 있다. PR218과의 대장 추가 충돌은 e7859e3에서 양쪽 파일을 보존해 정리했고 정합화 부분만 추가 검토 요청했다. 상세는 해당 PR 최신 상태를 따른다.
- 현장 원본: `current-cluster`, `current-edge`, `current-mon`, `current-capacity`, `edge-identity`, `cache-worker01/02/03`의 collector/receipt/stdout/stderr. 실제 수행한 API·HTTP GET와 CRI metadata 조회다. 토큰 발급·DB 쓰기·Pod 변경·drain·서버 파일 배치 없음. MON 조회의 임시 localhost port-forward는 종료 확인했다.
- source review 상태: 새 읽기 수집기는 **NOT PERFORMED (Pre-check)**. 재사용한 HA probe/judge와 APP rg.py는 `TOOL_BINDING.json`에 이전 승인 bytes와 조회한 현재 main의 동일성을 연결한다. 완료된 모의시험/CI를 재실행하지 않았다.

| 확인 | 현재 결과 |
|---|---|
| Deployment | API UID8a2af808… generation12 / engine UIDbf825dec… generation6, 각 ready/updated/available3 |
| 이미지 | API338b8a28… / engine8b257adb… manifest. Pod6개 imageID 일치, Deploy 후 UID 유지·restart0 |
| 배치 | 두 앱 모두 worker01/02/03 각1개; Local NodePort30080·ready endpoint각1 |
| worker02 | Node UID·boot/cluster는 `READINESS_BINDING.json`. 앱2개, PDB0/HPA0, 해당 노드 PVC Pod0. kube-state-metrics/ICR probe/DaemonSet은 퇴거 대상 아님 |
| 신규 배치 여유 | worker01 요청CPU0.8/8core·메모리576Mi/약23Gi, worker03 1.4/8core·2432Mi/약23Gi. 신규 앱1개는250m/256Mi. 해당 Worker 무taint·schedulable·Ready, 압력False |
| 캐시 | 새 두 manifest의 CRI metadata가 모든 Worker에 있음. 레이어 전체 무결성/registry 재pull 시험은 아님 |
| HTTP | edge01→각 Worker `/readyz`200·업무 `/metrics`404, edge local nginx `/readyz`200. 한 번의 정상 조회이며 HA 성공은 아님 |
| MON | `up`23개 모두1, 현재 앱 Pod 전용 port 대상6개 모두1. 개별 scrape 본문이나 전체 IF06B 인수로 확대하지 않음 |
| 시각 | edge01 abs offset0.000314688초 / control01 0.000330994초, Leap Normal. 기존≤0.25초 기준 충족 |
| 접근 | 기존 strict SSH fds-ansible01→svc_ansible, edge UID1003 `/home/svc_ansible`, CP1 sudo root/admin.conf. Python3.12.14. 신규 SA/키/Token 없음 |

## 2. 이번 회차 제안

원 기준은 병합된 [APP·HA 카드](https://github.com/321Team/fds-project-baseline/blob/b0a02109353616f3142ffd3b25228a8cdda04c8d/governance/handoffs/phase1-execution-20261010/APP_HA_EXECUTION_CARD_20261013.md) §4 및 [#22 결정안](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5887966702)이다. 기존 #22 과거 인수는 유지하며 새 이미지/분산 제약의 영향만 확인한다.

- **10/14 00:15~00:25 KST probe 실제 시작, 01:05까지 회복·수집 종료** 제안. UUID 대신 고유 회차명 `p1-ha-20261014-0015`. 시작 마감 미충족 시 실행0회. 시간은 `EXECUTION_PROPOSAL.json` UTC와 대조했다.
- edge probe **1회,900초**, 0.5초 tick마다3Worker GET `/readyz`: 초당6건·최대5403건, max_inflight24·connect1초/전체2초. probe/judge 코드는 그대로다.
- worker02 `.107` **1대**의 `fds-app` 두 앱만 cordon/drain1회→uncordon. 재부팅·노드 전체 workload 퇴거·Probe 실패 주입·이미지 변경·설정 변경·POST/DB 쓰기는 제외한다.
- uncordon 후 실제 2/0/1 또는1/0/2를 읽고, 필요하면 초과 노드의 같은 RS Pod를 **engine1개→회복→API1개**, 총2개 이하 UID/RV 선조건 Eviction으로 재분산한다. 추가 반복0회. 이미1/1/1이면 수행0회.
- 이권욱 콘솔 대기·Harbor 변경/H6/사후 관측·다른 APP/DB/MON/노드 변경 비중첩은 **새 창으로 확인 필요**다. 이전 Deploy 창과 소진된1회 허용을 재사용하지 않는다.
- 독립 리뷰는 이 카드의 대상/경계·시간 예산·관측과 회수 연결만 요청한다. 기존 source/AC/과거시험의 전체 재승인이 아니다.

## 3. 직전 진입 조건

1. 이 카드와 바이트가 같은 공급물, 새 허용 원문·독립 검토, 새 창 콘솔/비중첩을 확인한다. `EXECUTION_PROPOSAL.json`의 승인 대기 상태를 승인이라고 해석하지 않는다.
2. strict SSH/host key 경로 유지. CP1 host/boot·cluster UID·worker02 UID, 두 Deployment UID/generation/spec hash·active RS·imageID를 binding과 대조한다. Pod 교체/중간 rollout/다른 writer/불확정 대상이면 실행하지 않는다.
3. 6Node Ready/압력False, Worker 모두 schedulable·무taint, 앱3Ready/Worker별1/1/1·restart0·Local Endpoint, PDB/HPA0, 새 이미지 cache·수용 자원 여유·시각 기준을 다시 확인한다. worker02 전체 Pod를 읽어 selector에 맞는 것이 **fds-app의 이 두 Pod뿐**인지 대조한다. `kubectl drain --pod-selector`의 namespace 범위를 가정하지 않는다.
4. edge `/readyz` 모두200·업무 metrics404, MON 현재 대상23개 정상. 실행 직전과 사후 target 집합을 별도로 기록한다. Pod 이동 중 scrape target 교체를 과거 instance와 단순 합산하지 않는다.
5. 기존 경로가 없는 새 디렉터리만 mode0700, 파일0600으로 생성한다. edge `/home/svc_ansible/p1-ha-20261014-0015`, CP1 `/var/tmp/p1-ha-20261014-0015`(root). `supply/ha-probe.py`, `ha-judge.py`만 edge에 전달·SHA 대조. `rg.py`는 후속 참조이며 이번 실행에 사용하지 않는다. 기존 경로 존재·symlink·소유/권한/hash 불일치는 덮어쓰기 없이 중단한다.

## 4. 실행 순서와 명령

실행자는 기존 svc_ansible 경로를 사용하며 CP1 kubectl은 `sudo -n /usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf`이다. 아래는 승인 뒤 실행할 명령이며 이번 준비에서는 실행하지 않았다. stdout/stderr·rc·실제 wall/monotonic 시각을 각 단계별 새 원본으로 남긴다.

1. edge에서 공급 hash를 확인하고 probe1회:

   ```sh
   /usr/bin/python3 /home/svc_ansible/p1-ha-20261014-0015/ha-probe.py /home/svc_ansible/p1-ha-20261014-0015/probe.log 900 10.1.93.105,10.1.93.107,10.1.93.108 30080 24
   ```

   stdout/stderr와 PID·실제 시작/종료·rc를 별도 파일에 보존한다. 프로세스가 시작되지 않거나 포화·조기종료·기록 불가면 변경0회. 첫 probe record 뒤 CP1 실제 `baseline_start`를 기록하고 **61초 이상 모두200**·tick 누락0·지연≤0.2초를 확인한다. 변경 전 기준선 실패 시 drain하지 않는다.

2. CP1에서 fresh 대상·상태와 마감 여유를 다시 대조한다. 실제 `drain_start` 직후 아래 명령을 **1회** 실행한다. 이 명령 자체가 worker02를 cordon한다.

   ```sh
   sudo -n /usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf drain k8s-worker02 --pod-selector='app in (transaction-api,fds-engine)' --ignore-daemonsets --timeout=180s
   ```

   `--force`, `--disable-eviction`, `--delete-emptydir-data`, grace 축소, Pod delete, selector 확대를 사용하지 않는다. PDB/selector/대상 변화·명령 실패/180초 초과면 다음 퇴거 없이 복구로 간다. rc만으로 수락/거부를 추정하지 않고 대상 UID와 대체 Pod를 읽는다.

3. drain 종료 뒤 최대120초 내 두 앱3Ready·같은 이미지/RS·worker02 앱Pod0을 확인할 때 CP1 실제 `rescheduled_ready`를 기록한다. **61초 이상** 계속 관측하고 아래 uncordon을 수행한 실제 시각을 `uncordon`으로 남긴다.

   ```sh
   sudo -n /usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf uncordon k8s-worker02
   ```

   node `unschedulable=false` readback 후 **61초 이상** 관측하고 실제 `end`를 기록한다. `timeline.txt`는 `이름 epoch초`5줄이며 원 시각을 보존한다. 사후 길이를 맞추거나 결과가 좋아지도록 값을 고치지 않는다. 성공 경로 최대 약61+180+120+61+61=483초에 단계 여유를 더해900초 probe 안에 들어가야 한다. 900초를 넘겨야만 W를 덮는 상황이면 NOT_VERIFIED이며 자동 연장/재실행하지 않는다.

4. **W 종료 뒤** 필요할 때만 재분산한다. 최종6Pod/RS/UID·2/0/1 또는1/0/2를 새로 읽고 초과 노드의 같은 RS Pod1개를 선택한다. API보다 engine을 먼저 한다. 바로 전 fresh resourceVersion과 UID를 붙여 policy/v1 Eviction body를 생성·검토하고 해당 `fds-app/pods/<fresh-name>/eviction` endpoint에 `kubectl create --raw … -f <new-json>` **1회** 보낸다.

   ```json
   {"apiVersion":"policy/v1","kind":"Eviction","metadata":{"name":"<fresh exact pod name>","namespace":"fds-app"},"deleteOptions":{"preconditions":{"uid":"<fresh exact UID>","resourceVersion":"<fresh exact resourceVersion>"},"gracePeriodSeconds":30}}
   ```

   이 필드는 아직 생기지 않은 재배치 결과이므로 임의 UID를 미리 만들지 않는다. Pod 선택/파일 작성은 읽기 결과로만 확정한다. 각 앱120초 Ready·90초 MON·30초 안정 관측을 거친다. 첫 앱이 회복하지 않으면 두 번째는0회. 조건 충족에도 총2개로1/1/1이 되지 않으면 더 퇴거하지 않고 잔여 배치를 인계한다.

5. probe900초 종료·outstanding0·rc0을 확인한다. 원본 timeline을 edge로 동일바이트 전달한 뒤:

   ```sh
   /usr/bin/python3 /home/svc_ansible/p1-ha-20261014-0015/ha-judge.py /home/svc_ansible/p1-ha-20261014-0015/probe.log /home/svc_ansible/p1-ha-20261014-0015/timeline.txt 10.1.93.107
   ```

   원본을 PC로 수신·hash 대조한다. source/명령/UID·창/rc·전후 Pod·Endpoint·MON target·이미지·각 timeline 원시값을 봉인한다. 업무 metrics404/전용 scrape와 서비스 정상·worker02 schedulable·자식 프로세스 종료를 확인한다.

## 5. 판정과 실패 복구

- 기존 A=정상 Worker01/03의 비200 **0건**, B=성공응답 최대 간격 **≤1초**. W 전구간 측정·누락tick0·발사 지연≤0.2초·사전3Worker200·세 관측구간각≥60초를 모두 만족해야 PASS다. 대상worker02의000/503은 Local 경계로 별도 보존한다.
- HTTP 정상만으로 업무 POST/DB 무손실·새 Probe liveness 성공·전체 HA/Phase1 인수를 완료 처리하지 않는다. 기존 #22 Done/AC/원 인수 이력은 유지한다.
- 정상 Worker 비200·MON 비대상 장애·Pod/대상 교체·SSH 불명·deadline 초과·증적 기록 실패가 생기면 다음 변경을 멈춘다. **이 회차가 cordon한 같은 worker02를 uncordon**하고 실제 node/Pod/Endpoint/MON을 확인한다. 요청 결과가 불명확한 Eviction/drain은 재전송하지 않는다.
- 분산 복구는 허용한2개 한도뿐이며 실패를 숨기기 위한 강제 삭제·이미지 복귀·보안 정책 완화는 없다. Pod UID를 원래대로 되살릴 수 없고 같은 RS의 새 Pod 회복을 관측한다. 서비스 미회복 또는01:05 종료 시 이권욱 콘솔로 상태·이미 수락된 요청·원본을 인계한다. 종료시각이 지났다는 이유로 안전 복구 필요를 성공 처리하지 않는다.
- 측정 프로세스900초/미결 요청 정리상한 뒤 종료를 확인한다. 정상 실패 시 원본을 남기며 재시험은 별도 회차다. 무조건 trap 재drain/새 token/새 Deploy를 하지 않는다.

## 6. 이후 순서

HA와 배치·서비스 복구 이후, 필요한 실제 engine HTTP Probe1건은 기존 [최소 사례 카드](https://github.com/321Team/fds-project-baseline/blob/b0a02109353616f3142ffd3b25228a8cdda04c8d/governance/handoffs/phase1-execution-20261010/HTTP_PROBE_REUSE_20261013.md)의 정확한 container·주입/회수·MON 영향 범위를 별도로 구체화한다. 이번 HA 허용에 포함하지 않는다.

최종 APP 회귀는 병합 카드§5의 **같은 KST 날짜05:00 이후**, DB 사전RUN 범위0행·writer 배제·25요청1회·8열 DB대조·metrics6개 전후 기준을 유지한다. 이번 제안 시점 이후 earliest는10/14 05:00이며 현재 회차의 범위 밖이다. `rg.py` 기대 입력이 당일02:30/05:00을 사용하므로 편의상 전날로 바꾸거나 미래 입력에 대한 기준을 바꾸지 않는다. 기능 시험행은 기존 보존결정에 따르며 삭제하지 않는다. DB#11은 사용자의 **최종 앱 회귀 후 판단**, W4 **NOT_MEASURED**를 유지한다.

STATIC/READ 준비 완료와 독립 REVIEW·실제 HA Runtime·최종 인수는 각각 별개다. 새 window/console/nonoverlap 결정 전 HA·Eviction·POST·DB 쓰기0회.
