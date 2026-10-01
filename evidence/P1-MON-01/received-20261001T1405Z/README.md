# P1-MON-01 — monitor01 Gate F·receiver·blackbox·nginx 기동, IF-06B 수신 경로 (2026-10-01 15:00~23:05 KST)

MON Lead(이재환)가 monitor01(`server01_monitor`, rootless podman)과 k8s-control01(`server02`)에서 실행했다. ansible01(`server01_ansible`)은 tar 전달과 읽기 전용 조회에만 썼다.

- 결과 코멘트: [#17 layer 9/9](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5925731715), [#17 receiver·blackbox 기동](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5926685322), [#17 IF-06B 수신 경로](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5932866798)
- 승인·결정: [Gate F A안](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5924380025), [QA 재점검](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5927493560), [SEC 승인](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5927558258), [조건 수용](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5927596564)
- 실행기: infra-monitoring [#33](https://github.com/321Team/infra-monitoring/pull/33)·[#34](https://github.com/321Team/infra-monitoring/pull/34)·[#35](https://github.com/321Team/infra-monitoring/pull/35)·[#36](https://github.com/321Team/infra-monitoring/pull/36)(모두 GWONUK APPROVED·병합)

**운영 변경(monitor01):** rootless 컨테이너 3개 기동(receiver·blackbox·nginx), 9/27 rootful 설정·데이터 폴더 이름 변경 보존(`*.20260927-rootful-hold`, 삭제 없음), `/etc/fds` 700→711, 새 설정·데이터 폴더, SELinux `container_read_certs` on, 키 ACL(키 1개 읽기·상위 3개 폴더 통과), firewalld rich rule 1줄. **운영 변경(클러스터):** Secret `monitoring-api/monitor01-remote-write-auth`의 `password` 값 교체(값 기록 없음). 그 밖의 클러스터 변경 없음.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `monitor01/` | `~/p1-mon-layercheck-20261001T150019/`, `~/p1-mon-g8pre-20261001T150717/`, `~/p1-mon-sec1-20261001T173311/`, `~/p1-mon-sec2-20261001T173851/`, `~/p1-mon-sec2-20261001T173920/`, `~/p1-mon-nginx-20261001T222357/`, `~/fds-mon-tools/{receiver,blackbox}-cfg-20261001/` 설정 3개(파일 35개) | `monitor01-g8-20261001.tgz` 12,658 B, SHA-256 `386c3652…aec67c68` | 23:05 KST 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 35개 중 33개는 작업 중 서버가 출력한 SHA-256과도 일치했다(나머지 `state-final.txt`·`nginx-access.log`는 묶기 직전 생성) |
| `control01/` | `~/p1-mon-nginx-manifest-20261001T163143/`, `~/p1-mon-sec2-20261001T174149/`, `~/p1-mon-rw-check-20261001T230313/`(파일 7개) | `control01-g8-20261001.tgz` 3,696 B, SHA-256 `30415807…b7f306` | 같은 방식. 개별 파일 6개(`pf.log` 제외)가 작업 중 출력과 일치 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 이미지 tar·base64·임시 압축 파일은 묶지 않았다.

**비밀 정보:** 비밀번호·htpasswd 해시·개인키 본문·Authorization 헤더·쿠키는 없다(편입 전 검색 0건). `monitor01/p1-mon-g8pre-20261001T150717/sudo-ro.txt`에는 개인키 **파일의 SHA-256**(`204e9db9…`)이 있다. 해시만으로 키를 복원할 수 없어 그대로 둔다. htpasswd는 파일 SHA·권한·사용자 이름만, Secret은 resourceVersion·키 이름만 있다. `control01/…/root.crt`는 공개 Root 인증서다(SHA-256 `20ddfa5e…053f`).

## 1. Gate F — 이미지 동일성(A안: Harbor manifest → config.digest → archive config → 로컬 이미지 ID)

| 구성 | Harbor digest | 예상 config = 로컬 ID | 근거 파일 |
|---|---|---|---|
| receiver Prometheus 3.15.0 | `fds/prometheus@sha256:2c28708b…` | `66416213…` | `p1-mon-layercheck-…/result.txt`(tar `5397a917…` PASS, config PASS, **layer diff_ids 9/9**, 로컬 ID·RootFS 9 PASS), `g8pre/verify-receiver.json`(IMAGE_IDENTITY_MATCH), `g8pre/precheck.txt`(3.15.0 rev `5241a27f`, `promtool` 1 rule files·1 rules) |
| blackbox 0.28.0-master.065fc18 | `fds/blackbox-exporter@sha256:5969ff6a…` | `f99053f6…` | `g8pre/bb-load.txt`(tar `8dbf198d…` PASS, load, MATCH, rev `065fc188`, `--config.check` OK) |
| nginx 1.31.6 | `fds/nginx@sha256:cbb0d105…` | `a47dd5d8…` | `control01/p1-mon-nginx-manifest-…/manifest.json`(raw manifest SHA = `cbb0d105…`, `config.digest` = `a47dd5d8…`), `g8pre/nginx-load.txt`(tar `e7be0c8e…` PASS, MATCH, uid_map) |

- blackbox는 ansible01 빌드 tar(image ID `f99053f6` = Harbor 승인본 config)를 썼다. BUILD.md의 "승인 digest 재-pull → tar" 단계는 A안(config 동일성) 근거로 생략했다([#17 5926685322](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5926685322)).
- local RepoDigest(receiver `b3526e4e…`, blackbox `a819d556…`, nginx `3b0de96e…`)는 전송 과정의 local 값이라 기록만 한다.
- ansible01 쪽 출력은 파일로 저장하지 않았다. 아래는 사용자 화면 출력을 옮긴 것이다(파일 근거 없음): 빌드 tar `8dbf198d…`·`image-id.txt` `f99053f6…`·manifest Config `f99053f6….json`, nginx tar `e7be0c8e…`·Config `a47dd5d8….json`·User 65532, Gate-F 키 지문 `SHA256:I6QessOx…`로 blackbox·nginx `scp_rc=0`.

## 2. receiver·blackbox 기동 (`monitor01/p1-mon-g8pre-20261001T150717/`)

| 파일 | 내용 |
|---|---|
| `check.txt` | 15:07 기동 전 조회. `/etc/fds` 700으로 접근 불가, 데이터 폴더 `nobody`, 실행기·컨테이너 없음 |
| `sudo-ro.txt` | sudo 읽기 전용 조회. 9/27 rootful 설정(`receiver.prometheus.yml` 등)·데이터(580K)·rootful 컨테이너 2개 Exited(직접 pull 이미지) |
| `host-prep.txt` | 15:21 9/27 폴더 이름 변경 보존, `/etc/fds` 711, 새 `prometheus.yml`(`a3b2e89d…`), 데이터 폴더 `rules/watchdog.rules.json`(`56268535…`), `podman unshare chown 65534` |
| `bb-prep.txt` | blackbox 설정 저장소본(`82240e64…`)으로 교체, 9/27 폴더 보존 |
| `start.json` | 15:27 첫 `start` STOP(`listener 19090 missing`) → 실행기 결함(#34) |
| `diag.txt` | 같은 argv 단독 기동: 2초부터 `127.0.0.1:19090` listen, 오류 없음 → 확인 시점 문제 |
| `start2.json`, `post-start2.txt` | 16:18 #34 병합본으로 기동 성공. localhost-only, ready/healthy 200, Watchdog rule ok(firing — heartbeat 없음), `probe_success{10.1.93.109:6443}` = 1 |
| `nginx-pre.txt` | 인증서·키 공개키(`175f4b5d…`), `container_read_certs` off, firewalld 초기 상태 |

receiver 설정(`fds-mon-tools/receiver-cfg-20261001/`)은 `render_candidate.py` 출력에 `receiver-scrape-blackbox.json`을 합친 것이다. 실행기가 설정 파일 하나만 마운트하므로 `rule_files`는 데이터 폴더 `rules/`를 가리킨다.

## 3. 보안 설정 1·2·3 (SEC 승인·QA 조건)

| 단계 | 파일 | 결과 |
|---|---|---|
| 1. SELinux·키 ACL(17:33) | `p1-mon-sec1-…/pre.txt`·`apply.txt`·`post.txt`·`diag.txt` | 변경 전 off·ACL 없음 → on, 상위 3개 폴더 `server01_monitor:--x`, 키 `589819:r--`. 라벨 `cert_t`·소유자·공개키 해시 불변. `server01_monitor` 직접 읽기 거부, 컨테이너 uid 65532 읽기 가능(`cat_rc=0`), 65534 거부, AVC 0. `post.txt`의 uid 65532 `DENIED`는 busybox `test -r`가 ACL을 보지 않아 생긴 오판이다(`diag.txt`에서 확인) |
| 2. Basic Auth(17:39, 17:42) | `p1-mon-sec2-20261001T173851/`(htpasswd), `control01/p1-mon-sec2-20261001T174149/`(Secret rv `2238223`→`3097769`) | 같은 변경창. `monitor01/p1-mon-sec2-20261001T173920/`은 Secret 교체 명령을 monitor01에서 잘못 실행한 기록(kubectl 없음, 변경 없음)이다 |
| 3. firewalld(22:33) | `p1-mon-nginx-…/fw-pre.txt`·`fw-apply.txt`·`fw-post.txt` | rich rule 1줄(`.108/32` → `.30/32` 443→8443) runtime·permanent 같음. services·ports·masquerade 불변 |

## 4. nginx 기동과 인수 시험 (`monitor01/p1-mon-nginx-20261001T222357/`)

| 파일 | 내용 |
|---|---|
| `p1-mon-sec2-20261001T173920/check-nginx.json` | 17:39 #35 병합본 `check-nginx` 실패(`--network none`에서 bind 99) → #36으로 수정 |
| `check-nginx.json` | 22:23 #36 병합본 `NGINX_CONFIG_OK` |
| `start-nginx.json` | 22:39 `NGINX_STARTED`, listener `10.250.10.30:8443`만 |
| `accept-local.txt` | 22:40 TLS1.2/1.3 verify 0, TLS1.0/1.1 서버 거부(alert 70), 405/400/404, `.30` POST 403, **receiver `fds_monitoring_heartbeat` = 1, Watchdog inactive** |
| `nginx-access.log` | 23:05 수집. `10.1.93.108 POST /api/v1/write 204` 반복(출발지 보존), 첫 `.108` 400 1건 |
| `state-final.txt` | 23:05 컨테이너 3개 Up, listener 3개 |
| `control01/p1-mon-rw-check-…/rw-check.txt` | 23:03 클러스터 Prometheus: 최근 15분 샘플 60·실패 0·재시도 0, 전송 지연 0초. 첫 400 원인 `out of bounds`(오래된 샘플 1개). 로그 시간 순서 `no route to host` → `connection refused`(rule 적용 후 nginx 전) → 204 |

ansible01(비승인 출발지 `10.250.10.10`) TCP 443·8443 차단은 화면 출력만 있다(파일 없음).

## 판정 범위

- 이 기록은 Gate F 수용 조건 1~3과 IF-06B 경로 기동·일부 인수 시험의 근거다. **#17 AC 체크는 이 기록만으로 바꾸지 않는다.**
- **NOT RUN / NOT VERIFIED:** `.108` 출발지의 잘못된 인증 401과 `.108 → .30:8443` 직접 접속 차단, tcpdump 출발지 확인(ICR 경로 필요), heartbeat 5분 단절·복구, API-LB 실패·복구 회귀, 재부팅 자동 기동, Gate-F 임시 키 정리.
- 되돌리는 방법: `stop-nginx`·`stop`(실행기), `--remove-rich-rule`(이번 rule), `setsebool -P container_read_certs off`, `setfacl -b`(키와 상위 3개 폴더), 9/27 폴더 이름 원복. 삭제는 하지 않는다.
