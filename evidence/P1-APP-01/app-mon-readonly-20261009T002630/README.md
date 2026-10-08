# APP 업무 포트 metrics·실행본 및 Grafana 접근 경로 조회

CODEX_ASSISTED · 이권욱. 2026-10-09 00:26~00:28 KST, [00~09시 단독 창](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6062332401) 안에서 읽기 전용 조회했다. 관련 요구·기존 추정: [APP Lead #15](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-6052330629), [MON 리뷰 #17](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6035136512). 철회된 예외 요청을 판정 근거로 사용하지 않았다.

**업무 포트 `/metrics` 응답은 실제 200으로 확인됐다. Grafana 승인 관리 단말 전용 접근의 배타성은 이번 조회로 입증되지 않는다.** AC 체크·위험 수용·정책·설정·서비스·배포 변경은 없으며 Harbor 자동기동 세션은 접근하지 않았다.

## 실제 수행·응답

| 출발지·경로 | 결과 | 범위 |
|---|---|---|
| edge01 → worker01/02/03 `:30080/metrics` | 3/3 HTTP200, 각각 HELP18·TYPE18 | nginx를 거치지 않은 허용 업무 경로. `/readyz` 대조군도3/3 HTTP200 |
| transaction-api Pod 네트워크 → engine Service `10.97.246.223:8001/metrics` | HTTP200, HELP13·TYPE13 | worker01의 기존 transaction-api 네트워크 namespace. Service가 선택한 backend 개별 Pod는 식별하지 않음 |
| Prometheus Pod 네트워크 → engine Service `:9090/metrics` | HTTP200, HELP13·TYPE13 | 전용 metrics 허용 경로 대조군 |
| Prometheus Pod 네트워크 → transaction-api Service `:9091/metrics` | HTTP200, HELP18·TYPE18 | 전용 metrics 허용 경로 대조군 |
| edge01 → 자기 nginx `10.1.93.50:80/metrics` | HTTP404, HELP0·TYPE0 | `/readyz`는200. **외부 Client에서 새로 시험한 것은 아님** |

11개 HTTP GET을 각1회, timeout4초·응답 상한262,144B로 수행했다. redirect/proxy/retry를 사용하지 않았고 모든 응답은 상한 미만이었다. 전체 본문은 전송·저장하지 않고 상태코드·Content-Type·읽은 바이트 수·SHA256·HELP/TYPE 줄 수만 원격 수집기 출력으로 남겼다. 따라서 `body_sha256`은 이 회차의 관측 식별값이며 보관되지 않은 HTTP 본문을 다시 검증할 수 있는 원본 manifest가 아니다. 계측치 자체의 정확성·API DB 회귀 시험은 범위 밖이다.

### 접근·오류·원복

- Windows → 기존 `fds-ansible01/server01_ansible` → 기존 key/known_hosts의 `svc_ansible`.
- control01과 worker01/03은 기존 `sudo -n`으로1회 Python stdin 수집. control01은 Kubernetes raw GET10개만 수행하고 Secret/ConfigMap 내용을 조회하지 않았다. API JSON은 env/명령/annotation을 제외한 projection으로 반환했다. projection 전 해시는 기록하지만 전체 API 원문을 보존했다고 주장하지 않는다.
- Edge 첫 시도는 sudo 인증 부재로 **수집기 실행 전 rc1**. HTTP0건이며 실패 원문도 보존했다. HTTP GET은 root가 필요 없으므로 같은 승인 계정의 일반 권한으로 다시 수행했다. 새 sudo 권한이나 다른 인증 경로를 만들지 않았다.
- Worker의 `crictl inspect`에서 고정 containerID·Pod UID·RUNNING·PID를 확인하고 `nsenter -t PID -n`으로 해당 **네트워크 namespace만** 사용했다. 호스트 Python으로 고정 Service IP를 호출했으며 Pod 내부 DNS·앱 프로세스 실행 UID·ServiceAccount 인증 시험은 아니다. 실행 전후 PID/RUNNING과 netns 식별값을 남겼다. 기존 Pod 파일 쓰기·프로세스 재시작 없음.
- 쓰기·설치·권한 변경·임시 리소스·port-forward·고장 주입이 없어 설정 원복할 항목은 없다. GET에 따른 일반 접근 로그·카운터 발생은 가능하다. 의도적 로그/캐시 초기화 없음.
- 창 밖/호스트·실행 계정 불일치/컨테이너 식별 불일치 시 중단하도록 수집기에 제한했다. HTTP 오류는 행별 사실로 남기며 성공으로 치환하지 않는다.

## 현재 이미지와 실행 코드 대조

00:26 inventory에서 APP6개 Pod 모두 Ready, 각 앱은 Worker3대에1개씩이었다. transaction-api imageID는 `sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33`, fds-engine은 `sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369`다. `/app/run.py`와 `/app/app/main.py` 실제 파일 hash는 **worker01의 각 앱1개, 총4개**만 조회했다.

- 4개 모두 `fds-msa` 과거 Source `adc90410`의 해당 Git blob과 일치한다. 전체 commit은 `app-mon-analysis.json`에 있다.
- 현재 main `8eac4c982076e3c219840a13686b15c46879981f`와 비교하면 transaction-api `run.py`만 다르고 나머지3개는 같다.
- 이는 선택 파일4개 대조이며 전체 이미지 재현성·모든 컨테이너 파일 동일성이나 새 main 배포 완료를 입증하지 않는다. engine Service 응답 backend와 worker01에서 hash를 읽은 engine이 같다고 가정하지 않는다.

## Grafana 관리 접근 — 정적 조회 결과와 남는 공백

- 현재 `monitoring-api/grafana` Service는 ClusterIP `10.111.143.44:3000`, NodePort/LoadBalancer/externalIPs 없음. 같은 수집의 Ingress 목록0개. Grafana Pod는 worker03, hostNetwork 미설정이며 노출 container port에 hostPort가 없다.
- namespace의 `default-deny-all`이 Grafana ingress를 선택한다. Grafana 선택 정책의 명시적 허용은 Prometheus 방향 egress이며, 수집된 Kubernetes NetworkPolicy 안에 Grafana ingress 허용 규칙은 없다. 이는 CNI/호스트/긴급관리까지 모든 접근이 차단된다는 동작 증명이 아니다.
- RoleBinding13개·ClusterRoleBinding64개 및 대응 Role/ClusterRole 목록을 수집했다. monitoring-api 범위에서 `pods/portforward`의 create 또는 wildcard에 해당하는 정적 binding은 `cluster-admin`(Group `system:masters`)와 `kubeadm:cluster-admins`(동명 Group)다. 인적 소유자·인증서/그룹 구성원·현재 로그인 능력을 확인한 것은 아니다.
- `system:controller:generic-garbage-collector`와 `system:controller:namespace-controller`는 get/wildcard resource 규칙 후보로 별도 분류했다. 이 두 ServiceAccount가 실제 port-forward 가능하다고 단정하지 않았으며, 연결 방식에 대한 SubjectAccessReview나 실제 세션 시험도 수행하지 않았다.
- control01의 `/etc/kubernetes/admin.conf`, `/etc/kubernetes/super-admin.conf` 모두 root:root 0600 존재를 **stat만** 확인했다. 내용·개인키·토큰·인증서 주체·복사본 목록을 읽지 않았다. 다른 노드/관리 PC의 사본 존재와 현재 감사/회수 운영 절차는 미확인이다.

따라서 이번 결과는 **현재 공개 경로/RBAC/일부 보관 위치 목록**이다. “승인 단말 port-forward만” 인수나 예외 처분을 완료하지 않는다. 추가로 Lead가 관리 주체별 정상/비상 경로, 자격증명 보유 위치, 사용 조건, 감사 기록, 회수 조건을 실제 원본과 연결해야 한다. 단말의 IP/위치 제약을 RBAC 사용자·그룹 binding만으로 대신하지 않는다.

해석 참고: [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/), [port-forward 접근 통제](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/), [NetworkPolicy API의 로컬 노드 트래픽 예외](https://kubernetes.io/docs/reference/kubernetes-api/networking/network-policy-v1/). 마지막 예외의 이 클러스터 실효 동작은 이번에 시험하지 않았다.

## 증적 구조·재검증

- `receipts/`5개: 실행 코드 정확한 바이트, 명령·시각·outer rc·코드/stdout SHA256, 원 stdout 및 stderr. Edge 실패 포함. API/HTTP raw body 대신 위 명시된 projection·카운트의 **수집기 원 출력**이다.
- `app-mon-analysis.json`: 응답 요약·RBAC binding 후보·실행 파일과 Git source 해시 대조.
- `analyze_app_mon.py`: 증적 폴더의 `receipts` 경로, 두 commit을 가진 fds-msa 로컬 clone 경로, **새 출력 경로**를 인자로 주면 서버 접속 없이 분석을 다시 생성한다. 기존 봉인 파일에 덮어쓰지 않는다. 예: `python analyze_app_mon.py <receipts> <fds-msa-clone> <new-analysis.json>`.
- `run_readonly.py`: 로컬 전송 실행자 사본. 처음 Edge는 sudo 시도했고 이후 `--unprivileged` 옵션을 추가했다. 각 회차의 실제 명령은 invocation이 기준이다. `prepare_http_collectors.py`는 초안 생성 코드이며 이후 Edge root조건을 제거한 정확한 실행본은 해당 receipt의 `collector.py`다. 이 지원 코드들을 그대로 재실행하라는 운영 지시가 아니다.
- 실제 코드/stdout 해시10개 대조 일치. 민감 패턴 검색0건은 휴리스틱 점검이며 전체 비밀 부재 보증으로 확대하지 않는다. 폴더 manifest와 루트 대장에 연결한다. 수집기 자체는 독립 코드 리뷰 미수행의 순수 조회·제한 GET이며 독립 **증적** 리뷰는 별도로 요청한다.

## 권장 후속

1. APP Lead/Review Owner가 업무 포트 `/metrics`의 실제 노출을 근거로 처리 방향을 확정한다. 권장은 업무 app 라우트·해당 시험 수정 PR을 준비하고 전용9090/9091 수집 유지 여부를 검증하는 것이다. 새 이미지 Build/Scan/Digest·승인 배포·회귀가 뒤따르므로 이번 조회로 운영 수정 완료를 선언하지 않는다.
2. Grafana는 승인 관리 단말·비상관리 경로의 주체/보관/감사/회수 정보를 보완하고 통제 또는 예외 처분을 결정한다. 관리자 권한·kubeconfig를 임의 삭제하거나 신규 role로 바꾸지 않는다.
3. #174의 K8S 구버전 도구 정합화와는 별개 조회다. 해당 도구를 실행하지 않았으며 이번 결과가 K8S 잔여 AC를 해소하지 않는다.
