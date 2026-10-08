# DEC-P2-REG-01 — Harbor current leaf / FQDN TLS 읽기 전용 수집 원본 (2026-10-04 15:37:03 KST)

- 대상 이슈: [321Team/infra-rosa#9](https://github.com/321Team/infra-rosa/issues/9) (원티켓 [DEC-P2-REG-01 — fds-project-baseline#42](https://github.com/321Team/fds-project-baseline/issues/42) Sub-task 1/4, AC-2 TLS 부분 입력, 테스트 전략 추적 TS08)
- 수집 절차: [read-only intake runbook @e957eab](https://github.com/321Team/fds-project-architecture/blob/e957eab6f5e146721f3439efe7230f6ded295b61/phase2/runbooks/20261004-harbor-d22-readonly-intake.md) §3 블록. 입력 계약: [D22 input contract @1fb4700](https://github.com/321Team/fds-project-architecture/blob/1fb47001663e7689d9fd7eb9776f50221d5f5542/phase2/reviews/20261004-harbor-d22-input-contract.md) (PROPOSED, Freeze HOLD)
- 이 폴더는 D22 결정의 **입력 증적**이다. D22 최종 결정·IF-19·WBS 갱신은 Decision Lead(이권욱) 소관이며 이 편입으로 확정하지 않는다.

## 수집 정보

| 필드 | 값 | 근거 |
|---|---|---|
| ENV | P1 기존 Harbor (`10.1.93.54:443`), 클라이언트 cicd-runner01 | `context.txt`, `tls-diagnostics.txt` |
| 관측 시각 | 2026-10-04T15:37:03+09:00 | `context.txt` |
| 실행 호스트 / 계정 | `cicd-runner01` / `server01_cicd-runner` | `context.txt` |
| 도구 버전 | OpenSSL 3.5.8 25 Aug 2026 | `context.txt` |
| 명령 | `openssl s_client -connect 10.1.93.54:443 -servername harbor.fds.internal -verify_hostname harbor.fds.internal -verify_return_error -CAfile <공개 Root> -no-CApath -no-CAstore -showcerts -no_ticket` (stdout은 CERTIFICATE 블록만 저장) | runbook §3 |
| RC | `TLS_RC=0`, `FILTER_RC=0` | `status.txt` |
| 고정 Root PEM | 파일 SHA256 `20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f` (실행 전 기대값 일치 확인 후 진행) | `context.txt` |
| 서버 원본 경로 | `cicd-runner01:/home/server01_cicd-runner/d22-harbor-ro-34OMzIfp/` (파일 8개, 모두 10-04 15:37 생성, mode 0600) | 2026-10-08 `ls -l` |

## 관측 결과 (원본 파일 내용)

- leaf: subject `CN=harbor.fds.internal`, issuer `CN=FDS Project Root CA 2026`, serial `1000`
- 유효기간(UTC): 2026-09-15 04:00:08 ~ 2027-09-15 04:00:08, `-checkend 0` → `Certificate will not expire`
- SAN: `DNS:harbor.fds.internal`, `DNS:harbor01`, `IP Address:10.1.93.54`
- leaf DER SHA256 fingerprint: `61617af3574f37c70a2d9c7f284a75f82c844ae3eaf599cb3d0ec649126ebeaf`
- chain 검증: depth=1 Root, depth=0 leaf 모두 `verify return:1`
- `server-chain.pem`과 `leaf.pem`은 바이트가 같다(SHA256 `82c00201…ea97`). 서버가 leaf 1장만 보내고 중간 인증서는 보내지 않았다.

## 판정 범위

| 항목 | 판정 | 비고 |
|---|---|---|
| 고정 CA + FQDN 이름 검증 TLS | PASS | `-verify_hostname harbor.fds.internal` + `-verify_return_error` + RC 0 |
| IP 이름 검증(verify_ip) | **미시험** | SAN에 IP가 있다는 것은 verify_ip 성공이 아니다 |
| DNS 조회 | **미시험** | 고정 IP `10.1.93.54`로 접속했다. 이름 해석 성공을 뜻하지 않는다 |
| OS 기본 trust / Podman 로그인·pull / ROSA HCP trust·cold-pull | 범위 밖 | runbook §4·원티켓 잔여, ROSA Basic Ready 이후 |

같은 leaf(지문·serial·SAN·유효기간 동일)를 서버 측에서 본 기록은 [P1-HBR-01 harbor-tls-restore-post-20260930T172323.txt](../../P1-HBR-01/lead-runtime-20260930-20261002/harbor-tls-restore-post-20260930T172323.txt)에 있다. 그 기록과 [P1-HBR-01 AC-01 TLS negative(10-04 18:54)](../../P1-HBR-01/lead-runtime-20261004/ac01-tls-negative-20261004/README.md)는 IP 주소로 접속했다. 이 폴더는 FQDN 이름 검증을 남긴 유일한 회차다.

## 수신 경로와 해시 대조

사용자 readback(10-04)과 2026-10-08 재해시를 구분해 적는다.

| 단계 | 수행 | 결과 |
|---|---|---|
| 사용자 readback | 2026-10-04 현장 `sha256sum -c` (원티켓 #42 10-04 댓글) | 7/7 OK, `D22_RESULT_READBACK=OK` |
| 서버 재확인 | 2026-10-08, ansible01 → cicd-runner01 `sha256sum -c SHA256SUMS` | 7/7 성공 |
| 전송 묶음 | 2026-10-08, runner에서 `tar -C ~ -czf /tmp/d22-harbor-ro-34OMzIfp.tar.gz d22-harbor-ro-34OMzIfp` (원본 폴더 변경 없음) | tar.gz SHA256 `3f941e2a7ab2db0c6e2c415c21611f86eb032f3e997d25ded449fb9e4f337545` |
| ansible01 수신 | ansible `fetch` | checksum = remote_checksum (`251737710d8698b1ab4327e835bce56062c57f96`, SHA1), tar.gz SHA256 동일, 압축 해제 후 7/7 성공, leaf 지문 재계산 일치 |
| PC 수신 | 공유 폴더 경유 | tar.gz SHA256 동일, 내부 8개 파일, 7/7 OK, `openssl x509 -fingerprint -sha256` 일치 |
| 이 폴더 | 압축 해제 파일을 바이트 그대로 복사, 줄바꿈 정규화 없음(CR 0개) | `sha256sum -c SHA256SUMS` 7/7 OK |

**원본은 10-04 파일 8개, archive는 10-08 전송 묶음이다.** 10-04 수집 때 별도 archive·manifest는 만들지 않았고, runbook이 만드는 `SHA256SUMS`가 원본 manifest다. 10-08 전송용 `d22-harbor-ro-34OMzIfp.tar.gz`(2,668 bytes)는 위 해시 대조의 근거라서, PC가 받은 바이트를 재압축 없이 이 폴더에 함께 두었다(리뷰 B1 반영). 같은 이름의 `.sha256` sidecar를 두었고, 내부 8개 파일의 이름·크기·SHA256은 [`registry/ARCHIVE_CONTENTS.json`](../../../registry/ARCHIVE_CONTENTS.json)에 등록했다. 내부 8개 파일의 해시는 이 폴더의 원본 8개와 같다.

10-08 서버 `ls -l` 출력(mode 0600, 파일 8개)은 사용자 콘솔 화면으로만 확인했고 파일로 편입하지 않았다. archive 안의 tar 헤더에 같은 mode(`-rw-------`)와 10-04 15:37 mtime이 남아 있다.

## 파일

| 파일 | SHA256 |
|---|---|
| `SHA256SUMS` (원본 manifest, 아래 7개) | `274af1e2ded318bc309386de63818f37a6656ceb8dbf67bd4b53ec8eef3bc78b` |
| `context.txt` | `1e8bbe815d7817beb40073b020ed9bc002aa78eec2f77700e5b899e3f476ba13` |
| `status.txt` | `ba5489766263ce4ed759abe051d5a6bd7c9fd037c9298b0df31992604cca1c70` |
| `server-chain.pem` | `82c00201e7e0c14190bb7836741016540bba494dbb9a4b8baa6111e8f9a97ea9` |
| `leaf.pem` | `82c00201e7e0c14190bb7836741016540bba494dbb9a4b8baa6111e8f9a97ea9` |
| `leaf-metadata.txt` | `3ce125b81c206811ab977bddc678260bae82fe4b35be87bd91c1505a19a78742` |
| `expiry-check.txt` | `884cfe6153fc074f92defed83aaabbca814ec8e4f43e37b01e55ed76a86aaf8b` |
| `tls-diagnostics.txt` | `5f4be439d1ed0cdb38553f576d1b4dc1b6d19c0507be2e2a72c26a9689ea7880` |
| `d22-harbor-ro-34OMzIfp.tar.gz` (10-08 전송 묶음) | `3f941e2a7ab2db0c6e2c415c21611f86eb032f3e997d25ded449fb9e4f337545` |
| `d22-harbor-ro-34OMzIfp.tar.gz.sha256` (sidecar) | `REGISTRY_SHA256SUMS`에 등록 |

폴더 이름의 `infra-rosa-issue-9-`는 [증적 관리 규칙 「저장 경로」](../../../governance/EVIDENCE_POLICY.md)에 따라 출처 이슈를 표시한 것이다(리뷰 N1 반영, 최초 `harbor-leaf-tls-20261004T153703/`에서 병합 전 변경).

## 민감정보 점검

공개 인증서(PEM), 시각·호스트·계정 이름·OpenSSL 버전, RC, 검증 진단만 있다. private key, Robot secret, token, Pull Secret, TLS 세션·keying material은 없다(runbook이 s_client 세션 상세를 저장하지 않는다). 내부 주소·호스트 이름이 포함되어 저장소 접근 범위를 따른다.

저장소 `.gitignore`는 개인 키 유출을 막기 위해 `*.pem`을 제외한다. `leaf.pem`·`server-chain.pem`은 `BEGIN/END CERTIFICATE` 블록 1개씩만 있고 `PRIVATE` 문자열이 없음을 확인한 뒤 `git add -f`로 추가했다. 원본 `SHA256SUMS`의 파일명과 맞추기 위해 `.crt`로 바꾸지 않았다. 같은 이유로 `.gitignore`의 `*.tar.gz` 규칙에 걸리는 전송 묶음도 `git add -f`로 추가했다.

## 경계

- Harbor·Robot 설정 변경이나 rotation은 수행하지 않았다(P1-HBR-01 소관).
- Shared OCP pull PASS를 ROSA Registry 경로 승인으로 올리지 않는다.
- 이 편입은 독립 검토 전이며, 검토·병합이 DEC-P2-REG-01 AC-2 완료나 D22 판정을 뜻하지 않는다.
