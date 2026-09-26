# P1-DB-01 — Lead 직접 재수집 원본 (2026-09-25)

[PR #31](https://github.com/321Team/fds-project-evidence/pull/31)이 "P1-DB-01 AC 근거가 저장소 밖 아티팩트뿐"이라고 지적한 항목에 대해, 담당 Lead(이재환, supreme33-kr)가 서버 두 곳에서 명령 출력을 **파일로 바로 저장**해 편입한다. 이 폴더의 파일은 서버가 만든 출력 그대로이며 손으로 고치지 않았다. 해석은 이 README에만 적는다.

이 PR의 이전 커밋(`0110c05`)에는 붙여넣은 출력을 다시 정리한 파일이 원본처럼 들어 있었고 README도 "편집하지 않았다"고 잘못 적었다([하영님 리뷰](https://github.com/321Team/fds-project-evidence/pull/37#pullrequestreview-5313449647)). 그 파일들은 이번 커밋에서 이 폴더의 원본으로 교체했다.

## 수집 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이재환(supreme33-kr) 본인. 콘솔에 직접 접속해 실행 |
| control01 | 계정 `server02`, 2026-09-25T04:47Z (13:47 KST). `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf` |
| db01 | 계정 `server08`, 2026-09-25T04:49Z (13:49 KST). `sudo`, `psql -U fds_app -h 127.0.0.1` |
| 실행 방식 | 조회 명령만 실행. 각 명령의 시작·종료 시각과 종료코드는 `commands.log`에 기록됨 |
| 전달 | 서버에서 tar.gz + base64 출력을 채팅으로 전달. db01 압축본은 서버가 출력한 SHA-256(`de7261699efbbee2ea7c616792b54e43d9b0d893449e099659f841d437934008`)과 복원본이 일치. control01 파일은 서버가 미리 계산한 `SHA256SUMS.pre`(22개)와 복원본이 모두 일치, 추가분 압축본 SHA-256 `45c4aadac381cac17a06fe5c332ca62aa1079bf77c3c915c88c26eb06a0697cd` 일치 |
| 빈 파일 | 내용이 비어 있는 `*.stderr`는 생략했다. 서버 SHA256SUMS에는 빈 파일 해시(`e3b0c442…`)로 남아 있다 |
| 서버 해시 | `control01/server-SHA256SUMS.pre`, `db01/server-SHA256SUMS` — 수집 직후 서버에서 계산한 원본 |

`control01/commands.log`는 두 번째 수집(Alertmanager 재조회)까지 포함한 최종본이라, 서버 해시(`SHA256SUMS.pre`)의 `commands.log` 항목과 해시가 다르다(이후 줄이 추가됨). 앞부분은 동일하다.

## 파일 목록

control01: `fds-app-networkpolicy.yaml`(fds-app 네임스페이스 NetworkPolicy 전체), `fds-app-workloads.txt`, `nodes-wide.txt`, `rejection-test.py`(실행한 시험 코드 전문), `rejection-output.txt`, `hostname.txt`, `commands.log`.
db01: `pg_hba-active-lines.txt`, `listen_addresses.txt`, `firewalld-list-all.txt`, `firewalld-rich-rules.txt`, `ip-addr.txt`, `hostname.txt`, `commands.log`.

## 확인된 사실

- **차단은 NetworkPolicy가 담당한다.** `fds-engine-allow`의 egress는 kube-system DNS(53)만 허용하고 db01(5432) 규칙이 없다. 같은 네임스페이스의 `default-deny-all`이 나머지를 막는다. fds-engine Pod에서 db01:5432 연결 시험은 `TimeoutError('timed out')`이었다.
- **db01 접근 통제는 `pg_hba`와 NetworkPolicy에 있다.** `pg_hba`는 `fdsdb`에 대해 `hostssl … fds_app … scram-sha-256`으로 4개 주소만 허용한다. `listen_addresses='*'`이고 firewalld는 5432/tcp를 source 제한 없이 열어 두었다(rich rule은 SSH만).
- **주소와 호스트.** `.105`/`.107`/`.108`은 `nodes-wide.txt`의 k8s-worker01/02/03이다. `.50`은 프로젝트 문서상 edge01이며 이번 수집에서는 확인하지 않았다(NOT VERIFIED).
- **정책 정의의 저장소 위치.** 이 NetworkPolicy의 정의는 [infra-kubernetes PR #7](https://github.com/321Team/infra-kubernetes/pull/7)(미병합) 브랜치 `p1-k8s-01/p1-sec-01-revision` HEAD `c9ec46d`의 `manifests/03-networkpolicy.yaml`(blob `bb33d57756a0b93541a28a3453f748d47544a20e`)에 있다. 이 파일의 `fds-engine-allow` spec은 이번에 수집한 실제 객체와 의미가 같다. main에는 아직 없다. 정확한 apply 이력(적용한 커밋)은 확인하지 못했다.

## 이전 기록과의 차이

- 9/7 R2 증적은 차단을 ConnectionRefusedError로 기록했으나 이번 결과는 5초 타임아웃이다. Calico NetworkPolicy는 패킷을 DROP하므로 타임아웃이 정책 차단에 부합하지만, 9/7과 이번 사이에 구조가 바뀌었는지(9/22 `fds`→`fds-app` 이전 포함)는 확인하지 않았다.
- 이전 세션 기록에 있던 정책명 `allow-transaction-api-to-db`는 현재 클러스터에 없다(첫 조회에서 NotFound). 그 이름은 옛 데모 환경(`fds-msa/kubernetes/base`)의 것이다.

## 미수신·미확인

- 정책을 apply한 시점의 실제 명령·커밋 기록.
- 승인되지 않은 소스 IP에서 db01로의 직접 접속 거부 시험(이번 시험은 fds-engine Pod 기준 1건뿐).

AI 사용: CLAUDE_ASSISTED (실행은 담당자 본인, Claude는 명령 작성·복원·검증·문서화)
