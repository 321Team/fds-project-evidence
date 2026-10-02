# P1-MON-01 — monitor01 실행기 연결·수신 공백 보강, Gate-F 임시 키 정리, 자동 기동 되돌리기 시험 (2026-10-02 13:06~13:21 KST)

MON Lead(이재환)가 monitor01(`server01_monitor`)과 ansible01(`server01_ansible`)에서 실행했다. 앞 수집회차 [`received-20261002T0336Z`](../received-20261002T0336Z/README.md)(재부팅 자동 기동)의 리뷰 BLOCKER 2·3 보강과, #17 잔여 항목 2개(Gate-F 임시 SSH 키 정리, #38 rollback)의 기록이다.

**운영 변경:**
- 13:06 monitor01 `~/.ssh/authorized_keys`(Gate-F 키 한 줄)를 삭제했다.
- 13:09:17~21 monitor01 유닛을 `disable --now` → `enable --now`로 되돌렸다가 복구했다. 컨테이너를 회수하고 다시 기동했다.
- 13:11 ansible01 `~/.ssh/p1_mon_gatef_ed25519`(+`.pub`)를 삭제했다. 개인키는 `shred -u`로 지웠다.
- **13:17:51 monitor01이 다시 부팅됐다.** 계획된 시험이 아니며 원인은 이 기록 범위 밖이다. 유닛이 자동으로 다시 기동했다(아래 1절).
- 그 밖의 변경은 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `monitor01/` | `~/p1-mon-gatef-cleanup-20261002T130611/`, `~/p1-mon-rollback-20261002T130917/`(파일 5개) | `monitor01-gatef-rollback-20261002.tgz` 1,176 B, SHA-256 `0ce845d9…91b0054d` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일도 작업 중 서버 출력과 일치했다 |
| `monitor01/` | `~/p1-mon-autostart-binding-20261002T132030/`(파일 2개) | `monitor01-autostart-binding-20261002.tgz` 1,599 B, SHA-256 `8c4ed003…62fcc8d` | 같은 방식 |
| `ansible01/` | `~/p1-mon-gatef-cleanup-20261002T131123/`(파일 3개) | `ansible01-gatef-cleanup-20261002.tgz` 852 B, SHA-256 `9bca9f11…bd00fba1` | 같은 방식 |

- archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다.
- 비밀 정보 검색 0건이다.
  - `*.removed.pub`·`authorized_keys.gatef-removed.pub`는 공개키 한 줄이다.
  - ansible01 `post.txt`의 `ls -l ~/.ssh`는 다른 키 파일의 이름·크기·시각만 보여 주고 내용은 없다.
  - 개인키 본문은 어디에도 출력하지 않았다(`ssh-keygen -y`의 공개키를 fingerprint로만 변환).

## 1. 실행기 연결 (0336Z BLOCKER 2) — `monitor01/p1-mon-autostart-binding-20261002T132030/binding.txt`

| 항목 | 값 |
|---|---|
| `readlink -f ~/fds-mon-tools/current` | `/home/server01_monitor/fds-mon-tools/ffa4809` |
| `current` 링크 mtime/ctime | **2026-10-02 12:20:53.786** — 첫 재부팅(12:30:45) 전 설치 시각이다. 재부팅 뒤에 링크를 바꾸지 않았다 |
| `ffa4809/runtime_launch_local.py` | SHA-256 `d2708dfc…0caf7e86`, mtime 2026-10-01 22:23:57(원본 `1e33a0b` 복사본의 `cp -p` 보존 시각), ctime 12:20:48(복사 시각) |
| `current/…`·`ffa4809/…`·`1e33a0b/…` | 세 경로 모두 `d2708dfc…`로 같다 |
| 저장소 대조 | infra-monitoring merge `ffa4809`의 `monitor01/runtime_launch_local.py` = `d2708dfc61c9dc16bd4692ec04e6126687fe215053ea5969d27e88ed0caf7e86`(#38은 실행기를 바꾸지 않았고 `1e33a0b`와 같은 blob) |
| 유닛이 부른 경로 | local `ExecStartPre`/`ExecStart` = `/usr/bin/python3 /home/server01_monitor/fds-mon-tools/current/runtime_launch_local.py stop`/`start …`, nginx = `stop-nginx`/`start-nginx …`. 13:17:57~13:18:00 실행, 모두 `status=0` |

- 이 파일은 두 번째 부팅(13:17:51) 뒤에 수집했다. 링크 시각이 두 부팅보다 모두 앞서고, 수집 시점의 대상 파일 SHA가 저장소와 같다.
- 그래서 두 부팅 모두 같은 실행기를 불렀다고 판단한다. 첫 부팅 시점의 파일 SHA를 그 순간에 찍은 기록은 없다.

## 2. 수신 공백 (0336Z BLOCKER 3) — `monitor01/p1-mon-autostart-binding-20261002T132030/gap.txt`

- monitor01 journal이 영구 저장이 아니다(`no persistent journal was found`, 부팅 목록 1개). 그래서 첫 재부팅 전 마지막 nginx POST 시각은 **얻을 수 없다**.
- **정확한 remote_write 수신 공백은 NOT MEASURED다.** 관측 창은 12:29:35(재부팅 전 캡처) → 12:30:54(재부팅 뒤 첫 `.108 POST 204`)로 79초다.
- receiver의 `fds_monitoring_heartbeat` 원본 샘플(12:27:02~12:32:47)은 15초 간격으로 빠짐없이 있다(`MAX_SAMPLE_GAP_SEC 15.000`).
  - monitor01이 내려가 있던 동안의 샘플도 들어 있다. 클러스터 Prometheus가 재연결 뒤 밀린 샘플을 다시 보낸 결과로 본다.
  - 따라서 이 연속성은 수신 공백의 측정값이 아니라 "데이터 손실 없음"의 근거로만 쓴다.
- 두 번째 부팅의 첫 POST는 13:17:59.76이다(부팅 13:17:51, 유닛 Exec 13:17:57~13:18:00).

## 3. Gate-F 임시 SSH 키 정리

| 위치 | 사전 | 사후 |
|---|---|---|
| monitor01 `~/.ssh/authorized_keys` (13:06) | 1줄, `SHA256:I6QessOxwXgnc9fAlF9sMMyyOqJ7y0cPVQRZwhTaoh8` `P1-MON-01 Gate-F ansible01-to-monitor01 2026-09-30`. sshd `authorizedkeysfile .ssh/authorized_keys`, `authorizedkeyscommand none` | 파일 없음(`AUTHKEYS=ABSENT`), `gatef_fingerprint_count=0`. 9/30 등록 전에도 파일이 없었으므로 원래 상태로 돌아갔다 |
| ansible01 `~/.ssh/p1_mon_gatef_ed25519` (13:11) | 공개키·개인키에서 얻은 fingerprint가 모두 `I6Qess…oh8`. `~/.ssh/config` 참조 없음 | `PRIVKEY=ABSENT`, `PUB=ABSENT`, `gatef_pub_count=0`, `gatef_priv_count=0` |

- 삭제한 공개키 백업(`aa9d838c…`, `029dbb5e…`)은 9/30 등록 내용과 같다.
- monitor01 쪽 정리 명령(②)은 두 번 실행됐다. 두 번째는 파일이 이미 없어 `cp`만 실패했다. `post.txt`는 두 번째 실행 결과(13:06:43)이고 판정은 같다.

## 4. #38 되돌리기·복구 시험 — `monitor01/p1-mon-rollback-20261002T130917/`

| 시각 | 단계 | 결과 |
|---|---|---|
| 13:09:17 | 사전 | 두 유닛 `enabled`, 컨테이너 3개 Up 38분 |
| 13:09:17→18 | 되돌리기 `disable --now`(README 되돌리기 절차의 서비스 부분) | rc 0, `default.target.wants` 링크 2개 제거, `disabled`·`inactive`, 컨테이너 0개, `NO_LISTENERS` |
| 13:09:18→21 | 복구 `enable --now` | rc 0, `active` 2개, 컨테이너 3개 Up(이미지 ID `66416213`·`f99053f6`·`a47dd5d8`), listener 3개 |
| 13:09:49 | 수신 | heartbeat 지연 17.2초, receiver alerts `[]` |

- linger 해제와 설치 파일 삭제(되돌리기 절차의 나머지)는 실행하지 않았다. 자동 기동을 계속 쓰기 위해서다.

## 판정 범위

- 1·2절은 `received-20261002T0336Z` 리뷰 BLOCKER 2·3의 보강이다. 0336Z README도 이에 맞춰 고쳤다.
- 3절은 #17 잔여 "Gate-F 임시 SSH key cleanup 및 exact fingerprint 0건"의 기록이다(monitor01·ansible01 기준). 다른 호스트에 같은 키가 복사됐는지는 확인하지 않았다(NOT VERIFIED). 생성·사용 경로는 ansible01 → monitor01뿐이었다.
- **AC 체크는 병합 뒤 따로 판단한다.**
