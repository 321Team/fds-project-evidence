# P2-VPN-01 단계 B 묶음 — 준비 기록 (2026-10-14 18:3x KST, 이재환, CLAUDE_ASSISTED)

서버 전달 전 로컬 준비본이다. 단계 B 작업창 GO 전에는 Relay·vpn-gw01로 보내지 않는다.

- 소스: infra-vpn main 병합 커밋 `6432d7ebb712aaf6368e9a7a001ae55fc572215e` (PR #6, 부모 `f473ffb8` + PR HEAD `73ac1cd9`)
  - 병합본과 PR HEAD `73ac1cd960389cc6f1f9205a5637896416d22f06` 사이의 트리 차이는 0이다. 리뷰·CI(run 38540147640, 56 OK) 대상과 바이트가 같다.
- 추출: `git cat-file blob`으로 원본 바이트를 그대로 추출했다. `git hash-object` 재계산이 Git blob과 6/6 일치하고, CR은 0이다.
- PSK·자격증명 없음

| 파일 | Git blob | SHA256 | 이전 B0 묶음 대비 |
|---|---|---|---|
| p2vpn.sh | a294a171cd631c4007ffae7ae2d9ae97832c6ece | 88edf76ccf90ca4df3a53b56c831e8f37fd5b5daa3f889c5da290491d1ee4693 | 변경(PR #6) |
| conf/relay.conf.tmpl | af640844de78e2950c7e1342fd86cbf289f8236c | 40003e6bf0eda41754440d0c59b5b6a393dc81d17a68a5e0534aaea4576af112 | 같음 |
| conf/vpn-gw01.conf.tmpl | 46ef2eec9b08cfc0522db9566578274f08b2a58e | 8088b844c699ba2a5c720170a81b8142670737e3cfd234234d5956a4d04f581b | 같음 |
| nft/relay.nft.tmpl | f338035fb84c25ec60ef0c4c856334e7c6e917ae | 3f644b58bb582cc791ec08f60aa5301d57f972f0714c4f4562ec59bef5b8ff3e | 같음 |
| nft/vpn-gw01.nft.tmpl | 65153818e18251f946b156b2e370f0d6a6385b44 | 78506de258184a02eb180161cf88ba32c7aacfeccad6173967a122cd73247b24 | 같음 |
| systemd/fds-p2-vpn-forward.service | 14900528a4bc47e12d5cdde283d9a3e8e252be7f | f402613878a04d66078ab8636323f28217cd238621aa1440a2d707f3cf325815 | 변경(PR #6 R1 ExecStopPost) |

## 묶음
- 묶음 `p2-vpn-01-stageb.tgz`: 13,888 B, SHA256 `358624f5a380e341b7095ccd13357d03f9bf6d346a8d4c331f0552a212b0bbaf`
  - 만든 방법: GNU tar `--sort=name`, mtime 2026-10-14 00:00Z, owner 0/0, `gzip -n -9`
  - `p2vpn.sh`만 0755, 나머지는 0644
- 전달용 `p2-vpn-01-stageb.tgz.b64`: 244줄, 18,764 B(76자 줄바꿈)
  - 복원한 SHA256이 묶음과 일치한다.
  - b64 파일 자체 SHA256 `dd1602efa6d4c1b31708a95aa3ac07a2e890654467cf4185f08bbb553f6ae406`
- 로컬 대조
  - `sha256sum -c p2-vpn-01-stageb.tgz.sha256` OK
  - 풀어서 `sha256sum -c p2-vpn-01/SHA256SUMS` 6/6 OK
- 이전 Relay B0 묶음(`880a0df5…`, main `f473ffb8`)은 이 묶음으로 대체한다. 단계 B에는 쓰지 않는다.

## 서버 쪽 대조 (단계 B 착수 시)
1. `sha256sum -c p2-vpn-01-stageb.tgz.sha256`
2. 풀고 나서 `sha256sum -c p2-vpn-01/SHA256SUMS`
3. 이 표의 tgz SHA256·병합 SHA를 단계 B 증적에 기록한다.
