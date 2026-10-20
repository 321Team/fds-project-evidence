# P2-ROSA-01 — infra-rosa#5 첫 설정(bootstrap) run1~run7 · ⑫ · D-11d 원본 (2026-10-19 KST)

- 책임: [infra-rosa#5](https://github.com/321Team/infra-rosa/issues/5) (P2-ROSA-01 Sub-task 3/6, 접근 통제·RBAC·Namespace 분리) · Execution Lead 이하영
- 대상: ROSA HCP `fds-rosa-hcp` — cluster ID `2th4q1q4qf7ra35862s1u9q7f6n0vnmc`, API `https://api.fds-rosa-hcp.khht.p3.openshiftapps.com:443`, OpenShift cluster UUID `37eecf03-b7bc-45e1-8089-5a14a47fccd9`, 4.22.17
- 실행 위치: 이하영 개인 AWS CloudShell(ap-northeast-2). 원본 묶음은 CloudShell에서 만든 뒤 팀 공유 폴더(`\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트`)를 거쳐 이 저장소로 바이트 그대로 옮겼다(재압축 없음).
- 최종 보고: [#5 6268668621](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268668621)

## 결과 요약
| 단계 | 결과 | 원본 | #5 보고 |
|---|---|---|---|
| run7 bootstrap | `wrapper_rc=3 log_rc=0`(정책 승인 대기). 요청 시험 31건 중 30건 기대 일치, A-09 NOT_RUN(승인 Route host 미정). `CLASSIFY: PENDING_POLICY=20`, UNEXPECTED 0. 자동 회수 `REVOKE_VERIFIED` 2026-10-19T12:09:27Z, receipt `STATUS=POLICY_PENDING` | `rosa5-run4-7-20261019.tgz` 안 `run7/` | [6266875343](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6266875343) |
| 정책 | 플랫폼 기본 binding 20행, [infra-rosa PR#47](https://github.com/321Team/infra-rosa/pull/47) 승인·병합 `f3042f6228c4d5bdcde59c13330ceb90b287987a` | (소스 저장소) | — |
| ⑫ post-revoke-check | `D-11 RESULT: PASS`(rc=0), 2026-10-19T12:53:14Z. 승인 정책으로 ⑩-b 재판정 OK, 회수 전·새 세션 관리자 권한 없음, namespace UID 3개 일치, 관리면 ABSENT | `rosa5-run7-d11-20261019.tgz` | [6267698337](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6267698337) |
| D-11d 이재환 | PASS 6/6 (22:17~22:18 KST). 1차 22:15 401(입력 실수) 기록 포함 | `d11d-jaehwan-20261019/` (2026-10-20 수신) | [6268210444](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268210444) |
| D-11d 이권욱 | PASS 6/6 (22:25 KST) | **미수신** — 생산자 로컬 보존(아래) | [6268659431](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268659431) |

## 실행 코드(infra-rosa, 모두 이권욱 승인·병합)
| 회차 | 실행본 | 비고 |
|---|---|---|
| run1~run2 | `d2f2b2b`(PR#43) | |
| run3 | `f9a6125`(PR#44) | |
| run4 | `f67aa70`(PR#45) | |
| run5 / run6 / run7 | PR#46 브랜치 `d24ddc5` / `8051256` / `4c026e6`(실행 당시 미병합) | PR#46은 이후 `07d5390`으로 보완해 `e1d50cc`로 병합 |
| ⑫ | main `f3042f6`(PR#46 + PR#47) | |

## 회차 경과 (실패·편차를 덮지 않음)
| 회차 | 시작(KST) | 결과 | 원인 | 회수 | 승인 |
|---|---|---|---|---|---|
| run1 | 15:51 | STOP | 붙여넣기로 비밀번호 줄이 밀림(401) | 회수 확인 | GO |
| run2 | 16:38 | STOP `141/130` | Ctrl+C로 래퍼 종료 | **자동 회수 실패 → 수동 회수 16:41** | GO |
| run3 | 18:28 | STOP J-7 | scope 경고를 OTHER로 판정 | 자동 | GO, **승인 시각(18:45)보다 이른 시작** |
| run4 | 20:28 | STOP H-2 | 그룹 접미사 scope 경고 | 자동 | GO |
| run5 | 20:47 | STOP A-04 | route 시험 `--port` 누락(클라이언트 오류) | 자동 | **새 GO 없이 리드 판단** |
| run6 | 20:56 | STOP D-01 | `oc create` 거부 문구 형식 | 자동 | **새 GO 없이 리드 판단** |
| run7 | 21:06 | rc3(정책 대기) | — | 자동 | **새 GO 없이 리드 판단** |

- run3~run6의 STOP에서 권한 결과 자체는 매번 기대값과 같았다(시험 판정·명령 형식 문제).
- GO 편차 기록: [run3 STOP 6264116497](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6264116497), [run5 결정 6266440709](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6266440709), [run6 결정 6266614237](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6266614237), [run7 결정 6266788277](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6266788277), [리드 판단 회신 6267048468](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6267048468). 이 편입은 이 편차의 소급 승인이 아니다.
- 검토자(이권욱) 원본 수신·검산: run1 [6261906571](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6261906571), run2 [6265495864](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6265495864), run3 [6265280394](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6265280394), run4~7 [6267080210](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6267080210), ⑫·인계표 [6268659431](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268659431).

## 파일
| 파일 | 크기 | TGZ SHA-256 | tar SHA-256 | 내용 |
|---|---:|---|---|---|
| `rosa5-run1-20261019.tgz` | 10,194 | `66fba2a0…a656e` | `19061b25…5018` | P6 사전 산출물 + run1(래퍼 로그·증적·verify·postcheck) + `run1-p6-SHA256SUMS` |
| `rosa5-run2-20261019.tgz` | 3,661 | `c15e5921…6fd31` | `169155cb…2fea` | run2 + 수동 회수 원문 `manual-*.txt` + `run2-SHA256SUMS` |
| `rosa5-run3-20261019.tgz` | 50,695 | `02544ea5…bd99e` | `a3d76e8b…fb68` | run3 + `closure.txt` + `run3-SHA256SUMS` |
| `rosa5-run4-7-20261019.tgz` | 243,537 | `b7ed9d6b…901e` | `30683f8f…057ed` | run4~run7(각 `bootstrap.log`·`run-start/status`·`evidence-*`) + `run4-7-SHA256SUMS` |
| `rosa5-run7-d11-20261019.tgz` | 4,249 | `17ec2606…77bc` | `4a4df21b…bfee` | ⑫ `run7/d11-20261019T125233/`(자체 SHA256SUMS) + `post-revoke.log` |
| `d11d-jaehwan-20261019/` | 6개 | — | — | D-11d 이재환 원본(아래) |
| `*.tgz.sha256` | | | | 묶음 SHA-256 sidecar |
| `SHA256SUMS` | | | | 이 폴더 파일 해시 |

전체 해시는 `*.tgz.sha256`과 `SHA256SUMS`에 있다. 내부 파일 목록은 `registry/ARCHIVE_CONTENTS.json`에 있다.

- run1 묶음: 다운로드 사본(이 파일)과 CloudShell 재생성본(`f8cc0b12…`, 10,195 B)은 묶은 시각만 다르고, 목록(`TZ=UTC tar -tvzf` 해시 `ee62eb95…239d`)과 내부 `run1-p6-SHA256SUMS`(`c86c32ab…41be0`)가 같다([#5 6263257612](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6263257612)).

## D-11d 이재환 원본 (`d11d-jaehwan-20261019/`, 2026-10-20 수신)
생산자(이재환)가 공유 폴더 `d11d-jaehwan-20261019\`에 올린 6개를 바이트 그대로 옮겼다. 생산자 `SHA256SUMS` 4/4 일치, 각 파일 SHA-256이 [#5 6268210444](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268210444)의 보고값과 같다.

| 파일 | 크기 | SHA-256 | 내용 |
|---|---:|---|---|
| `d11d-jaehwan-20261019T221505.log` | 1,980 | `52a5da28e28a032ec8a0884ec343568d4865e25a15f6414e608b289bf39a8985` | 1차 transcript, 22:15:05~22:16:03 KST, `Login failed (401 Unauthorized)` → FAIL(입력 실수, 권한 질의 전 STOP) |
| `d11d-jaehwan-20261019T221702.log` | 1,939 | `ab61f033cfa68a838de714b258f21d7d888bc9d4afbd33e4d9a1e62b602c70ea` | 2차 transcript, 22:17:02~22:18:08 KST, `USER=jaehwan`, 승인 API, can-i 6개 기대값 일치, `D-11d RESULT: PASS` |
| `d11d-jaehwan.ps1` | 2,591 | `4f70ce1543299df84f6b7ebb1287f0106c53d65dbdf94a1df23154843a754c15` | 실행 파일(infra-rosa main `f3042f6` README d11d-ps 블록 + `$API_URL`·`$EXPECTED_USER`·oc 경로) |
| `run-d11d-window.ps1` | 406 | `23c1bae17e348129cc9417f13135c0ea95a28ed9caa92271d887cfc2a82da91b` | 별도 콘솔 창 실행·`Start-Transcript` 실행기 |
| `README.md` | 1,808 | `5be5106d38d598164f3e5e03336088c6338a4b9456796e5bf6711b9f6b399b25` | 생산자 설명 |
| `SHA256SUMS` | 367 | `b8b013a7bc22eabc61ef5adc9dfaacef9447b2ff0a0fa6294c5e6d45aebf8f2e` | 생산자 Manifest(위 4개 파일) |

- 비밀값 검사: 비밀번호·토큰·kubeconfig 0건. transcript에는 `Password:` 프롬프트만 있고 입력값은 없다.
- 생산자 기록: 22:13 시도는 입력 전 취소돼 transcript가 없고, `list nodes`의 scope 경고는 transcript에 들어가지 않았다.

## 미수신 (Pending)
| 항목 | 생산자 보고 해시 | 위치 |
|---|---|---|
| D-11d 이권욱 `gwonuk-d11d-20261019T132512Z.tgz`(PASS) | `3741810af9e648870eea96a60f7e7f6fc8d3a0044fccbfe80332883226e799dd` (851 B) | 권욱 로컬(공유 폴더 게시 확인, 미편입) |

받으면 이 PR(병합 전) 또는 같은 Record ID 아래 새 수집회차 폴더로 편입한다.

## 판정 범위
`RUN7=WRAPPER_RC3(POLICY_PENDING) / POLICY=PR47_MERGED / D-11=PASS / D-11d=PASS(2/2; 재환 원본 편입, 권욱 원본 미편입) / A-09=NOT_RUN / D-10=NOT_RUN / CI(infra-rosa)=NOT_RUN(check-runs 0)`

#5 첫 설정 단계의 실행 증적이다. #4/#38 Full, P2-ROSA-01 전체 AC 완료, 티켓 종결이 아니다. 해시 일치는 무결성 확인이며 시험 PASS의 단독 근거가 아니다.

## 민감정보
- **자격증명 0건:** 묶음 생성 때 kubeconfig·SA token(`t`, `sa.kubeconfig`)·`pw/`(비밀번호)·htpasswd를 제외했다. 편입 전 다시 검사해 파일명·내용(OpenShift OAuth `sha256~` token, JWT, 개인키, `client-key-data`, AWS access key 패턴) 모두 0건이었다.
- **식별자 포함:** AWS 계정 ID·IAM role/user ARN(`preflight-cluster.json` 등), OCM organization ID, 내부 노드 호스트명, run1 `p6/rosa_whoami.out`의 OCM 계정 이메일 1건. 이 저장소의 기존 P2 증적(예: `evidence/P2-IAC-01/`)과 같은 수준의 식별자이며, 원본 바이트 보존 규칙에 따라 가리지 않고 그대로 둔다. 검토에서 가림이 필요하다고 판단하면 원본은 공유 폴더에 두고 가린 파생 묶음으로 바꾼다.
