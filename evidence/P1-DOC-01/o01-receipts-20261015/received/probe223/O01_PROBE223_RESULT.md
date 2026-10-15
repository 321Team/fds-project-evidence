# O01 후속 결과 — AC07 정정본 확인 + Probe223 오프라인 재확인

수행 2026-10-15 KST · 수행자 이재환(supreme33-kr) · AI 사용: CLAUDE_ASSISTED. Claude는 명령 안내, 원본 필드 출력 보조 스크립트 작성, 결과 정리를 도왔다. 명령 실행, 문서·원본 열람, 각 항목 확인과 판단은 이재환이 직접 했다.

기준 카드: baseline `b865232d09e33b94fe5544a69a9d81c1d98add6c`의 `governance/handoffs/o01-ac07-correction-probe223-20261015/`(AC07_CORRECTION_CONFIRMATION.md, PROBE223_SESSION.md, PROBE223_RESULT_TEMPLATE.md).

## 1부 — AC07 정정본 확인

| 항목 | 실제 결과 |
|---|---|
| 확인자 / KST 시각 | 이재환 / 2026-10-15 10:34:45 시작, D1~D4 판독 후 10:37:44에 2부로 넘어감 |
| 읽은 문서 merge SHA | infra-cicd `0b0412a293dfb00fa1437d484ca012d1a4898412`: `docs/deploy-native-auth-probe.md`, `docs/o01-ac07-reading-notes-20261015.md`(브라우저에서 GitHub로 열람) |
| D1 | 정정 Runbook "실행 순서" 5번이 "25건의 고정 SSAR(allow 6 / deny 19)"로 바뀐 것을 확인 |
| D2 | Runbook 머리말에 "AC07 실측 기준: PR #82 merge `9fb2e2dc`, 검토 HEAD `db8230d7`"이 먼저 나오고, PR #61은 초기 구현 이력으로 분리된 것을 확인 |
| D3 | 판독 보완 문서의 "AC07 실행 소스의 governance.md" 고정 링크(infra-cicd `9fb2e2dc`)가 열리는 것을 확인 |
| D4 | 판독 보완 문서 "봉인 후 승인·인수 이력"에서 README·verifier의 대기 표기는 당시 값이고, 증적231 병합(`72375108`)과 #16 AC07 인수를 함께 읽는다는 설명을 확인 |
| D5 | `raw/reviews82.json`과 `references/pr82-reviews.json`의 SHA256이 둘 다 `4b4358b7c9d5c952d8ae5ca831d1742e2816911a54f5e8a12eba7d2e4f0fecc1`(PowerShell `Get-FileHash`, 10:34:45) |
| 남은 문제 | 없음. AC07 verifier는 카드에 따라 다시 실행하지 않음 |
| 도움받은 부분 | 확인할 위치 안내와 D5 해시 명령은 Claude가 제시. 판독과 링크 열람은 본인 |

## 2부 — Probe223 재확인

| 항목 | 실제 값 |
|---|---|
| 수행자 / 참여 수락 / 관여 범위 | 이재환 / 2026-10-15 이권욱 요청(카톡)에 따라 수행 / **Probe223 증적 PR223 독립 리뷰어로 검증기를 실행·승인한 이력 있음**(review 5511991541). K8S PR86 코드 작성·실행은 하지 않음 |
| 신규 판독 또는 재확인 | **기존 참여자의 재확인 세션** |
| KST 시작·종료 / OS·Python·Git | 10:37:44 / 10:39:05(`00-start.txt`, `08-end.txt`) / Windows 10 Enterprise 10.0.19045, Python 3.14.7, git 2.54.0.windows.1 |
| 입력 repository·HEAD / git status / 각 rc | fds-project-evidence, AC07 때 쓴 `C:\o01\ev` checkout 재사용, HEAD `43e26384ae422f2017f1e96e6c1bb5fe46d087d4`(rc 0, `01-head.txt`). 대상 폴더 status: 시작 전 빈 출력 rc 0(`02-status-before.txt`), 종료 후 빈 출력 rc 0(`07-status-after.txt`). `python --version` rc 0(`03-python.txt`) |
| Manifest SHA256 | `46d41a1a733caec603209280f4277e3f41592070d14f47ecd6f030fb4b08e8fe`, 대상 파일 수 109(`04-manifest.txt`). 카드 기대값과 일치 |
| verifier 명령 / 전후 KST / 종료 코드 | `python -I -B evidence/P1-K8S-01/http-probe-runtime-20261014T0950/verify_result.py evidence/P1-K8S-01/http-probe-runtime-20261014T0950` / 10:39:05~10:39:05 / rc 0 |
| stdout·stderr 경로 / SHA256 | `06-verify.stdout.txt` `f65e5998…f7f3`, `06-verify.stderr.txt` 0 B(`e3b0c442…b855`), `06-verify.meta.txt`. PowerShell 리다이렉트라 UTF-16LE로 저장됨 |
| verifier 결과 | `HTTP_PROBE_RUNTIME_PASS_WITH_RECORDED_OBSERVATION_LIMITS`, stop 1·cont 0, hold 81.79초, 같은 Pod UID `e349b045…` restart 1, 다른 Pod restart 0, 이미지·spec 불변, 배치 1/1/1, HTTP·MON 60초 회복, 관측 300·오류 0 |
| 실행하지 않은 것 | `apply_once.py`, `verify_and_stage.py`, `engine_stop.py`, 관측·서버 수집기(열람만). 서버 접속·SIGSTOP·토큰 발급 없음 |

### 원본 탐색 (보조 스크립트 출력 `05-explore.txt` + README 직접 열람)

| 항목 | 찾은 파일·필드 / 설명 |
|---|---|
| 명령·계정·시각·rc | `apply-once/receipt.json`: 10/14 09:50:41~09:52:03 KST, route `fds-ansible01 -> svc_ansible@10.1.93.107`, rc 0. `remote-originals/input.json`: 대상 worker02, Pod `fds-engine-65479b5bf-4gfgq`(UID `e349b045…`), PID 1290996, container `7b24cf1f…`, 창 09:45~09:55 시작·10:20 종료, source sha `8b9fe37d…` |
| STOP·CONT | `remote-originals/events.jsonl` 5줄: STOP_INTENT·STOP_SENT 09:50:42 → ORIGINAL_EXIT_OBSERVED_NOT_PROBE_PASS·ORIGINAL_EXITED_NO_CONT·FINAL_ORIGINAL_EXIT 09:52:04. STOP 1회, CONT 0회. 원 프로세스는 kubelet 재시작으로 종료됐고 실행기가 재개하지 않음 |
| Ready·Endpoint·Killing·재시작 | `observer.jsonl` 300 tick: tick 0(09:48:51) Ready/Endpoint true → readiness 실패 이벤트 09:50:46~, liveness 실패 09:50:54~ → tick 68(09:51:07) Ready=False·engine Endpoint 제외 → **Killing 09:51:34 "failed liveness probe, will be restarted"** → tick 97(09:52:05) restartCount 1, containerID `…11fa51dc8e31` → tick 102(09:52:15) Ready·Endpoint 복귀. 300 tick 내내 같은 Pod UID, 다른 워크로드·노드 정상 |
| 실패 관측과 회복 보충 | `worker-http.receipt.json` rc 1, `worker-http.stderr` `ProcessLookupError`(원 PID 종료 경쟁), `worker-http.jsonl` 67줄 보존. 회복은 별도 `http-recovery/stdout.json`(READ_ONLY_RECOVERY_SUPPLEMENT, 09:53:21~09:54:21, readyz·livez 200, stable60 true)으로 보충. **실제 HTTP 최초 회복 시각은 기록되지 않음** |
| MON·영향·회복 | `mon-during`: fds-engine `10.244.69.193:9090` 한 대상만 down(verifier가 확인). `mon-stable` 09:52:29~09:53:49 stable60 true. `recovery-edge`(edge01 09:52:30): Worker NodePort readyz 200·`/metrics` 404, API 변경 0·DB 쓰기 0 |
| 공급·리뷰 | `remote-originals-receipt/stdout.json`: 원격 파일 base64·sha·0600, 새 컨테이너 `737b90c6…`(같은 Pod UID, 09:52:04 기동). `GITHUB_MERGE_REVIEW_RECEIPT.json`: PR86 HEAD `d53ce00f` merge `e60e0223`(APPROVED) 등 2건, 10/14 09:57:59 KST 조회 |
| kubelet journal | `kubelet-journal-utc/stdout.json` rc 1, `-- No entries --`. 원인 연결은 같은 UID의 Kubernetes liveness/Killing 이벤트로만 함 |

### 관측 한계 (verifier `limits`와 README와 일치)
1. control01에서 Pod로 직접 보낸 HTTP는 주입 전부터 실패했다. 장애 근거는 worker02 실제 HTTP와 control01 API 관측이다.
2. worker HTTP/process 수집기가 원 PID 종료 때 rc 1로 끝나, HTTP 최초 회복 순간은 없다. 60초 회복 보충은 따로 있다.
3. kubelet journal에 기록이 없다.
4. 관측기와 회복 보충은 독립 코드 리뷰를 받지 않은 순수 관측 도구다.
5. verifier 출력의 `independent_evidence_review: PENDING`, `final_APP_regression: NOT_RUN`, `DB_acceptance`, `W4`는 **10/14 당시 값**이다. 이후 PR223 승인·병합(`ddd1e38c`), 224 회귀, DB#11 종결이 있었으며 봉인 원본은 바꾸지 않는다.

### 문서 결함 후보
| 결함 후보 | 근거·영향 | 처분 / 재검증 |
|---|---|---|
| P1(경미) 호스트 간 시각 기준 | `apply-once/receipt.json`(ansible01 기록)의 종료 09:52:03.67이 `remote-originals/events.jsonl`(worker02 기록)의 원 프로세스 종료 09:52:04.27보다 약 0.6초 빠르다. ssh 래퍼는 원격 종료 뒤에 끝나야 하므로 두 호스트 시계 차이로 보인다. README에는 시각을 비교할 때 어느 호스트 시계를 쓰는지 적혀 있지 않아, 순서를 거꾸로 읽을 수 있다 | 이권욱 판단. README 또는 카드에 "시각은 기록 호스트 기준, 호스트 간 비교 시 초 단위 오차 가능"을 한 줄 추가하는 안. 판정 결과에는 영향 없음 |

그 밖에 README·세션 카드·verifier 출력 사이의 시각, 횟수, 상태값 불일치는 발견하지 못했다(점검 범위: 위 원본 탐색 7항목과 README 표).

## 결과 파일 (`C:\o01\result-probe223\`)
`00-start.txt`, `01-head.txt`, `02-status-before.txt`, `03-python.txt`, `04-manifest.txt`, `05-explore.txt`, `06-verify.stdout.txt`/`.stderr.txt`/`.meta.txt`, `07-status-after.txt`, `08-end.txt`, `p223_explore.py`(Claude 작성 보조, SHA256 `7e8c957c…53be`), 이 결과 양식.

수행자 결과: 1부 D1~D5 확인 완료, 2부 Probe223 오프라인 재확인 PASS(기존 참여자 재확인), 경미 결함 후보 1건. DOC Lead 검수: 미입력. 잔여 핵심 재현·O01 전체 인수·Critical 문서 결함0·DOC Freeze: 미판정.
