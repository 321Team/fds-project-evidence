# P1-MON-01 — cicd-runner01 제한적 수동 복구 기록 (2026-10-05 18:10~18:14 KST)

port-forward 재시험 1회차([evidence#116](https://github.com/321Team/fds-project-evidence/pull/116))가 Restore Gate BLOCKED로 끝난 뒤, [PMO 결정 5991412125](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5991412125)(②안: 재시험 없이 기존 runner 서비스의 제한적 수동 복구)에 따라 runner 서비스를 1회 시작한 기록입니다. 결과 보고는 [#17 5991531891](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5991531891)입니다. 실행자는 MON Lead 이재환(supreme33-kr)이며, 해석은 이 README에만 적습니다.

**이 기록은 수동 복구 승인에 의한 서비스 회복입니다.** PF 성공, 옛 토큰 무효화 실증, 1회차 Restore Gate 통과가 아닙니다. 1회차 `status.txt`의 `RESTORE_GATE=BLOCKED`와 PF AC NOT VERIFIED는 그대로입니다.

## 수집 정보

| 위치 | 계정 | 파일 | 성격 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02` | `control01/cp-objects.txt` | 서버 `~/pf-retest-d9bc0c8/recovery-20261005-runner/`에서 `tee`로 만든 파일을 화면 `cat` 출력에서 복원. 서버 SHA-256(`control01/server-SHA256SUMS`)과 일치 |
| cicd-runner01 `10.250.10.20` | `server01_cicd-runner` | `runner/pre-check.txt`, `start.txt`, `post-check.txt` | 같은 방식으로 복원. 서버 SHA-256 3/3 일치(`runner/server-SHA256SUMS`) |
| PC `10.1.93.29` | `soldesk`(`gh`) | `pc/pre-*.json`, `pc/pre-check-gh.txt`, `pc/post-gh-poll.txt`, `pc/post-runners.json` | GitHub API raw 응답과 요약(PC에서 직접 실행. 시각은 KST로 표기) |

## 복구 직전 확인 (결정문 1~5)

| # | 확인 | 결과 | 시각(KST) | 파일 |
|---|---|---|---|---|
| 1 | SA·Role·RoleBinding `monitoring-api/p1-mon-pf-verify` | 3개 모두 명시적 `NotFound`, rc=1 | 18:11:48 | `control01/cp-objects.txt` |
| 2 | runner 잔여 | `/dev/shm` kubeconfig 0, 1회차 시험 kubectl 0, `p1-mon-pf-verify` 포함 port-forward 프로세스 0, `ss` rc=0, TCP 13000 리스너 0 | 18:11:57 | `runner/pre-check.txt` |
| 3 | 토큰 만료·시계 | epoch `1791191517` > TOKEN_EXP `1791186948`(16:55:48), 약 76분 경과. runner와 PC 시각 일치 | 18:11:57 | `runner/pre-check.txt` |
| 4 | runner 상태 | local `inactive`, Runner Listener·Worker 0 / GitHub `cicd-runner01`(id 2) offline · busy=false | 18:11:57 / 18:10:50 | `runner/pre-check.txt`, `pc/pre-runners.json` |
| 5 | CI 대기 | infra-cicd queued 0, in_progress 0 | 18:10:50 | `pc/pre-queued.json`, `pc/pre-in_progress.json` |

3번은 만료 시각 경과 확인일 뿐이며, SA 삭제에 따른 인증 거부를 실증한 것이 아닙니다. 옛 토큰은 재구성하거나 재배치하지 않았습니다.

## 실행·결과

| 단계 | 결과 | 시각(KST) | 파일 |
|---|---|---|---|
| `sudo systemctl start actions.runner.321Team-infra-cicd.cicd-runner01.service`(1회) | `start_rc=0`, `is-active=active`. 이 시점 Listener 0(기동 직후) | 18:12:52 | `runner/start.txt` |
| GitHub runner | online · busy=false | 18:13:08 | `pc/post-gh-poll.txt`, `pc/post-runners.json` |
| 재확인(읽기 전용) | `active`, `Runner.Listener run --startuptype service` 1개 | 18:13:37 | `runner/post-check.txt` |

start는 한 번만 실행했습니다. 반복 start·restart, 설정·권한 변경, 다른 서비스 재기동, 새 PF·토큰·RBAC 생성, canary는 하지 않았습니다.

## 한계

- 서버 파일은 화면 출력에서 복원했습니다. 서버가 출력한 SHA-256과 바이트 단위로 일치합니다.
- `post-runners.json`은 18:13:08 폴링 직후 다시 받은 응답입니다. 폴링 기록(`post-gh-poll.txt`)과는 별도 요청입니다.
- 이 복구는 1회차 PF의 결과를 바꾸지 않습니다. PF 승인 단말 AC는 NOT VERIFIED이고, Close 분류는 #30에서 다룹니다.

## 파일 무결성

`SHA256SUMS`에 이 폴더 전체 파일의 SHA-256을 적었고, 저장소 `REGISTRY_SHA256SUMS`에 등록했습니다.

AI 사용: CLAUDE_ASSISTED (명령 작성, 출력 복원·대조, README 작성)
