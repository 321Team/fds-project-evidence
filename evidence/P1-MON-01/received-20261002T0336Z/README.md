# P1-MON-01 — monitor01 재부팅 자동 기동 설치·재부팅 시험 (2026-10-02 12:20~12:36 KST)

MON Lead(이재환)가 monitor01(`server01_monitor`)에서 실행했다. 코드는 [infra-monitoring#38](https://github.com/321Team/infra-monitoring/pull/38)(merge `ffa4809`, 권욱 승인·병합)이다.

**운영 변경:**
- 12:21 사용자 유닛 2개와 `images.env`를 설치했다. `~/fds-mon-tools/current` → `ffa4809` 링크를 만들었다.
- 12:21:20 `sudo loginctl enable-linger server01_monitor`
- 12:28 유닛 enable
- 12:29~12:30 monitor01을 재부팅했다(`sudo systemctl reboot`).
- 재부팅 중에는 외부 Watchdog과 heartbeat 수신이 끊겼다. 클러스터는 변경하지 않았다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `monitor01/` | `~/p1-mon-autostart-20261002/`(파일 9개, 그중 2개는 0 B) | `monitor01-autostart-20261002.tgz` 7,383 B, SHA-256 `1bc2607a…6588a4` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 9개도 서버 출력과 일치했다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 단 아래 1절의 빈 파일 2개(`units.tgz`·`python3.12`, 0 B)는 archive 안에만 두고 풀지 않았다(빈 `.tgz`가 archive 점검에 걸린다). 비밀 정보 검색 0건이다. `images.env`는 승인 digest만 담고 있다.

## 1. 설치

| 항목 | 결과 | 근거 |
|---|---|---|
| 전달 묶음 | `units.tgz` `eabf1db3…`(#38 `ffa4809` `monitor01/systemd/`의 3개 파일). 풀어 둔 `x/`의 SHA가 저장소와 같다: local `6283314f…`, nginx `5ef67862…`, `images.env` `d4bc669e…` | `x/` |
| 실행기 | `~/fds-mon-tools/ffa4809/runtime_launch_local.py` `d2708dfc…`(= `1e33a0b`의 같은 파일, #38은 실행기를 바꾸지 않았다). `current` → `ffa4809` | 설치 당시는 화면 출력뿐이었다. 원본 보강: [`received-20261002T0421Z` 1절](../received-20261002T0421Z/README.md)(`current` 링크 mtime 12:20:53, 첫 재부팅 전) |
| 유닛 환경 | PATH에 `/usr/bin`·`/usr/sbin`이 있다(podman·ss). `systemd-analyze --user verify` rc 0 | 화면 출력 |
| linger | `Linger=yes` | `boot-check.txt`(세션 1 `Class=manager`) |
| enable | `default.target.wants/`에 링크 2개(12:28), `is-enabled` enabled 2줄 | `boot-check.txt` |

### 설치 중 문제 — `systemctl --user` 연결 거부

- **현상:** 12:21 이후 `systemctl --user`가 "Failed to connect to user scope bus via local transport: 연결이 거부됨"으로 실패했다. 사용자 systemd(9/27부터 실행)와 dbus-broker는 살아 있었고, 컨테이너와 수신도 정상이었다(12:23 확인). 디버그 출력에서 실패한 연결은 `$XDG_RUNTIME_DIR/systemd/private`였다. 이 소켓 파일의 시각은 12:22였다.
- **우회:**
  - enable은 살아 있는 D-Bus(`busctl --user … EnableUnitFiles`, `Reload`)로 했다.
  - 유닛 restart 시험은 하지 않았다. rootless podman도 이 소켓을 쓰므로, 기존 컨테이너만 지우고 새로 만들지 못할 위험이 있었다.
  - 대신 재부팅으로 시험했다. 재부팅 뒤에는 `systemctl --user`가 정상이다.
- **원인(추정, 재현하지 않음 — NOT VERIFIED):**
  - `systemd-analyze --user verify`가 private 소켓 경로를 새 파일로 바꿨을 가능성이 높다.
  - 근거 1: 사용자 systemd 로그를 보면 12:21:11 `daemon-reload`는 private 소켓으로 정상 처리됐다. 그 직후 `verify` → linger(12:21:20) → `enable`이 이어졌고, `enable`부터 실패했다.
  - 근거 2: 12:22에 `daemon-reload; systemd-analyze --user verify`가 한 번 더 실행됐다(아래 터미널 재붙여넣기). 소켓 파일 시각 12:22가 이와 맞는다.
  - **Runbook: 실행 중인 사용자 systemd에서 `systemd-analyze --user verify`를 쓰지 않는다.**
- **터미널 재붙여넣기(12:22):**
  - 1·2단계 화면 출력이 그대로 셸에 한 번 더 붙여넣어졌다(셸 history로 확인, 파일 근거 없음).
  - 그 결과 프롬프트가 붙은 줄의 리다이렉션으로 `units.tgz`가 0 B로 덮였다. 출력 줄 `… /usr/bin/python3 -> python3.12`로 빈 파일 `python3.12`가 생겼다. 두 파일 모두 SHA `e3b0c442…`(빈 파일)다.
  - 나머지 줄은 같은 설치 명령의 재실행이었다(cp·ln·install 같은 값, `daemon-reload`·`verify`).
  - 아니면 명령이 아니라 실행되지 않았거나, 인자 없이 `podman`·`ss`가 실행됐다. 설정·데이터·컨테이너 변경은 없다.
  - 풀어 둔 `x/` 3개 파일은 12:20에 풀린 그대로이고, SHA가 저장소와 같다.

## 2. 재부팅 시험

| 시각(KST) | 사건 | 근거 |
|---|---|---|
| 12:29:35 | 재부팅 전: 컨테이너 3개 Up(receiver·blackbox 20시간, nginx 14시간), 부팅 9/27 21:16:53 | `reboot-pre.txt` |
| 12:30:45 | 부팅 | `reboot-post.txt`(`uptime -s`) |
| 12:30:50 | linger 사용자 systemd 세션 1(`Class=manager`) | `boot-check.txt` |
| 12:30:51 | `fds-monitor01-local` 시작. `ExecStartPre stop`이 이전 Exited 컨테이너 2개 제거(`LOCAL_SERVICES_STOPPED`) | `journal-boot.txt` |
| 12:30:53 | `LOCAL_SERVICES_STARTED`. receiver·blackbox 이미지 ID = 예상 config digest(`66416213…`·`f99053f6…`), listener `127.0.0.1:19090`·`127.0.0.1:9115`. 유닛 Finished | `journal-boot.txt` |
| 12:30:53~54 | `fds-monitor01-nginx` 시작. 이전 nginx 컨테이너 제거 → `NGINX_STARTED`(`a47dd5d8…`, `10.250.10.30:8443`). 유닛 Finished | `journal-boot.txt` |
| 12:30:54 | 첫 `10.1.93.108 POST /api/v1/write 204` | `journal-boot.txt` |
| **12:30:58** | **GUI 로그인 세션 3(tty2) — 두 유닛이 로그인 전에 기동 완료** | `boot-check.txt` |
| 12:31:19 | 두 유닛 `active/exited`, `Result=success`, `NRestarts=0` | `reboot-post.txt` |
| 12:32:02 | heartbeat 지연 14.9초, receiver alerts `[]`(Watchdog firing 없음), 컨테이너 3개 Up·listener 3개 | `reboot-post.txt` |

- 12:30:54~12:36:20 nginx 204만 있고 오류가 없다(`[warn]` client body buffering은 기존과 같다). receiver·blackbox `level=warn/error` 0건.
- **정확한 remote_write 수신 공백은 NOT MEASURED다.** 관측 창은 12:29:35(재부팅 전 캡처) → 12:30:54(재부팅 뒤 첫 POST)로 79초다. 재부팅 전 마지막 POST는 journal이 영구 저장이 아니어서 얻을 수 없었다. 재부팅 뒤 heartbeat 지연은 14.9초이고 Watchdog firing은 없었다. 보강 기록은 [`received-20261002T0421Z` 2절](../received-20261002T0421Z/README.md)에 있다.

## 판정 범위

- 이 기록은 #17 G8 monitor01의 "재부팅 뒤 자동 기동" 근거다. **AC 체크는 병합 뒤 따로 판단한다.**
- **범위 밖(Known Limitation):** 실행 중 컨테이너가 죽었을 때의 자동 재시작. 부팅 때 이전 컨테이너 로그는 회수와 함께 사라진다.
- **NOT RUN:** 유닛 restart 시험(위 사유로 재부팅 시험으로 대체), `systemd-analyze --user verify` 원인 재현.
