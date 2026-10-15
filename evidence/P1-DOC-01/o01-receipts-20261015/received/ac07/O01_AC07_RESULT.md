# O01 AC07 1차 결과 — 제3자 수행 기록

수행 2026-10-15 KST · 수행자 이재환(supreme33-kr) · AI 사용: CLAUDE_ASSISTED(명령 안내·원본 필드 출력 보조 스크립트 작성·결함 후보 정리 보조). 명령 실행, 파일 열람, 판단 확인은 이재환이 직접 했다.

기준 카드: baseline PR174 `governance/handoffs/grafana-o01-ac07-start-20261015/O01_AC07_SESSION.md`(HEAD `101b461a`, 작성 시점 OPEN).

| 항목 | 실제 값 |
|---|---|
| 수행자 / 참여 수락 근거 | 이재환 / 2026-10-15 09:4x KST 이권욱에게 카톡으로 참여 수락 통지 후 시작 |
| AC07 코드·원본 작성/실행 직접 관여 여부와 범위 | 없음. 증적231 작성 이권욱·승인 이하영, infra-cicd#82 작성 이권욱·승인 이하영, 10/14 21:55 실행 이권욱. 이재환의 PR82·#231 리뷰·댓글 및 #16 AC07 댓글 0건(GitHub 조회) |
| 시작/종료 KST | 2026-10-15 09:44:13 / 09:50:52 (약 6분 40초. 카드 추정 30~45분보다 짧음. 보조 스크립트로 원본 필드를 모아 출력한 영향) |
| OS / Python / Git | Windows 10 Enterprise 10.0.19045 / Python 3.14.7 / git 2.54.0.windows.1 |
| 입력 repository / HEAD / 대상 status 전후 | 321Team/fds-project-evidence, 새 폴더 `C:\o01\ev`에 `--no-checkout` clone 후 `43e26384ae422f2017f1e96e6c1bb5fe46d087d4` detached. 대상 폴더 status: 시작 시 비어 있음(rc0) → verify 후 비어 있음(rc0) → 종료 시 비어 있음(rc0) |
| Manifest SHA256 | `8ef7fa2bbadae05a526cd9890dd69d16915f227c7d549d883513996a0a22bfb2` (카드 기대값과 일치) |
| 실행 명령 / 종료 코드 | `python -I -B evidence/P1-CICD-01/ac07-native-runtime-20261014/verify.py` → rc 0 (09:49:24~25 KST) |
| stdout / stderr 원본 위치 | `C:\o01\result\03-verify.stdout.txt`(SHA256 `44dc5787…5021`), `03-verify.stderr.txt`(0 B), `03-verify.meta.txt`. PowerShell 리다이렉트라 UTF-16LE로 저장됨 |
| 실제 재현 범위 / 미실행 범위 | 재현: 원본 탐색 5항목, 기존 판정기 오프라인 실행, Runbook 판독. 미실행: 서버 접속·토큰 발급·SSAR/GET 재실행·AC08(만료 후 401)·AC09. 이 결과는 1차 세션 범위이며 O01 전체가 아님 |
| 작성 중 받은 도움과 문서만으로 해결 못 한 부분 | Claude가 `C:\o01\result\o01_explore.py`(SHA256 `febcd6c9…0454`)를 작성. 원본 JSON에서 지정 필드만 판정 없이 출력하는 보조 도구이며, 출력은 `02-explore.txt`(SHA256 `1980e1e8…83db`). README와 Runbook은 notepad로 직접 열람. 문서만으로 해결 못 한 부분은 아래 결함 D1~D3 |

| 원본 탐색 항목 | 실제로 찾은 파일·필드 / 설명 |
|---|---|
| 명령·실행 호스트·시각·rc | `raw/native-execute.receipt.json`: 2026-10-14 21:55:57.39~21:55:58.84 KST, rc 0. ssh 대상 `fds-ansible01`에서 `transfer_native_probe.py --execute`(bundle `1d549ffa…`) 실행. Actions Run이 아닌 SSH broker 진단 |
| SSAR25와 실제 GET2, 미실행 범위 | `raw/native-execute.stdout` `runner_observation.permissions`: 25건 중 allow 6(fds-app transaction-api·fds-engine 각 get/update/patch), deny 19, allowed==expected 전부 일치. GET 2(두 Deployment UID `8a2af808…`, `bf825dec…`). SSAR은 허가 질의이며 금지 변경·exec는 실제로 실행하지 않음. DEPLOY=NOT_EXECUTED |
| 실패 수집과 성공 재조회 | `raw/rbac-before/`: rc 1, `KeyError: 'kind'`(List item kind 생략). `raw/rbac-before-r2/`: rc 0. 둘 다 PURE_READ_PRECHECK, token_issued=false, server_files_written=false. 조회 도구 보정이며 토큰 재발급·Runtime 재시험이 아님 |
| 코드/리뷰/병합/AC 인수 연결 | `raw/SOURCE_BINDING.json`: 검토 HEAD `db8230d7`, merge `9fb2e2dc`, 파일 8개 모두 reviewed_head 바이트 일치. `references/pr82-reviews.json`: hayeounglee APPROVED @`db8230d7`(2026-10-14 21:43:34 KST). AC 인수는 증적231 병합 `72375108`과 #16 인수 결정(외부 기록)으로 연결 |
| 전후 불변·회수·점유 해제의 범위 | `raw/POSTCHECK_SUMMARY.json`: 앱 identity/spec/imageID/Ready/restart 불변, Pod Ready 6, RBAC 관련 binding 5·role 5 불변(RoleBinding 13·ClusterRoleBinding 64 조회), probe 프로세스 0, 공개 소스 6폴더 42파일 해시 일치. `raw/WINDOW_RELEASE.json`: 21:50~22:10 창 해제, 토큰 참조 미보유. `raw/cleanup-cp1`·`cleanup-runner` rc 0. **서버 토큰 폐기는 하지 않았고 자연 만료(22:10:58)** |
| 과거 REVIEW_PENDING 출력의 현재 해석 | verify 출력과 POSTCHECK의 `AC07: RUNTIME_OBSERVED_EVIDENCE_REVIEW_PENDING`은 2026-10-14 실행 당시 값. 이후 증적231 승인·병합과 #16 AC07 인수 결정으로 현행 상태가 갱신됨. 봉인 원본은 수정하지 않음 |

판정기 확인: `verify.py`와 `references/compare_scan_observations.py`의 import는 표준 라이브러리(hashlib·json·re·pathlib 등)만 있었고, 네트워크·토큰 처리 코드는 없었다. verify 결과: `OFFLINE_CONSISTENCY=PASS`, manifest 116, receipt 20, source 8, SSAR 25(6/19), GET 2, ReadyPods 6, TTL 900.

| 발견한 문서 결함 | 영향 / 근거 | 담당자·처분·재검증 |
|---|---|---|
| D1 SSAR 건수 불일치 | `references/deploy-native-auth-probe.md` L62 "실행 순서" 5번은 "13건의 고정 SSAR", 같은 문서 "Runner 요청과 판정"과 실제 결과는 25건(allow 6/deny 19). 제3자가 기대 건수를 잘못 잡을 수 있음 | 이권욱(문서 Lead) 판단 대기. 봉인 사본은 그대로 두고 원 문서(infra-cicd)에서 정정 여부 결정 |
| D2 소스 기준 혼동 | 같은 문서 L3 머리말은 진단 소스를 PR#61 `14dba0f0`/merge `88394d7a`로 소개. 실제 AC07 실행은 PR82 merge `9fb2e2dc`. Runbook만 읽으면 실행 소스를 오인할 수 있음 | 이권욱 판단 대기. 현행 소스 SHA를 머리말에 명시하거나 README 우선을 표기하는 안 |
| D3 깨진 상대 링크 | 같은 문서 L12 `[governance.md](governance.md)`가 증적 `references/`에 없음(`Test-Path` False). 같은 폴더의 `ac07-rbac-followup-20261014.md`는 있음 | 이권욱 판단 대기. 증적 사본의 링크 한계를 README에 적거나 원 저장소 고정 링크로 대체하는 안 |
| D4(경미) README 현재 상태 부재 | README 첫머리가 "증적 독립 검토 대기·AC07 최종 인수 대기"로 남아 있음. 봉인 원본이라 정상이나, 현재 상태로 가는 링크는 세션 카드에만 있음 | 세션 카드에서 이미 보완. 추가 조치 필요 여부는 이권욱 판단 |
| D5(경미) 리뷰 원본 경로 차이 | README는 `raw/reviews82.json`, 세션 카드는 `references/pr82-reviews.json`을 가리킴(두 파일 모두 존재). verify.py는 후자를 사용 | 카드 또는 README 한쪽에 동일성 설명 추가 여부 판단 |

제3자 수행 결과: 1차 범위(원본 탐색·오프라인 판독·Runbook 판독) 완료, 오프라인 판정 PASS, 문서 결함 후보 5건(주요 3, 경미 2). DOC Lead 이권욱 검토 결과: 미입력.
남은 O01 핵심 재현 범위 / 다음 대상 / 일정: 미확정(카드 기준 다음 후보 Probe223 등은 이권욱이 지정).
O01 전체 인수·Critical 문서 결함0·DOC Freeze: 미판정.
