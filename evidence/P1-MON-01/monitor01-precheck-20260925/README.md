# P1-MON-01 — monitor01 콘솔 Pre-check 결과 (2026-09-25)

[baseline#17 실행 요청](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5819249301)에 따라 MON Lead(이재환)가 monitor01에서 읽기 전용 수집기를 두 번 실행한 결과다. 각 회차 폴더의 파일은 수집기가 만든 archive를 풀어낸 **서버 생성 원본 그대로**이며, 각 폴더의 `SHA256SUMS`는 수집기가 서버에서 만든 것이다.

## 실행 정보

| 항목 | run1 | run2 |
|---|---|---|
| 시각(KST) | 2026-09-25 20:53:26 | 2026-09-25 21:01:43 |
| 계정 | `server01_monitor` (uid 1000) | 같음 |
| 명령 | `bash monitor01-console.sh` | `sudo -v && bash monitor01-console.sh` |
| 수집기 | `ops/mon-followup/monitor01-console.sh` SHA256 `92a4958be4c1db46d6ca599b05af9d6c06439f921be9379696df5765226758ba` ([infra-monitoring](https://github.com/321Team/infra-monitoring/blob/1b1ef1babfe7c9f0356c6d2e410a47db1fb916f9/ops/mon-followup/monitor01-console.sh), 각 폴더 `collector.sh`) | 같음 |
| 결과 | rc=1, `NONZERO_CHECKS=5` (sudo 캐시 없음) | rc=1, `NONZERO_CHECKS=1` (docker 미설치) |
| archive | `MON_HOST_INPUTS.zRsBkumT.tar.gz` 3,716 B, SHA256 `58fbdb3a…6ed677` | `MON_HOST_INPUTS.Lpj4jVQv.tar.gz` 3,904 B, SHA256 `3537e2a5…960b6b` |

- 전달: 서버에서 base64로 출력해 채팅으로 받았고, 조각별 `cksum`과 archive SHA-256을 서버 출력과 대조해 일치를 확인한 뒤 풀었다. 각 폴더 `archive.sha256.txt`는 서버가 출력한 archive 해시를 옮겨 적은 것이다(수신 측 작성).
- archive 파일 자체는 편입하지 않고 풀어낸 파일을 편입했다. 내용 대조는 각 폴더 `SHA256SUMS`로 한다.
- 수집기는 read 16회만 수행하며 설치·재시작·설정 변경은 없다(`scope.txt` `READ_ONLY=YES`, `result.txt` `RUNTIME_CHANGE=NOT_RUN`).

## 요약 (판정 아님)

- 서비스: `nginx`·`prometheus`·`blackbox-exporter`·`docker` unit 없음. `podman.service` disabled, root 컨테이너 0개. `cockpit.socket` active.
- listener: 22, 631(localhost), 9090(`cockpit.socket` 기본 포트로 추정, 프로세스 미대조). 443 없음.
- 경로: Worker `.105/.107/.108`는 `10.250.10.1` 경유, ansible01 `.10`은 직결.
- 인증서·키: leaf·root CA는 사용자 홈(644, `user_home_t`), 개인키는 `/etc/fds/pki/…`(600 root, `cert_t`). 파일 내용은 읽지 않았다.

이 결과는 사전 검증 입력이며 AC 인수·Runtime PASS가 아니다.

AI 사용: CLAUDE_ASSISTED (실행은 담당자 본인, Claude는 수집기 확인·수신 대조·문서화)
