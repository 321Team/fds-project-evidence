# PR #4 운영 적용 증적 검토 v1.0

검토일: 2026-09-08 · 대상: [infra-ansible 운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10)

**판정: 실제 운영 적용 6/6 및 수신 원본 기술 검토 PASS. SFTP 전송 경고는 비차단 후속 확인 항목이다.** 사용자 서버에서 실행한 결과를 Codex가 첨부 원본으로 검토했다. Codex의 서버 직접 실행이나 재환님의 독립 승인으로 기록하지 않는다. 이슈 #10의 독립 운영 증적 검토와 증적 PR의 편입·병합은 대기 상태다.

## 1. 실행과 수신 범위

| 항목 | 확인 결과 |
|---|---|
| 실행 묶음 | FDS_SSH_PR4_Apply_Kit_v1.2 · `--apply --https-auth` |
| Run ID | `20260908T102238Z-7dcfedd0` |
| 서버 기록 종료 시각 | 2026-09-08 19:26:18 KST |
| 원본 상태 | `APPLIED_VERIFIED_REVIEW_REQUIRED` — 원본 그대로 보존 |
| 운영 경로 / 브랜치 | `/home/server01_ansible/p1-ans-01` / `main` |
| 승인·적용 Commit | `3a02dc8934adb1f80df48ec6763689c401a1e8d6` |
| 운영 엔진 | `/usr/bin/ansible-playbook` · ansible-core 2.16.19 |
| 실제 설정 파일 | `/home/server01_ansible/p1-ans-01/ansible.cfg` |
| 실행 결과 | 51/51 단계 PASS, 모든 rc=0 |

원본 `FDS_SSH_PR4_Apply_Result.tar.gz`는 23,850 bytes이며 SHA-256은 다음과 같다.

```text
7d0ff1914fe8f4ef583c048c6125e0e2e0a3a77fc11a412feb16abd4afe6de17
```

첨부 이름의 `(1)`은 수신 파일명 차이로 매핑했다. Sidecar의 원래 파일명과 실제 수신 바이트를 대조했으며 외부 SHA-256 일치, 내부 목록 55/55 일치, 원본 정규 파일 56개 전체를 확인했다. 체크섬 자체를 제외한 파일이 모두 내부 목록에 포함된다. 절대 경로·상위 경로 이동·링크·중복 엔트리는 없다.

`INPUT_SHA256SUMS`와 `SOURCE_TREE.json`은 전달한 v1.2 묶음의 동일 파일과 바이트가 같다. 압축 원본과 sidecar는 기존 수신 첨부로 보존하며, Git에는 추출 텍스트 원본과 검토·매핑 정보를 등록한다.

## 2. Git 인증과 기존 운영 경로 동기화

`GIT_SYNC_REPORT.json`과 `APPLY_REPORT.json`의 동기화 기록이 일치한다.

| 항목 | 이전 | 이후 |
|---|---|---|
| 브랜치 | `cr-p1-ans-01-01-dns-resolver` | `main` |
| HEAD | `507d8882a04f53640b07251bcc234b7d6ee81c09` | `3a02dc8934adb1f80df48ec6763689c401a1e8d6` |
| untracked/ignored 파일 | 59개 | 59개, 보존 집계 Hash 동일 |

승인 소스 28개 검증이 기록됐다. 보존 집계 Hash는 `cce35d26b95ccbd56ace390a584e4f15c438dfbdcd4573d5b883854dfa4c2aff`이다. 강제 동기화·stash·clean은 사용하지 않았다. 성공 상태를 내기 전 실행기의 최종 작업 사본·보존 검사를 통과하는 경로까지 확인했으며, 별도의 최종 Git 보고서가 추가로 수신됐다고 해석하지 않는다.

이전 HTTPS 인증 입력 불가로 인한 fetch rc=128 문제는 이번 실제 fetch 성공으로 해소됐다. 임시 인증 캐시 종료는 사용자 콘솔의 `GIT_AUTH_CACHE=EXIT_COMPLETED`로 확인한 내용이며 별도 원본 캐시 로그는 없다. 수신 파일의 GitHub PAT 형식 및 개인키 헤더 검사에서 해당 문자열은 발견되지 않았다.

## 3. 6대 실제 적용과 상태 보존

| 실행 순서 | 대상 | 첫 apply | 두 번째 apply | 신규 SSH·최종 상태 |
|---|---|---|---|---|
| 1 | k8s-worker01 · 10.1.93.105 | PASS · changed=0 | PASS · changed=0 | PASS |
| 2 | k8s-worker02 · 10.1.93.107 | PASS · changed=0 | PASS · changed=0 | PASS |
| 3 | k8s-worker03 · 10.1.93.108 | PASS · changed=0 | PASS · changed=0 | PASS |
| 4 | k8s-control01 · 10.1.93.102 | PASS · changed=0 | PASS · changed=0 | PASS |
| 5 | k8s-control02 · 10.1.93.103 | PASS · changed=0 | PASS · changed=0 | PASS |
| 6 | k8s-control03 · 10.1.93.104 | PASS · changed=0 | PASS · changed=0 | PASS |

12회 모두 실제 `harden_svc_ansible_key.yml` 실행이며 `--check` 실행이 아니다. 원본 PLAY RECAP은 매회 `ok=4 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`이다. 보고서의 recap과 원본 로그가 일치한다.

`changed=0`은 미실행을 뜻하지 않는다. 제한된 키 1개 상태가 이미 기대값과 같았으므로 기존 키 파일을 다시 쓰지 않았다. 수정한 조건식은 갱신된 운영 코드에서 평가됐다. 컨트롤러 Git 동기화와 각 노드의 전용 백업 생성은 실제 변경이다.

노드마다 before·backup·첫 적용 후 신규 SSH·두 번째 적용 후 신규 SSH·final의 총 30개 상태를 대조했다. 모든 hostname·목적지 IP·접속 Source `10.250.10.10`이 기대값과 같으며, authorized_keys Hash·uid/gid·소유자·그룹·0600·mtime·관리 키 1개·제한 키 1개가 전후 동일하다. 모든 노드의 파일 Hash는 `b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834`이다.

SSH 명령은 기존 known_hosts의 엄격 검증, 공개키 인증, 비밀번호·대화형 인증 차단 및 연결 재사용 차단을 사용했다. 해당 상태 수집 명령의 원격 코드도 v1.2 `node-state.py`와 일치한다.

각 노드에서 확인된 전용 백업 경로는 다음과 같다. 이 경로는 서로 다른 6대 호스트에 각각 존재한다.

```text
/var/lib/fds-change/ssh-pr4/20260908T102238Z-7dcfedd0/authorized_keys
```

OS 사전·사후 검사는 각 6대 `ok=15 changed=0 failed=0`이다. DNS 사전·사후 검사는 각 6대 `ok=32 changed=0 failed=0 skipped=5`이다. DNS에서 건너뛴 5개는 변경 승인·롤백 상태 디렉터리·원 상태 백업·NM 설정·NM reapply 작업이며 verify 단계의 정상 분기다.

## 4. 비차단 특이사항: SFTP 경고

원본 16개 로그에서 `sftp transfer mechanism failed` 경고 36건을 확인했다. 사전·사후 OS/DNS 24건과 노드별 첫·두 번째 적용 12건이다. 이후 작업은 모두 성공했다. 따라서 이번 SSH 키 수정 적용의 기술 PASS를 취소할 근거는 없지만 SFTP 정상 동작까지 PASS로 표시하지 않는다.

Ansible SSH 플러그인의 기본 `smart` 전송은 SFTP·SCP·piped 순서로 시도한다. 다른 경로로 전송이 이어졌을 가능성과 부합하지만, 이번 로그만으로 실제 성공한 방식이나 SFTP 실패 원인을 확정할 수 없다. [Ansible 공식 SSH 플러그인 설명](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/ssh_connection.html)

후속 확인은 이슈 #10에 연결한다. 확인 대상은 컨트롤러의 유효 전송 설정과 SFTP 클라이언트, 대상 서버의 유효 SSH SFTP subsystem, 최소 파일 전송의 실제 사용 방식이다. 원인 증거 없이 키 제한을 완화하거나 전송 방식을 강제하는 수정 Commit을 발행하지 않는다. P1-K8S 구현 시 파일 전송 경로를 사용하는 작업의 확인 항목으로 인계한다.

## 5. 완료 범위와 남은 절차

인증 오류 해소, 기존 운영 경로의 승인 main 동기화, 6대 SSH 키 수정 코드의 실제 실행·재적용·SSH 유지, OS/DNS 전후 검증은 완료다. 이번 결과만으로 시스템 Ansible을 2.21.3으로 업그레이드했다고 볼 수 없다. 운영 엔진은 2.16.19이며 [버전 전환 이슈 #9](https://github.com/321Team/infra-ansible/issues/9)는 별도다.

PR #4의 기존 코드 승인·병합은 유지한다. 운영 이슈 #10에 명시된 독립 검토와 [증적 Draft PR #1](https://github.com/321Team/fds-project-evidence/pull/1)의 편입 검토·병합은 대기이며, 이번 Codex 수신 검토를 사람의 승인으로 대신하지 않는다. Bootstrap은 HOLD다. 기존 증적 대장의 05h/05j 정합성 보완과 다른 티켓의 인수 상태도 이번 실행만으로 해소 처리하지 않는다.
