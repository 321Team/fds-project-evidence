# P1-MON-01 — 승인 단말 port-forward 재시험 1회차 원본 (2026-10-05 16:28~16:52 KST)

#17 [시작 기록 5990038082](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5990038082)·[실행창 승인 5990093805](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5990093805)의 port-forward 1회차 원본입니다. 결과 보고는 [#17 5990398765](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5990398765)입니다. 실행자는 MON Lead 이재환(supreme33-kr)이며, 해석은 이 README에만 적습니다.

**결과 요약:** runner에 붙여넣은 kubeconfig 앞에 다른 줄이 섞여 YAML이 깨졌고, 신원·권한 시험(A9)은 실행되지 못했습니다(AUTHZ=FAIL). 이후 정리는 모두 끝났습니다. 다만 옛 토큰 거부를 실증하지 못해 Restore Gate가 **BLOCKED**이고, runner는 offline으로 유지 중입니다. **port-forward AC는 이 회차로 판정할 수 없습니다(NOT VERIFIED).**

## 실행 소스

infra-monitoring merge `d9bc0c8d9d8cb68b07fffa6221e6f059c3ff6f0e`(승인 HEAD `6262eb0e`). 현장 전달 후 SHA-256 대조 결과입니다.
- `pf_cp.sh` `cbe25e84d91c95c8003c4a9eeb1f5810c455057447ba3f17d578d84d11c519e2` (control01)
- `pf_runner.sh` `22566e14e886c4e924e4a846749a24185dc3008d1907cd8491e01469fb868b02` (cicd-runner01)
- `pf_gh.sh` `8243b1032d323a9d71bf7b3c5601bef5cfec04ce1236c5fc2514b6a4783fcddf` (PC, `pc/pf_gh.sh`)

## 수집 정보

| 위치 | 계정 | 회차 폴더 | 이 PR의 파일 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02` | `~/pf-retest-d9bc0c8/run-20261005T1640` | `control01/pfcp.tgz`(서버에서 `tar -b 1 -czf`로 만든 압축본 원본) + `.sha256` sidecar + 풀어낸 `control01/run-20261005T1640/`(44개) |
| cicd-runner01 `10.250.10.20` | `server01_cicd-runner` | 같은 경로 | `runner/pfrn.tgz` + `.sha256` + 풀어낸 `runner/run-20261005T1640/`(14개 파일. 빈 `bin/` 디렉터리는 Git에 담기지 않음) |
| PC `10.1.93.29` | `soldesk`(Git Bash, `gh`) | `C:\Users\soldesk\pf-run-20261005` | `pc/gh-baseline-1620/`(16:18 사전 조회), `pc/gh/`(A1 pre·A4 after_stop raw JSON·meta·verdict) |

- **전달:** 서버 압축본을 `base64 -w 76`으로 화면에 출력했습니다. 줄마다 `cksum`을 붙여 받았고(control01 53/53, runner 28/28 일치), 복원한 압축본 SHA-256이 서버 출력과 같습니다(control01 `085a4a35…`, runner `b7f66ecd…`). 서버 임시 압축본은 출력 직후 삭제했습니다(`TMP_REMOVED`).
- **비밀값:** 두 회차 폴더 모두 서버에서 `eyJ`(JWT 접두) 포함 파일 0건을 확인했고, 복원본도 0건입니다. 토큰은 control01 화면에만 출력됐고 파일에는 클레임(sub/aud/iat/exp)만 있습니다. runner kubeconfig는 `/dev/shm`에만 있었고 정리 단계에서 삭제됐습니다. 이 PR에는 kubeconfig 본문이 없고, 줄 번호·길이·키 이름만 남긴 `05b-kubeconfig-structure.txt`만 있습니다.
- **PC 시각 표기:** PC Git Bash에 시간대 데이터가 없어 `pf_gh.sh`의 meta 시각이 UTC로 "GMT" 표기됐습니다. 예를 들어 `07:28:40 GMT`는 16:28:40 KST입니다.

## 단계별 결과 (KST)

| 단계 | 시각 | 결과 | 근거 파일 |
|---|---|---|---|
| A1 GitHub pre | 16:28:40 | online · busy=false · queued 0 · in_progress 0 — PASS | `pc/gh/verdict.txt`, `pre-*.json` |
| A2 control01 pre | 16:30:21 | PRE=PASS, Grafana `grafana-f65457bfd-ghl62`(ready), Service ClusterIP, Ingress 0, 임시 객체 명시적 NotFound | `control01/…/00~06*`, `pinned.env` |
| A3 runner pre / stop | 16:31:47 / 16:41:19 | PRE=PASS(ss rc=0, 13000 리스너 0) / RUNNER_STOPPED_LOCAL=PASS(inactive, Runner 프로세스 0) | `runner/…/00~03*`, `ss.log` |
| A4 GitHub after_stop | 16:42:16 | offline · busy=false — PASS | `pc/gh/after_stop-*` |
| A5 kubectl 설치 | 16:43:40 | 체크섬 OK, v1.36.4 — PASS | `runner/…/04-kubectl-sha.txt` |
| A6 임시 RBAC | 16:44:48 | server dry-run PASS, 생성 응답 UID 3개(SA `99664c97…`, Role `3d8a86ef…`, RB `fa894f44…`) — PASS | `08-*.yaml`, `09-dryrun.txt`, `10-create.txt`, `created.env` |
| A7 토큰 | 16:45:48 | 소유 UID 재대조 PASS, 호출자 kubernetes-admin, aud `https://kubernetes.default.svc.cluster.local`, exp 16:55:48, TTL 600초 — PASS | `12-owned-before-token.txt`, `13-tokenrequest-caller.txt`, `15-token-claims.txt` |
| A8 배치 | 16:46:37~16:48 | KUBECONFIG_PLACED=PASS(파일 2,786바이트, 0600, `token:` 포함) | `runner/…/05-kubeconfig-perm.txt` |
| A9 출발지·신원·권한 | 16:49 | ROUTE_SRC `.20` PASS. 신원·can-i 6건은 kubectl이 파일을 읽지 못해 실행 불가(`yaml: line 4: mapping values are not allowed in this context`) → AUTHZ=FAIL | `06-route.txt`, `07-whoami.txt`, `08-can-i.txt` |
| A10·A11 | — | 실행 안 함. port-forward 프로세스·13000 리스너 생성 없음 | — |
| 원인 기록 | 16:50 | kubeconfig 줄 구조: 1행 37자 비키 줄, 2·3행 빈 줄, 4~15행 본문(cluster 1,553자, user 990자 각 한 줄로 온전) | `05b-kubeconfig-structure.txt` |
| A12 임시 객체 삭제 | 16:50:32 | 소유 UID precondition raw DELETE 3건, 사후 absent 3건 — TEMP_OBJECTS_REMOVED=PASS(토큰 만료 전) | `17-*`, `18-delete-*.txt`, `19-*` |
| A13 runner 정리 | 16:51:33 | CLEANUP_STARTED·Gate RESET → PF_PROCESS_STOPPED=NOT_STARTED, KUBECONFIG_REMOVED=PASS, TEST_KUBECTL_REMOVED=PASS, OLD_TOKEN_AUTH_AFTER_SA_DELETE=**NOT_DENIED** → RESTORE_GATE=**BLOCKED**, RUNNER_RESTORED=NOT_RUN | `runner/…/status.txt`, `12-old-token-after-sa-delete.txt` |
| A14·A15 | — | 실행 안 함(Gate BLOCKED). runner offline 유지 | — |

## 해석과 한계

- **원인:** 붙여넣기 범위에 kubeconfig가 아닌 줄이 섞였습니다. 37자 줄의 내용은 확인하지 않았습니다. 본문의 긴 줄은 접히지 않았습니다. `place`는 `token:` 포함·권한만 검사하고 YAML 구문은 검사하지 않아 PASS로 기록됐습니다.
- **`NOT_DENIED`의 의미:** 옛 토큰이 인증에 성공했다는 뜻이 아닙니다. kubectl이 파일을 읽지 못해 `Unauthorized`를 받지 못한 것이고, 따라서 **SA 삭제에 의한 토큰 무효화도 실증되지 않았습니다.** 토큰은 16:55:48에 만료됐습니다.
- **잔여 상태:** 임시 객체 absent 3건, runner kubeconfig 삭제(`/dev/shm` 잔여 0, 16:51 확인), 시험용 kubectl 삭제, port-forward 미생성.
- 이 회차는 승인 단말 port-forward 성공·비승인 접근 실패 AC의 근거가 되지 않습니다. runner 재기동과 재시험은 #17에서 PMO/QA 판단을 받습니다.
- control01 `pre`의 정확한 시각은 `control01/run-20261005T1640/00-time.txt`를 따릅니다.

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일의 SHA-256
- `control01/pfcp.tgz.sha256`, `runner/pfrn.tgz.sha256`: 압축본 sidecar(서버 출력값과 같음)
- 풀어낸 control01 파일 44개의 해시는 서버에서 출력한 `sha256sum *` 결과와 대조할 수 있습니다. 압축본 해시가 같으므로 내용도 같습니다.

AI 사용: CLAUDE_ASSISTED (명령 작성, 전달 복원·대조, README 작성)
