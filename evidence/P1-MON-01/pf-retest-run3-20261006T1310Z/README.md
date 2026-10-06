# P1-MON-01 — 승인 단말 port-forward 3회차 원본 (2026-10-06 22:05~22:22 KST)

#17 [조건부 GO 6014851491](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6014851491)·[시작 기록 6016985265](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6016985265)에 따른 PF 새 RUN `run-20261006T2200` 1회의 원본입니다. 결과 보고는 [#17 6017441619](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6017441619)입니다. 실행자는 MON Lead 이재환(supreme33-kr)이며, 해석은 이 README에만 적습니다.

**결과 요약:**
- 승인 단말 cicd-runner01(`.20`) → API LB(`.109`) → Grafana port-forward 성공(health 200, 인증 없는 접근 401)
- 신원·권한 경계 6/6 PASS
- SA 삭제 후 옛 토큰 `DENIED`(만료 전, N2 대조 일치)
- Restore Gate PASS, runner online 복구

**T0 22:10:54 → GitHub online 22:22:06**이며, 승인 한계(중단 22:30:54, 복구 22:50:54) 안에 끝났습니다.

## 실행 소스와 입력

- 도구: infra-monitoring merge `d9bc0c8d`(승인 HEAD `6262eb0e`). 시작 직전 SHA-256을 대조했고 3/3 일치합니다.
  - control01 `pf_cp.sh` `cbe25e84…`
  - runner `pf_runner.sh` `22566e14…`
  - PC `pf_gh.sh` `8243b103…`
- 도구 밖 실행 입력(GO S2): `inputs/pf3-a7-a8b.txt`(A7 토큰·A8 표식 필터 배치·A8b 구문 검사 원문). SHA-256 `e17556673b30469248488ed03ef1acf5a704439ffd7c93c22ee622f864597a57`는 시작 기록에 게시한 값과 같습니다. 실행 때는 `<TOKEN_EXP>`, `<GRAFANA_POD>`, `<OTHER_POD>`만 실제 값으로 바꿨습니다.

## 수집 정보

| 위치 | 계정 | 서버 경로 | 이 PR의 파일 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02` | `~/pf-retest-d9bc0c8/{run-20261006T2200, mon-gate-20261006T2200.txt}` | `control01/ev-control01-pf3.tgz` + `.sha256` + 풀어낸 파일 |
| cicd-runner01 `10.250.10.20` | `server01_cicd-runner` | `~/pf-retest-d9bc0c8/run-20261006T2200`, `run-20261006T1625/13c-listener-continuity.txt` | `runner/ev-runner-pf3.tgz` + `.sha256` + 풀어낸 파일(빈 `bin/`은 Git에 담기지 않음) |
| PC `10.1.93.29` | `soldesk`(Git Bash, `gh`) | `C:\Users\soldesk\pf-run-20261005\gh-20261006T2200` | `pc/gh-20261006T2200/` |

- **전달 방식:** 서버 압축본을 `base64 -w 76`과 줄별 `cksum`으로 받았습니다. 줄 검사합은 control01 57/57, runner 53/53 일치합니다. 복원한 압축본 SHA-256도 서버 출력과 같습니다(각 `.sha256`). 서버 압축본은 서버 홈 디렉터리에 남아 있습니다.
- **비밀값:** 두 서버 모두 회차 폴더에서 `eyJ`·`PRIVATE KEY`·`client-key-data`·`token: ` 패턴이 0건이었습니다(서버에서 검사). 복원본도 0건입니다.
  - 토큰은 control01 화면에만 출력됐고 A8 직후 `clear`했습니다. 파일에는 클레임만 있습니다(`15-token-claims.txt`).
  - runner kubeconfig는 `/dev/shm`에만 있었고, 이 PR에는 권한·크기만 남긴 `05-kubeconfig-perm.txt`가 있습니다. cleanup에서 삭제됐습니다.
- **PC 시각 표기:** meta 시각은 UTC를 "GMT"로 표기한 것입니다(예: `13:22:06 GMT` = 22:22:06 KST).
- **PC `after_stop`:** 22:11:17, 22:11:27, 22:11:38, 22:11:49 네 번은 GitHub 반영 지연으로 online(FAIL)이었고, 22:12:00 다섯 번째에 offline(PASS)이었습니다. `after_stop-meta.txt`·`verdict.txt`에는 다섯 번이 모두 있습니다. `after_stop-runners.json`은 같은 이름으로 덮어써져 **마지막(PASS) 응답만** 남아 있습니다.

## 단계별 결과 (KST)

| 단계 | 시각 | 결과 | 근거 파일 |
|---|---|---|---|
| A1 GitHub pre | 22:05 | online·busy=false·queued 0·in_progress 0 — PASS | `pc/…/pre-*`, `verdict.txt` |
| 시작 Gate | 22:06~22:09 | MON `up` 23/23·remote_write 실패 0(22:09:16), heartbeat 13.3초, runner 잔여 0·active | `control01/mon-gate-20261006T2200.txt` |
| A2 control01 pre | 22:10:35 | PRE=PASS, Grafana `grafana-f65457bfd-ckjgj`, 비교 Pod `prometheus-d8949bd64-2zc4m` | `control01/run-20261006T2200/00~07*`, `pinned.env` |
| A3 runner pre·stop (**T0**) | 22:10:54 | PRE=PASS, RUNNER_STOPPED_LOCAL=PASS | `runner/run-20261006T2200/00~03*`, `ss.log` |
| A4 GitHub after_stop | 22:12:00 | offline — PASS(앞의 지연 4회 보존) | `pc/…/after_stop-*` |
| A5 kubectl 설치 | 22:1x | 체크섬 OK, v1.36.4 | `04-kubectl-sha.txt` |
| A6 임시 RBAC | 22:1x | DRYRUN=PASS, 생성 UID SA `ab58eef6…`, Role `75799552…`, RB `63ee01e6…` | `08-*`, `09-dryrun.txt`, `10-create.txt`, `created.env` |
| A7 토큰 | exp 22:23:43 | 소유 UID 재대조 PASS, 호출자 kubernetes-admin, TTL ≤900 PASS | `12-owned-before-token.txt`, `13-tokenrequest-caller.txt`, `15-token-claims.txt` |
| A8 배치 | 22:14:33 시작 | `MARKER_CHECK=PASS b=1 e=1 apiVersion=1 current-context=1 lines_in_block=12 lines_passed=12`, KUBECONFIG_PLACED=PASS(파일 0600, 2,745바이트, 22:16) | `runner/…/05a-marker-check.txt`, `05-kubeconfig-perm.txt`, `status.txt` |
| A8b 구문·context | 22:18:22 | `parse_rc=0 ctx=pf` | `05c-parse-check.txt` |
| A9 verify | 22:18 | ROUTE_SRC `.20` PASS, `auth whoami` = `system:serviceaccount:monitoring-api:p1-mon-pf-verify`(UID `ab58eef6…`), can-i 6/6 → AUTHZ=PASS | `06-route.txt`, `07-whoami.txt`, `08-can-i.txt` |
| A10 control01 recheck | 22:1x | 소유 UID·Grafana Pod 상태 불변 → POD_RECHECK=PASS | `control01/…/16-*` |
| A11 pftest | 22:19:12 | `127.0.0.1:13000 -> 3000` forwarding, health 200, search 인증 없음 401, 프로세스 종료 | `09-pf.log`, `10-http.txt`, `pf.ident`, `pf.pid` |
| A12 delete | 22:20:05 | 소유 UID precondition 삭제 3건, 사후 absent 3/3 | `control01/…/17-*`, `18-*`, `19-*` |
| A13 cleanup | 22:20:14 | **OLD_TOKEN_AUTH_AFTER_SA_DELETE=DENIED**(`Unauthorized`), KUBECONFIG_REMOVED=PASS, TEST_KUBECTL_REMOVED=PASS, TEMP_OBJECTS_REMOVED_CP=PASS → **RESTORE_GATE=PASS** | `runner/…/status.txt`, `12-old-token-after-sa-delete.txt` |
| A14 restore | 22:20:52 | `start_rc=0 is-active=active`. 도구 판정 `RUNNER_RESTORED_LOCAL=FAIL` | `13-runner-restore.txt` |
| S3 13b | 22:21:30 | active·running, MainPID 10779, `NRestarts=0`, Listener PID 10794 1개, `/dev/shm` kube 0 | `13b-post-restore-check.txt` |
| A15 GitHub post_restore | 22:22:06 | online·busy=false — PASS | `pc/…/post_restore-*` |

## 해석과 한계

- **N2 대조:** runner `status.txt` `TOKEN_EXP=1791293023`과 control01 `15-token-claims.txt` `exp= 1791293023`이 같습니다. A13(22:20:14)은 만료(22:23:43) 전이므로, `DENIED`는 SA 삭제에 의한 토큰 무효화를 실증합니다.
- **`RUNNER_RESTORED_LOCAL=FAIL`:** 도구가 `systemctl start` 후 최대 3초 기다리고 Listener를 한 번만 확인하기 때문에 생긴 시차입니다. 30초 뒤 13b에서 실제 복구를 확인했고, GitHub도 online입니다. 도구 status는 고치지 않았습니다.
- **A8 실행 일탈 1건:** 입력 대기 중 실행자가 블록 대신 A8 명령 줄을 먼저 붙여넣었습니다. Ctrl+C 없이 이어서 BEGIN~END 블록을 붙이고 Enter·Ctrl+D를 눌렀습니다. 그 명령 줄은 표식 밖이라 필터가 버렸고(`lines_passed=12`), 결과에 영향이 없습니다.
- **오후 canary 시작 Gate 보강:** `runner/run-20261006T1625/13c-listener-continuity.txt`는 이번 PF 시작 전(22:06:37)에 읽기 전용으로 수집했습니다. 오후 Listener PID 6852는 16:33:52 기동, `NRestarts=0`이고, journal에 16:50까지 추가 기동이 없습니다.
- 비승인 외부 접근 실패는 이 회차 범위가 아니며 9/26 run2(evidence#73)를 따릅니다.
- 일부 단계(A5·A6·A7·A10)의 정확한 시각은 각 서버 파일의 기록을 따릅니다.

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일의 SHA-256(README 포함, 자기 자신 제외)
- `*/ev-*-pf3.tgz.sha256`: 압축본 sidecar(서버 출력값과 같음)
- `ARCHIVE_CONTENTS`: 압축본별 파일 목록

AI 사용: CLAUDE_ASSISTED (명령 작성, 전달 복원·대조, README 작성)
