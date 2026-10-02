# P1-MON-01 — IF-06B `.108` 출발지 음성 시험 3건 시도: worker03 호스트 출발 트래픽 미도달 (2026-10-02 14:58~15:11 KST)

MON Lead(이재환)가 기존 접근으로 monitor01(`server01_monitor`), worker03(`server07`), control01(`server02`)에서 실행했다. 근거는 QA GO [#17 5946270938](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5946270938)(NON-MUTATING ACCEPTANCE PROBE)이고, 결과 보고는 [#17 5946545297](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5946545297)이다.

**운영 변경: 없다.** 새 SSH trust·firewalld rule·NetworkPolicy·GNP·Pod 변경은 없다. 한 일은 다음뿐이다.
- monitor01 tcpdump(헤더만, 14:58:41 시작 → 15:05 정지)
- worker03 curl 2회
- control01 조회와 Prometheus 작업용 port-forward(19095, 끝나고 정지)

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `monitor01/` | `~/p1-mon-108-20261002T145837/`(파일 6개) | `monitor01-108-20261002.tgz` 961 B, SHA-256 `9d2411d6…1072f8cb` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 6개도 작업 중 서버 출력과 일치했다 |
| `worker03/` | `~/p1-mon-108-20261002T145903/`(파일 2개) | `worker03-108-20261002.tgz` 2,017 B, SHA-256 `61c07f69…10811d13` | 같은 방식 |
| `control01/` | `~/p1-mon-108-post-20261002T150702/`(파일 2개) | `control01-108-20261002.tgz` 728 B, SHA-256 `a4c6ee1f…965e82ee` | 같은 방식. `hep-gnp.txt`는 15:10 화면 조회와 같은 내용을 15:11에 파일로 다시 남긴 것이다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다.

비밀 정보 검색 0건이다.
- `fds-root-ca.crt`는 승인 Root CA 공개 인증서다(SHA-256 `20ddfa5e…`).
- 잘못된 인증 값은 그 자리에서 만든 임의 값이고, 파일·화면에 남기지 않았다(`unset`).
- tcpdump는 `-q` 헤더 요약만 출력했고 payload 옵션은 쓰지 않았다.

## 1. 시험

| 시각(KST) | 위치 | 항목 | 결과 | 근거 |
|---|---|---|---|---|
| 14:58:41 | monitor01 | firewalld runtime·permanent·direct 사전 기록, tcpdump 시작 (`ens160`, `src .108 → dst .30` 443·8443 SYN만) | `listening on ens160` | `fw-pre.txt`, `tcpdump.txt` |
| 14:59:15 | worker03 | `ip -4 route get 10.250.10.30` | `via 10.1.93.58 dev ens160 src 10.1.93.108` | `test.txt` |
| 14:59 | worker03 | CA 대조 | `20ddfa5e…` 일치 | `fds-root-ca.crt` |
| 14:59:15→15:01:29 | worker03 | T1 `.108 → .30:443` 잘못된 인증 POST(`--cacert`, `-k` 없음) | **연결 안 됨**: curl rc 28, 133초, `http=000` | `test.txt` |
| 15:01:29→15:01:34 | worker03 | T2 `.108 → .30:8443` 직접 | 연결 안 됨: rc 28, 5초 | `test.txt` |
| 15:05 | monitor01 | tcpdump 정지 | **0 packets captured** — 위 SYN이 monitor01 `ens160`에 도착하지 않았다 | `tcpdump.txt` |
| 15:05:31 | monitor01 | firewalld 사후, nginx, heartbeat | firewalld diff 없음(`fw_diff_rc=0`), nginx 4xx/5xx 0, `10.1.93.108 204` 30분 150건, heartbeat 지연 14.4초, receiver alerts `[]` | `fw-post.txt`, `fw-diff.txt`, `post.txt` |
| 15:07:09 | control01 | 클러스터 | `count(up)` 23 / `up==1` 23, remote write 30분 failed 0·retried 0·samples 120 | `cluster-post.txt` |

## 2. 원인 — worker03 HostEndpoint egress (`control01/…/hep-gnp.txt`)

- HostEndpoint `fds-k8s-k8s-worker03`: node `k8s-worker03`, interface `ens160`, expectedIPs `10.1.93.108`.
- GlobalNetworkPolicy `fds-k8s-host-k8s-worker03`: types Ingress·Egress, order 100, `applyOnForward=false`.
  - egress 허용은 `10.1.93.109:6443`, VXLAN 4789(노드 6대), DNS `.52/.53:53`(UDP·TCP), NTP `.102:123`, Harbor `.54:443`, CP `.102~.104:6443`뿐이다. 마지막 규칙은 `Deny`다.
  - **`10.250.10.30`은 허용 목록에 없다.**
- 따라서 worker03 **호스트 프로세스**(curl)가 보낸 SYN은 worker03에서 버려진다.
- in-cluster Prometheus Pod의 remote write는 포워딩 트래픽이고 `applyOnForward=false`라 이 정책을 거치지 않는다. 그래서 SNAT된 `.108` 출발지로 계속 도착한다(204 지속).
- 버려지는 순간의 Calico drop 카운터·로그는 수집하지 않았다. 따라서 원인은 "HostEndpoint/GNP 구성과 관측 결과(SYN 미도달, Pod 트래픽만 도달)가 일치하므로 worker03 호스트 egress 정책에 의해 차단된 것으로 판단"하는 수준이다.
- 기존 `icr39-probe/probe-w03` Pod는 hostNetwork가 아니고 이미지가 `calico/node`다. 출발지와 도구가 이 시험에 맞지 않아 쓰지 않았다.

## 판정 범위

| 항목 | 판정 |
|---|---|
| `.108 → .30:443` 잘못된 인증 401 (SEC 마지막 조건) | **NOT VERIFIED** — 요청이 nginx에 도달하지 않았다 |
| `.108 → .30:8443` 직접 차단 | **NOT VERIFIED** — 연결은 실패했지만 443도 같은 원인으로 막혀 있어 monitor01 쪽 차단의 근거가 아니다 |
| tcpdump 출발지 `.108` 보존 | **NOT VERIFIED** — 도착 패킷 0건 |
| 시험 무영향 | PASS — firewalld diff 0, 204 지속, heartbeat·Watchdog 정상, Target 23/23, remote write 실패·재시도 0 |

- GO 조건(새 NP·Pod 변경 금지) 안에서는 worker03 호스트에서 이 시험을 할 수 없다. 경로는 QA에 결정을 요청했다. 정해진 경로로 다시 시험하면 새 수집회차로 추가한다.
- 이 기록으로 #17 AC를 바꾸지 않는다.
