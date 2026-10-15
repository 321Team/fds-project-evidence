# vpn-gw01 단계 B 사전 읽기 P5·P7 (2026-10-15 10:10:50 KST, 이재환, CLAUDE_ASSISTED)

| 파일 | 내용 |
|---|---|
| `vpngw01-P5-P7-read-20261015T0110Z.full.txt` | 터미널 출력 원문(사용자가 붙여 넣은 그대로, 생략 없음). 원본 |
| `vpngw01-P5-P7-read-20261015T0110Z.txt` | 파생 사본: ipsec status의 알고리즘 목록만 생략하고 그 사실을 머리말에 표시 |

- 실행: `server08@vpn-gw01`, 작업 디렉터리 `~/p2vpn-precheck-20261012`. 읽기만 했고 변경은 없습니다.
- **root 권한 확보와 존재 검사의 구분**
  - 붙여 넣기 직전에 `sudo -v`를 따로 실행했습니다. 이 줄은 원문에 포함되지 않았습니다.
  - 같은 묶음의 `sudo -n nft list tables`(rc 0)·`sudo -n ipsec status`(rc 0), 바로 다음 묶음의 `sudo -n firewall-cmd` 4건(rc 0)이 모두 성공했습니다. `sudo: 암호가 필요합니다` 같은 인증 실패 줄도 없습니다.
  - 따라서 `sudo -n test -e`는 root로 실행됐습니다. `/root/fds-p2-vpn`의 상위 경로 검색 권한 문제는 해당하지 않습니다. `exists_rc=1`은 해당 경로가 없다는 뜻입니다.
- `ipsec status`는 필터 없이 실행했고, 명령 직후 `ipsec_status_rc=0`입니다.
- 유닛 `inactive`/`not-found`의 rc 4는 유닛 파일 부재(`exists_rc=1 /etc/systemd/system/fds-p2-vpn-forward.service`)와 함께 판단합니다.
- 창 시작 직전에 같은 조회를 다시 실행합니다. 이 관측은 실행 시점의 상태를 보증하지 않습니다.
