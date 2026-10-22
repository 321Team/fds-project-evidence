# P2-VPN-01 — 창 A(터널·DB 사전 창·T3/T6/T3-R) 실행 원본, 2026-10-20

출처 티켓: [fds-project-baseline#37](https://github.com/321Team/fds-project-baseline/issues/37) (P2-VPN-01). DB 사전 예외는 [#47](https://github.com/321Team/fds-project-baseline/issues/47) 도구(infra-db `57f050ef`)를 썼다.

VPN_RUN `20261020T1430` 터널 위에서 DB_RUN 두 회차를 열고 닫았다.
- `20261020T1430`: T3
- `20261020T1730`: 추가 1회, T6·T3-R

창이 끝날 때 db01·VPN 양쪽·probe·route를 모두 원복했다. #7(NetworkPolicy B/A)·N3·C7 ② 분류는 이번 창에서 실행하지 않았다.

## 기록 연결

| 단계 | GitHub 기록 |
|---|---|
| 창 A·db01 사전 창·probe 비용 GO / P1·P2 Apply GO(W1 최후 16:15) | [#37 6283339322](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6283339322) / [6285186087](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6285186087) |
| 진행 기록 1(G·V1·T1) / 2(W0~W4) | [6284350183](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6284350183) / [6285894013](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6285894013) |
| 추가 1회 GO(T6·T3-R, DB 최대 70분) | [6286351296](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6286351296) |
| 추가 1회 결과 | [6286925448](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6286925448) |
| vpn-gw01 V9 순서 이탈 보고 | [6287464471](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287464471) |
| 하영 P9·P8 결과 | [6287528544](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287528544) |
| 최종 정리 보고 / 세션 History / RPM 정정 | [6287648840](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287648840) / [6287684201](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287684201) / [6287844835](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287844835) |
| 권욱 원본 검토(3/3) / RPM 정정 수신 | [6287774429](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6287774429) / [6288109333](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6288109333) |

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이재환. Relay·probe: CloudShell `netop` 프로필(MFA) → `assumed-role/FDS-Network-Operator/321team-jaehwan` → SSM. vpn-gw01·db01: `server08` + sudo |
| 원복 인수자 | 이권욱 |
| 코드 | VPN: Stage B 묶음 `p2-vpn-01-stageb.tgz` `358624f5…bbaf`(infra-vpn 실행 코드와 같음, [ev239](https://github.com/321Team/fds-project-evidence/pull/239) `package/`). DB: infra-db `57f050ef` `db01-rosa.sh` `3f7f95f6…70d8`, `apply.sh` `c893d058…b245` |
| 대상 | Relay `i-05e4b63d31d8d5ac5`, vpn-gw01 10.1.93.51, db01 10.1.93.55, probe `i-0e77e222635031388`(10.20.10.150, 하영 P1 생성·P9 삭제) |
| 시각(KST) | G 14:34 → V1·T1 14:46 → W1 16:09:47 → T3 16:12:20 → W4 16:33:48 → 추가 W1 17:09:48 → T6 17:24 → T3-R 17:26:23 → W4 17:28:17 → P9 17:47 → vpn-gw01 V9 18:00:32 → P8 18:08 → Relay V9 18:10:13 → Active 세션 0 18:11:39 |

## 파일

| 경로 | 출처 수준 | 내용 |
|---|---|---|
| `db01/p37-db01-20261020.tgz` (+ `.sha256`) | db01에서 묶어 scp로 받은 **원본** archive, 3,876 B `e2ec4cff…a6a5` | 두 RUN 폴더(파일 22개, 디렉터리 4개) |
| `db01/p2-hyb01-rosa-20261020T1430/` | 위 archive를 푼 파일(바이트 동일) | `check` 3회·`pre-apply`·`pre-rollback` 로그, `pre.receipt`, SYN 관측 `capture/`(시작·PID·`syn.txt`·`syn.err`, 수동 `capture-exit.txt`) |
| `db01/p2-hyb01-rosa-20261020T1730/` | 같음 | `check` 2회·`pre-apply`·`pre-rollback`, `pre.receipt`, `capture/`(`capture_rc=0` 자동 기록), T6 db01 캡처 `t6-db01.txt` |
| `rpm/p37-rpm-reconcile-20261020.tgz` (+ `.sha256`) | CloudShell 다운로드 **원본** archive, 1,374 B `2f67c549…6e2d` | `cloudshell-rpm-20261020T1430.log` |
| `rpm/cloudshell-rpm-20261020T1430.log` | 위 archive를 푼 파일(바이트 동일) | 10/21 18:25 Relay 조회만: rpm 전후 파일·`dnf history` 7(`undo 6` Success)·현재 목록 해시 |
| `vpngw01/t6-journal-vpn-gw01-20261020T1730.sanitized.txt` | **정제본**(아래 SPI 정제) | vpn-gw01 T6 구간 `journalctl -u ipsec` 12줄 |
| `cloudshell/cloudshell-20261020T1430.log` | 원본 바이트 그대로 | 14:30 창 `script` 로그(G~V1, 14:46 Relay apply 부근까지) |
| `cloudshell/cloudshell-v9-20261020T1430.sanitized.log` | **정제본** | Relay V9 rollback·`check`, T6 Relay 원본(eth0 캡처·journal) 출력, Active 세션 조회 |
| `cloudshell/eni-*.tsv` 3개 | 원본 바이트 그대로 | ENI 목록 G(14:34)·W1(16:07)·추가창 W0(17:06). W1과 W0는 같은 바이트 |
| `vpngw01/redact_spi.py` | 정제에 쓴 스크립트 | 아래 정제 기록 |

### SPI 정제 (카드 rev3 §4)

[T3·T6 카드 rev3](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6120204407) §4는 공개 증적에 PSK·SPI를 지운 정제본만 두고, 전체 원본은 비공개 전달 경로에 두게 한다. 그래서 SPI가 들어 있는 두 파일은 정제본만 넣었다. 그 파일이 들어 있는 원 archive 두 개(`p37-vpngw01-20261020.tgz`, `p37-windowA-20261020-cloudshell.tgz`)도 이 폴더에 넣지 않았다. **원본은 고정 비공개 폴더 `02차 프로젝트\window-a-jaehwan-20261020\`에 그대로 있다.**

| 정제본 | 원본(비공개 폴더) | 바뀐 것 |
|---|---|---|
| `t6-journal-vpn-gw01-20261020T1730.sanitized.txt` 1,884 B `eedfa056f17daea163cb3cec1237d448cd0a15c29aaafc393e632022d79039f0` | `p37-vpngw01-20261020.tgz`(828 B `8831ea22…5a78`) 안의 `t6-journal-vpn-gw01-20261020T1730.txt` 1,872 B `f203c08515f48aa05ab125e50cf8634078df46027016dcffcdf1e4035ed8d366` | `<0x…`·`>0x…` SPI 3곳 → `0xSPI_REDACTED` |
| `cloudshell-v9-20261020T1430.sanitized.log` 6,303 B `2b2a4128c5f791cf192b62c8d813a287b9963cc342bc456eaf9cfd5c86291ca5` | `p37-windowA-20261020-cloudshell.tgz`(5,401 B `9296f5e8…7915`) 안의 `cloudshell-v9-20261020T1430.log` 6,291 B `1266585279dd6d6d1d3163f172ab9a692bee890d1419db8f1633a70a2f941743` | `SPI=…` 1곳, `<0x…`·`>0x…` 2곳 → `SPI_REDACTED` |

- 변환 명령: `python -I redact_spi.py <원본> <정제본>`. 정규식 `SPI=[0-9a-f]{8}` → `SPI=SPI_REDACTED`, `([<>])0x[0-9a-f]{8}` → `\10xSPI_REDACTED`. 그 밖의 바이트(CR·ANSI 제어문자 포함)는 그대로다.
- 정제하지 않은 나머지 cloudshell 파일 4개(`cloudshell-20261020T1430.log`, `eni-*.tsv` 3개)는 원 archive 안의 파일과 바이트가 같다(`cmp` 일치).
- PSK·secrets 내용·xfrm 키는 어느 파일에도 없다. PSK는 `read -s`로 넣어서 로그에는 `PSK 입력(표시 안 됨)` 문구만 있다. MFA 코드·IMDS 토큰 값도 찍히지 않았다. 64자 hex는 파일·목록 SHA256이다.

## 결과 요약 (보고 기준, 판정은 각 링크)

| 항목 | 결과 |
|---|---|
| T1 | PASS(14:46, 양쪽 IKE·Child SA established) |
| T3 | PASS(16:12:20 `CONNECTED`, db01 SYN 1건 시각·출발지 일치) |
| T6 | 중앙 판정 **INCONCLUSIVE**(원본 검토 6287774429). Relay eth0 캡처가 방향을 구분하지 않은 tcpdump 텍스트라 외부 평문 egress 0을 독립 확정하지 못함. SEC 의견은 PASS(6286988821) |
| T3-R | 성공 보고(17:26:23 `CONNECTED`, db01 SYN 일치) |
| db01 | 두 RUN 모두 `RESULT pre-rollback=OK`, W0 해시(`c7dc1f37…`) 복구, pg_hba 불변 |
| VPN | 양쪽 `ROLLBACK_DONE`, conn·secrets·nft·유닛 부재. Relay `ip_forward=0` |
| 세션 | 오늘 연 SSM 세션 6개 모두 Terminated, Active 0 |

## 한계 (보고 원문 그대로 보존)

- 첫 관측(`1430`)은 Ctrl+C로 끝나 `capture_rc`가 남지 않았다. `capture-exit.txt`는 수동 기록이다.
- 첫 CloudShell `script` 로그는 14:46 Relay apply 부근까지만 있다. 그 뒤 CloudShell 명령의 출력은 이 폴더에 파일로 없다. tsv 파일과 이슈 보고 원문이 전부다.
- T6 캡처 명령의 rc, T6 전후 nft 전체 원문, 복구 뒤 accept 카운터, vpn-gw01 V9 stdout은 터미널 화면에만 있었고 파일로 남기지 않았다 → **미수집**. 보고 댓글에 옮긴 값이 전부다.
- Relay tcpdump 설치(17:19, GO 범위 밖, 구두 보고 뒤 진행)와 undo(17:33)는 [6286925448](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6286925448) §4와 이 폴더의 `rpm/`으로 기록한다. 08:19 설치·08:33 undo 직후 화면 출력은 미수집이다.
- 정리 순서는 승인 순서(P9·P8 → V9)와 달리 P9 → vpn-gw01 V9 → P8 → Relay V9였다(6287464471).
- 원 archive 두 개는 SPI 정제 때문에 이 폴더에 넣지 않았다. archive 바이트 대조는 비공개 폴더 원본과 위 SHA256으로 한다.

AI 사용: CLAUDE_ASSISTED
