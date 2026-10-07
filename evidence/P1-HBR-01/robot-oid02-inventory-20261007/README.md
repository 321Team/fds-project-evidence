# P1-HBR-01 — Robot 소비자·노드·이미지·Docker 사전 상태 읽기 전용 조사 원본 편입 (2026-10-07)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13), OID-02는 [#14](https://github.com/321Team/fds-project-baseline/issues/14)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-06 Robot 회전, AC-04 Docker restart persistence, OID-02 처분의 PASS·승인이 아니다.** 서버·Harbor·Robot·방화벽은 변경하지 않았고 새 트래픽 시험·재시작·스캔도 하지 않았다. 모든 조회는 읽기 전용이다(2026-10-07 11:59~12:07 KST).

## 근거
[권욱 님 심층 리뷰 6017678964](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6017678964): Robot 회전 실행 준비 차단 HB-R1(소비자·검증 경로 미확정), Docker restart 차단 HB-R3(logger·정책·시간 한계 복구 분기 부족)과 요청한 사전 값(`RestartPolicy`·`LogConfig`·State·guard unit/의존성). [#14 6016976640](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6016976640): OID-02 2단계의 실제 eligible 노드·콘텐츠 완전성 공백.

## 파일과 해시
| 경로 | 크기 | SHA-256 | 내용 |
|---|---|---|---|
| `server-originals/robot-consumers-k8s-20261007T115910.txt` | 2206 | `1de512a47d5f1637d30bf0443a3eebef567eddc1facff7444d0504425d89fddf` | 11:59:10 control01(`server02`, ssh) `kubectl`: docker 계열 Secret(이름·type·UID·resourceVersion·생성 시각, data 미조회), ServiceAccount·Pod의 imagePullSecrets |
| `server-originals/robot-consumers-workers-20261007T115917.txt` | 766 | `d338ff71152f8357859d342ee1a579ff2ca4df3d8b7971be736be2640f02fe5d` | 11:59:18 worker 3대(ansible `-b`, `svc_ansible`): `/etc/containerd/certs.d/10.1.93.54/` 목록, `.docker/config.json` 위치와 Harbor 주소 포함 줄 수(내용 미출력) |
| `server-originals/robot-which-account-20261007T120116.txt` | 477 | `d87ffea3f015621682ee4d12483d2efd0e5194c583b927f56e6941cd50e57d39` | 12:01:16 control01 Secret 3개와 worker01 `/root/.docker/config.json`에서 **Harbor 주소와 사용자 이름만** 추출(비밀번호 미출력) |
| `server-originals/node-eligibility-20261007T115929.txt` | 2301 | `3dfc7a5f1cc6963eaff1417804ecb6bc13961cbb5f882c94163442362f659407` | 11:59:30 control01 `kubectl`: 노드 6개의 unschedulable·taint·os·arch·Ready·자원, 라벨 전체 |
| `server-originals/oid02-images-check-20261007T120334.txt` | 4163 | `d4c9b1ed7100b76fbc9f9221cd97e45355907397db77ea272ef576696bd96d01` | 12:03:35 6개 노드 `ctr -n k8s.io images check`에서 kube-controllers·coredns 줄(내용 완전성 판정) |
| `server-originals/worker01-docker-usage-20261007T120341.txt` | 876 | `0d57cc9a4da61388715b8217b3d9fd22f520c1a956ab71289b340313a92e73c3` | 12:03:42 worker01 `/root/.docker` 목록·mtime, Harbor 주소가 든 설정 파일 이름, nerdctl/docker 프로세스 유무 |
| `server-originals/kubelet-cred-config-20261007T120723.txt` | 498 | `4c9b2f7ab2f45d4539797b5011a632724c50225f9811526f638310e5d211ba8d` | 12:07:23 worker 3대 `/var/lib/kubelet/config.yaml`의 featureGates·인증 확인 정책 grep, kubelet 인자의 feature-gates |
| `server-originals/workloads-pull-policy-20261007T120724.txt` | 1509 | `fc3936e6eba203b07678ed272b8c963d8a48252e883b244ea2746ccd38788aa4` | 12:07:24 control01 Deployment·DaemonSet·StatefulSet의 imagePullSecrets·imagePullPolicy·이미지(Harbor 주소 항목만) |
| `server-originals/harbor01-docker-prestate-20261007T120724.txt` | 2810 | `7a33eba476dd6abfb35ca20716efc770ad8e6621f56101df2cdc57f6fc846cd5` | 12:07:25 harbor01(ansible `-b`, `svc_ansible`, `{% raw %}`로 감쌈): 컨테이너 10개 재시작 정책·로그 설정·상태(Env 제외), `docker info`, daemon.json 유무, docker·guard 서비스 의존성과 guard unit 파일 |
| `server-originals/nodes-disk-containerd-20261007T120725.txt` | 2556 | `e503bdc65d7fbbed451b186095d22626965e84f17dafa04726bc796ca31ce37f` | 12:07:26 6개 노드 `df -h`(containerd·kubelet 경로)와 `ctr version` |
| `scripts/show-docker-user.sh` | 421 | `f4ad6d430a5c2266b123347e8a7fa22449064558291185ba2b0e1476a2a85c25` | `robot-which-account`에서 worker01 파일의 사용자 이름만 꺼내는 스크립트. `auth` 값을 메모리에서 base64 해독해 `:` 앞(사용자 이름)만 출력하며 비밀번호 부분은 출력·저장하지 않는다 |
| `observations/ansible01-SHA256SUMS.local-part1-20261007.txt` | 724 | `b9aebf67b91d920bbaedb957d74d60e46b34dc5d69873c36e70925ca69769ed2` | ansible01에서 1차분(조회 6개+스크립트) 복사 후 만든 해시 목록(서버 측 해시) |
| `observations/ansible01-SHA256SUMS.local-part2-20261007.txt` | 433 | `10a84f593630f44c4a3819b35484e1064ca0f37f782d3f9c9d577deaa0c68a97` | ansible01에서 2차분(조회 4개) 복사 후 만든 해시 목록 |
| `observations/ansible01-SHA256SUMS.all-20261007.txt` | 1401 | `8ed42b59e41574f71fd8fc7442284aff35e1ad0c10e976820e7aaa1e65d6ea75` | ansible01에서 1·2차분을 한 폴더(`part1`·`part2`)로 합친 뒤 만든 전체 해시 목록 |

ansible01 터미널에 출력된 해시 11개와 공유 폴더 경유 본 PC 사본이 11/11 일치했다. 압축 안에 압축 파일은 없다.

## 조사 결과 요약
- **Robot 소비자(`robot-consumers-*`, `robot-which-account`):** docker 계열 Secret은 `fds-app`·`monitoring-api`·`monitoring-node`의 `harbor-pull-secret` 3개(생성 2026-09-22)이고 3개 모두 사용자 이름이 `robot$worker`이다. ServiceAccount에는 imagePullSecrets가 없고 Pod 13개가 spec으로 직접 참조한다(fds-app 6, monitoring-api 4, monitoring-node 3). worker01 `/root/.docker/config.json`(2026-09-30 12:17, root 0600, 215바이트)에 `robot$worker` 항목 2개(`10.1.93.54`, `10.1.93.54:443`)가 있고 worker02·03은 로컬 인증이 없다. `/etc/containerd/certs.d/10.1.93.54/`는 worker01에만 있고 `ca.crt`뿐이다. 실행 중인 nerdctl/docker 프로세스는 없고, containerd·crictl 설정에는 Harbor 주소가 없으며 kubelet 폴더의 `image_manager/pulled/` 기록 4개에 Harbor 주소가 있다(내용 미열람).
- **pull 정책(`workloads-pull-policy`):** 7개 워크로드 모두 `harbor-pull-secret`. `alertmanager`·`grafana`·`prometheus`·`node-exporter`는 `Always`, `fds-engine`·`transaction-api`·`kube-state-metrics`는 `IfNotPresent`. 실행 중 앱 이미지는 `fds-engine@sha256:5e2a081c…`, `transaction-api@sha256:a7093136…`.
- **kubelet(`kubelet-cred-config`):** `config.yaml`에 featureGates·이미지 인증 확인 정책 값이 없다(grep 결과 비어 있음). 프로세스 인자 grep의 두 줄(`feature-gates";`, `feature-gates[^`)은 ansible이 실행한 명령 문자열 자체가 `ps`에 잡힌 것으로 보이며 kubelet의 실제 인자가 아니라고 해석한다(해석).
- **노드(`node-eligibility`, `nodes-disk-containerd`, `oid02-images-check`):** 6개 노드 모두 Ready·스케줄 가능·linux/amd64, control 3대에 `control-plane:NoSchedule` taint, worker는 taint 없음. 각 노드 CPU 8·메모리 약 24Gi·임시 저장소 약 67GB·Pod 110, 루트 파일시스템 70G 중 약 60~62G 여유, containerd v2.3.5 동일. `kube-controllers`는 control01에만 있고 `complete (3/3)`, CoreDNS는 control01~03에 `complete (14/14)`, worker 3대에는 둘 다 없다.
- **harbor01 Docker 사전 상태(`harbor01-docker-prestate`):** 부팅 2026-10-06 10:04:31. 앱 컨테이너 9개는 `restart=always`, 로그 `syslog tcp://localhost:1514`, 10/6 복구 후 running(시작 04:17~04:21Z). `harbor-log`는 `restart=always`, 로그 `json-file`, 시작 2026-10-06T01:04:47Z. `docker info`: logging `json-file`, **`liveRestore=false`**, cgroup systemd. `/etc/docker/daemon.json` 없음. `docker.service`는 `fds-harbor-ac04-guard.service`를 Requires하고 After에도 포함하며 guard unit은 `Before=docker.service`, `RequiredBy=docker.service`, `Type=oneshot`·`RemainAfterExit=yes`, `ExecStart=/usr/sbin/nft -f /etc/p1-hbr-ac04.nft`이다.

## 한계 (숨기지 않음)
1. 조회 시점(2026-10-07 11:59~12:07)의 현재 상태이며 복구 당시나 이후 변화를 대신하지 않는다.
2. Secret의 마지막 갱신 시각과 어느 세대의 `robot$worker`인지는 확인하지 못했다(생성 시각 2026-09-22만 있음). Harbor 쪽 Robot ID·권한·생성/만료는 이 조사 범위 밖이다.
3. `show-docker-user.sh`는 worker01 파일의 `auth` 값을 메모리에서 해독해 사용자 이름만 출력한다. 비밀번호는 출력·저장하지 않았지만 해독 자체는 root 권한으로 수행했다.
4. kubelet의 이미지 인증 확인 기능 상태는 확정하지 못했다. 기본값 사용으로 보이나 설정 파일에 명시가 없다는 사실만 기록한다.
5. `liveRestore=false`와 앱 컨테이너의 `syslog localhost:1514` 로그 설정은 Docker 재시작 시 10/6 부팅과 같은 순서 문제가 재현될 수 있는 구조적 사실이다. 이 조사는 재시작이나 재현 시험을 하지 않았으며 원인을 확정하지 않는다.
6. `oid02-images-check`는 각 노드의 플랫폼(linux/amd64) 기준 `ctr` 판정이다. 공급 출처·재반입 원본은 여전히 미확인이다.
7. 원본은 ansible·터미널 출력이며 서버 쪽 봉인이 없고 독립 재해시하지 않았다.
8. 이 조사로 Robot 재발급·폐기, Docker restart, 이미지 보충, Source 제거를 승인하거나 시작하지 않는다.
