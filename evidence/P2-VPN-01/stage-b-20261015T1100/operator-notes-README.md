# P2-VPN-01 Stage B 실행 증적 — RUN 20261015T1100 (2026-10-15 11:00~11:28 KST, 실행 이재환, CLAUDE_ASSISTED)

GO: infra-terraform#11 6182615142 / 시작 기록 6182821690. 묶음 `p2-vpn-01-stageb.tgz` 358624f5…, merge 6432d7eb.

| 파일 | 출처 | 내용 |
|---|---|---|
| `p37-stageb-20261015T1100.tgz` | CloudShell `~/`에서 묶어 다운로드 | `gate-aws.log`(조회 게이트·Relay P5/P6·B0·B1, 세션 l5dv…), `b3-relay.log`(B3~Relay 원복, 세션 qgxh…), `SHA256SUMS`. `script -q -f` 출력 기록(입력 기록 없음) |
| `vpngw01-stageb-20261015T1100.txt` | 사용자 터미널 출력을 채팅으로 옮긴 사본 | vpn-gw01 B0·B1·B2(결과 줄)·B4·B5·status·T4/T5 카운터·T10·원복·항목별 대조 |
| `relay-b2-20261015T1100.txt` | 사용자 터미널 출력 결과 줄 | Relay B2. 세션 df72…는 PSK 입력 회차라 터미널 기록을 하지 않았음 |

- PSK·secrets 내용·해시, xfrm 키는 들어 있지 않습니다. 실행기가 SPI와 키를 가립니다.
- `b3-relay.log`에는 창을 착각해 Relay에서 실행한 vpn-gw01용 줄이 들어 있습니다. apply는 경로가 없어 rc 127로 실행되지 않았고, 나머지는 읽기 명령과 프롬프트 문자열 오입력(`command not found`)입니다. 상태 변경은 없습니다.
- 첫 B3 확인 묶음은 apply 명령보다 먼저 실행됐습니다. 그 결과는 apply 직전 상태 기록으로 봅니다.
