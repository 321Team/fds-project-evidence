# P1-SEC-01 — 보안 AC 잔여 원본 수집: kube-system PSA·CoreDNS dry-run·RBAC·30080 Source 시험·Secretbox backup (2026-10-02)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 이 수집은 #19에서 "이슈 코멘트로만 존재하고 서버 원본이 없던" 항목을 서버에서 다시 조회·실행해 원본으로 남긴 것이다. 관련 결정: [CR #125](https://github.com/321Team/fds-project-baseline/issues/125)(backup·rollback P1 필수, 예방 rotation `NOT MET / RISK ACCEPTED`), [CR #127](https://github.com/321Team/fds-project-baseline/issues/127)(AC-04 원본 유지, source-preservation 필수 하위조건).

## 출처와 수신

| 항목 | 값 |
|---|---|
| 수집 시각 (KST) | 2026-10-02 14:42(backup) · 14:52(증적 조회) · 15:14~15:17(30080 시험) |
| 수집·실행 | 이하영(P1-SEC-01 Lead)이 각 서버 콘솔에서 직접 실행. 스크립트 작성·수신 검증·편입 정리는 Claude Code 보조 |
| 수신 시각 | 2026-10-02 15:25 KST 이후, 공유 폴더 `p1-sec01-evidence/`를 거쳐 Claude Code 세션에서 수신 |
| 전달 경로 | 각 서버 → ansible01(`server01_ansible`)에서 `scp`로 취합(`~/p1-sec01-evidence/`, `infra-ansible` 작업 트리 밖) → 사용자가 공유 폴더에 배치 → 세션에서 수신 |
| 수신 검증 | 아카이브 5개 바이트 SHA-256이 서버가 만든 `.sha256` sidecar와 5/5 일치. 내부 `SHA256SUMS`(4개 아카이브) 전부 일치. backup 아카이브는 내부 Manifest가 없고 `11-backup-SHA256SUMS`를 포함한다 |
| 비밀정보 검색 | `password\|secret=\|token=\|BEGIN … KEY\|ENC_KEY\|bearer\|authorization:\|postgresql://` — 의미 있는 일치 0건. 일치 6줄은 명령 줄의 `secrets` 리소스 이름 2줄과 `etcdctl` 도움말 문구(`--password=password123` 예시 포함) 4줄이다 |

## 수집회차 구성

| 아카이브 | 실행 서버·계정 | 출발 Source / 대상 | 내용 |
|---|---|---|---|
| `p1-sec01-late-20261002T055244Z.tar.gz` | k8s-control01 · `server02` | — | PSA 라벨, CoreDNS server dry-run, monitoring-node 생성 권한, `prometheus-sa` 권한(23개 파일) |
| `p1-sec01-secretbox-backup-20261002T054208Z.evidence.tar.gz` | k8s-control01 · `server02`(sudo) | — | Secretbox 설정·etcd snapshot backup의 상태·해시(키·snapshot 본문 제외) |
| `p1-sec01-30080-approved-20261002T061754Z.tar.gz` | edge01 · `server08` | `10.1.93.50` → Worker `.105/.107/.108` `:30080`,`:32085` | 승인 Source 시험 |
| `p1-sec01-30080-unapproved-20261002T061432Z.tar.gz` | ansible01 · `server01_ansible` | `10.250.10.10`(관리망, mgmt-gw01 경유) → 동일 | 비승인 Source 시험 |
| `p1-sec01-30080-unapproved-20261002T061659Z.tar.gz` | k8s-control01 · `server02` | `10.1.93.102`(Worker와 같은 망) → 동일 | 비승인 Source 시험 |

`scripts/`에 실행한 스크립트 3개를 둔다(아래 "실행 스크립트 출처").

## 관측값 (원본 보존 — 판정 아님)

**PSA 라벨** (`late/10-ns-psa-labels.txt`)
- `kube-system`: `enforce=privileged`, `audit=restricted`, `warn=restricted`. version 라벨 없음.
- `fds-app`·`ci-cd`: `enforce/audit/warn=restricted` 및 세 모드 모두 `-version=v1.36`.
- `monitoring-api`: `enforce/audit/warn=restricted`. **version 라벨 없음.**
- `monitoring-node`: `enforce=privileged`, `audit/warn=restricted`. **version 라벨 없음.**

**CoreDNS dry-run** (`late/21-coredns-dry-run.txt`): `deployment.apps/coredns configured (server dry run)`, rc=0. `Warning: would violate PodSecurity "restricted:latest": runAsNonRoot != true …, seccompProfile …` 출력. `last-applied-configuration` 애노테이션 부재 경고도 함께 출력(server dry run이므로 변경 없음). 적용 대상 Deployment 원본은 `20-coredns-current.yaml`.

**monitoring-node 신규 Workload 생성** (`late/30-*`, 6개): `default:default`와 `monitoring-node:node-exporter-sa` 두 SA 모두 `deployments`·`daemonsets`·`pods` create = `no`. 비승인 SA는 `default` 기준이므로 "RBAC 미부여" 확인이며 Admission 차단 시험이 아니다.

**`prometheus-sa` 권한** (`late/40-*`~`49-*`)
- Prometheus Pod의 `serviceAccountName` = `prometheus-sa`. 구 SA `prometheus`는 `NotFound`(2026-09-27 infra-monitoring#20 SA 전환 이후).
- `nodes/metrics` get = yes. `nodes/proxy` = no, `nodes`(전체) = no, Secret get/list(`-A`) = no.
- ClusterRole `prometheus-sa-kubelet-metrics` rules: `nodes/metrics` `get`만(`48-…yaml`).
- Alertmanager Pod는 `alertmanager-sa`, Grafana Pod는 `grafana-sa`.

**30080 / 32085 Source 시험** (`results.tsv`, 각 6행, TCP connect 3초 timeout)

| Source | `:30080` (.105 / .107 / .108) | `:32085` (.105 / .107 / .108) |
|---|---|---|
| edge01 `10.1.93.50` (승인) | CONNECTED / CONNECTED / CONNECTED | TIMEOUT / TIMEOUT / TIMEOUT |
| ansible01 `10.250.10.10` (비승인) | TIMEOUT ×3 | TIMEOUT ×3 |
| k8s-control01 `10.1.93.102` (비승인) | TIMEOUT ×3 | TIMEOUT ×3 |

승인 Source에서는 `curl http://<Worker>:30080/readyz`가 3대 모두 `http_code=200`(약 8ms)이다.

**Secretbox backup** (`secretbox-backup/`)
- `/etc/kubernetes/enc/encryption-config.yaml`: mode 600, root:root, 274 B, SHA-256 `2b1c6cb4…63ecc`. `kube-apiserver.yaml` SHA-256 `2460bc9b…eada`.
- 설정 사본 2개의 백업 후 `sha256sum -c` 성공(`12-backup-verify.txt`).
- etcd snapshot: 9.0 MB, 620 keys, revision 3287996, etcd 3.6.0. snapshot 파일 SHA-256 `8ace820c…771e2f`, 상태 표는 `23-etcdutl-snapshot-status.txt`.

## 한계와 주의 (판정에 쓰기 전에 읽을 것)

1. **TIMEOUT은 차단 주체를 구분하지 않는다.** ansible01은 관리망이라 mgmt-gw01 방화벽을 거치므로 그 TIMEOUT만으로는 Worker의 Calico 정책(`nodeport-30080-allow`)이 막은 것인지 알 수 없다. 같은 망의 k8s-control01 시험으로 보완했으나, 이번에 GNP spec이나 host 정책을 다시 조회하지는 않았다(spec은 `received-20260926T034804Z`의 `p1-sec-01-originals-20260926T033752Z.tar.gz` 안 `20-gnp-nodeport-30080-allow.yaml`). `REFUSED`를 차단으로 읽지 않는다. 이번 결과에는 REFUSED가 없다.
2. **32085는 도달 불가만 관측했다.** listener 부재의 근거는 evidence#54 `b2-svc-after.yaml`(`transaction-api-nodeport` 30080만 노출)이다. 이번 시험이 정책과 listener 부재를 구분하지는 못한다.
3. **source-preservation(Pod에서 본 source IP)은 이 수집 범위가 아니다.** 해당 증적은 [received-20261001T034506Z](../received-20261001T034506Z/README.md)이다.
4. **`kube-apiserver.yaml.bak-preenc` 부재.** `10-config-state.txt`에 `/etc/kubernetes/manifests/kube-apiserver.yaml.bak-preenc`를 찾을 수 없다고 기록됐다. Gate2 실행 문서는 암호화 적용 전 manifest를 그 이름으로 백업했다고 적었다. 이번 `kube-apiserver.yaml.bak`는 **적용 후**(mtime 2026-09-22 09:40) 상태이며, 적용 전 manifest 위치는 확인하지 않았다.
5. **`21-etcd-snapshot-status.txt`는 도움말이다.** etcd 3.6의 `etcdctl`에는 `snapshot status`가 없어 상태 표 대신 usage가 출력됐다. 같은 snapshot을 `etcdutl snapshot status -w table`로 다시 확인한 결과가 `23-etcdutl-snapshot-status.txt`다(실행: control01 `server02`, `sudo kubectl exec etcd-k8s-control01`). 원본 `21`은 수정하지 않고 보존했다.
6. **backup 아카이브는 두 번 만들어졌다.** 첫 아카이브(SHA-256 `e9e72037…6a43`)는 `23` 파일 추가 전 상태였고 이후 같은 이름으로 다시 묶었다(`2bc0cdbe…2ae1`). 이 폴더에는 **두 번째 것만** 수신했다. 서버의 `.sha256` sidecar는 서버 절대경로(`/root/…`)를 적고 있어 `sha256sum -c`로는 검증되지 않으므로 해시 값만 대조했다.
7. **`.bak`와 etcd snapshot 본문은 편입하지 않는다.** 키·Secret이 들어 있어 control01 `/root/p1-sec01-secretbox-backup-20261002T054208Z/`에 root-only로 남아 있다. 이 PR이 보여 주는 것은 backup의 존재·크기·해시이며, **복원 가능성은 시험하지 않았다.** rollback 시험도 이번에 하지 않았다.
8. **`etcdutl` 상태 표의 `HASH 48214e62`는 etcd 내부 해시이며 파일 SHA-256이 아니다.**
9. **`collect-sec01-evidence.sh`는 한 번만 실행됐다.** 파일별 `# rc=`가 포함돼 있으며 `can-i`의 `no`는 rc=1이 정상이다.
10. **`edge01` 출발 Source의 `source_ips`에 `10.42.0.0/10.42.0.1`이 함께 기록됐다.** 시험에 사용된 출발 주소는 `10.1.93.50`이다(edge01의 기존 k3s 인터페이스 주소로 보이며 이 수집에서는 확인하지 않았다).

## 실행 스크립트 출처

| 파일 | SHA-256 | 출처 |
|---|---|---|
| `scripts/collect-30080-probe.sh` | `277f4af60d6dc00ba4debefdb3732d83a6b078165ba8b83ea6315804d61dabf8` | ansible01에서 만든 파일을 `scp`로 control01·edge01에 복사해 실행(복사 시 2,032 B 보고). 이 파일이 실행본이다 |
| `scripts/collect-sec01-evidence.sh` | `aeb62f4a170a4bf3f58613a04a5fda72c92c501181c5c3e314d4c94769a7c887` | 작성 원본. 서버에는 heredoc으로 붙여넣어 생성했고 실행본의 바이트 해시는 **미수신**. 줄 수(70)만 서버 `wc -l`과 일치 |
| `scripts/sec01-secretbox-backup.sh` | `7be5e4df55bc9f1b243f9c8f218ae131c25e52ca6287d3f7f7b05902a8fede03` | 위와 같음. 줄 수(47)만 일치 |

세 스크립트는 읽기·조회·접속 시도와 control01 로컬의 backup 파일 생성만 한다(클러스터 객체를 만들거나 바꾸지 않는다). 기존 `infra-*` 저장소에 있는 코드가 아니며 별도 리뷰를 받지 않았다. 따라서 이 수집은 "리뷰된 코드의 실행 결과"가 아니라 증적 수집용 조회 결과로 취급한다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 이 수집의 관련 파일 |
|---|---|
| AC-01 / 핵심요구 1: kube-system `enforce=privileged`, `audit/warn=restricted` | `late/10-ns-psa-labels.txt`, `11-kube-system-ns.yaml` (PSA version 라벨은 `monitoring-api`·`monitoring-node`에 없음을 관측) |
| 핵심요구 2: CoreDNS 실제 Manifest dry-run | `late/20-…yaml`, `21-coredns-dry-run.txt` |
| 핵심요구 3: monitoring-node 신규 Workload 생성 제한 | `late/30-*` |
| AC-03 / 핵심요구 5: Prometheus `nodes/metrics`만, `nodes/proxy`·Secret 금지 | `late/40-*`~`49-*` |
| AC-04 / 핵심요구 4 / IF-02: `.50/32`→Worker:30080만 허용 | 30080 시험 아카이브 3개 (Positive 1, Negative 2) |
| AC-05: backup | `secretbox-backup/` (rollback·rotation은 이 수집에 없음) |

AC 체크, Gate, 티켓 상태는 이 PR로 바꾸지 않는다. 판정은 Review Owner·Lead가 #19에서 별도로 한다.

## 이 편입이 하지 않는 것

- rollback 시험, Secretbox 복원 시험, 예방 rotation은 포함하지 않는다.
- IF-12A/B/C, IF-13A 등 Interface 흐름 시험은 포함하지 않는다.
- `fds-app`의 version 라벨을 포함한 PSA 위반 Pod 시험은 [received-20260926T152344Z](../received-20260926T152344Z/README.md)에 있다.
