# P1-SEC-01 — AC-05 Secret 암호화 rollback 재시험 원본: precheck 2회(NO-GO 1, GO 1), rollback-test 1회(PASS) (2026-10-07)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 2026-10-06 rollback-test(`RESULT: FAIL`, [evidence#120](https://github.com/321Team/fds-project-evidence/pull/120))의 후속으로, 보완된 도구 v4.4(`infra-kubernetes` PR #66 병합 `9c160ea400da9f5251ccf6897ce504f6aed127bb`)를 `k8s-control03`에서 **1회** 실행한 원본이다. 스크립트가 보고한 결과는 `RESULT: PASS`이나, **이 폴더는 AC-05 PASS·NOT_MET 해소·Known Issue 종결을 주장하지 않는다.** 판정은 Review Owner 몫이다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 도구 | `scripts/sec01-secretbox-rollback-v4.sh` rev `v4.4-20261006`, SHA-256 `e80d8936cd6e846ebc04d999e9df68052497fbccfc7786d3f5bf8bd3584bb61e` (승인값과 일치, 병합 커밋 `9c160ea4`의 blob에서 가져온 사본이며 각 아카이브 `00-identity.txt`의 `script_sha256`과 같음) |
| 실행 | `k8s-control03`(`10.1.93.104`), 이하영(P1-SEC-01 Lead)이 **control03 콘솔 root에서 직접 실행**(ssh 경유 아님). 명령 안내·수신 검증·편입 정리는 Claude Code 보조 |
| 승인 | 조건부 GO [6029963808](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6029963808)·유지 [6030136381](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6030136381), 시작 Gate 기록 [6030622286](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6030622286), **START 승인(Gate 6 서면 확인) [6030663580](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6030663580)**(13:01 KST), 착수 표시 [6030671720](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6030671720)(13:04:18) |
| 전달 경로 | control03 `/root`의 archive·sidecar·completion 9개를 `server04` 홈 폴더로 복사(암호화 설정 사본 제외) → ansible01(`scp`) → 사용자가 zip으로 공유 폴더에 올려 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-07 13:2x KST |

| 회차 | 아카이브 | SHA-256 | 수집(UTC) | 파일 수 | 결과 |
|---|---|---|---|---|---|
| precheck 1 | `p1-sec01-secretbox-precheck-20261007T035556Z.EhuHPT.evidence.tar.gz` | `2ff85c91d386418652c2bea0b53eb0a1c11dc2812792fb17747e7798bf6bca54` | 03:55:56Z (12:55:56 KST) | 46 | **`RESULT: NO-GO`**, `EXIT_CODE=1` (입력 오류, 아래) |
| precheck 2 | `p1-sec01-secretbox-precheck-20261007T035636Z.pvSHLd.evidence.tar.gz` | `dabce0bf6cfc984c9a36a658751f152b486843b4560c8890280ce1f4a8567345` | 03:56:36Z (12:56:36 KST) | 46 | `RESULT: GO`, `EXIT_CODE=0` |
| rollback-test | `p1-sec01-secretbox-rollback-test-20261007T040738Z.EI6Yri.evidence.tar.gz` | `4a586ffee48d3d8c0ef46afabda10c3f6ecb0e4de9d1d661fd5604598449315e` | 04:07:38Z (13:07:38 KST) | 124 | **`RESULT: PASS`**, `OPERATION_RESULT=PASS EVIDENCE_STATUS=COMPLETE EXIT_CODE=0` |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar의 해시 값 = ansible01 재계산 = 수신 후 재계산(3/3 일치). sidecar는 서버 경로(`/root/…`)를 적고 있어 `sha256sum -c`를 쓰지 못해 해시 값을 셸로 직접 대조했다.
- **이 도구의 아카이브에는 내부 `SHA256SUMS`가 없다**(10/6 #120도 같은 구조). 아카이브 무결성은 sidecar 해시로만 확인했고, 내부 파일 목록은 완결성 표시(`EVIDENCE_STATUS=COMPLETE`)에 의존한다. 아카이브 안 `99-operation-provisional.txt`의 `EVIDENCE_STATUS=PENDING`은 봉인 전 임시 파일의 값이며 최종은 아카이브 밖 `*.completion.txt`(`COMPLETE`)다.
- 비밀정보 패턴 검색(`password|secret=|token=|BEGIN … KEY|bearer|authorization:`) 일치 0건, `secret:` 필드 0건, `.orig`·`.rolled`·`.bak`·`.db`·`.etcd-raw` 파일 없음. Secret 값·키 자료는 증적에 없다.
- **제외한 파일:** control03 `/root/enc-config-prechange-20261007.yaml`(암호화 설정 사본, 키 자료 포함)은 증적에 넣지 않았다. 해시(`2b1c6cb4…`)만 `pre-enc-backup.txt`에 있다.
- 콘솔 화면 출력(실행 중 터미널 출력)은 파일로 편입하지 않았고, 서버 파일 원본이 아니다. 같은 내용이 `run.log`에 있다.

## 관측값 (원본 보존 — 판정 아님)

### rollback-test (`run_id=20261007040738-102843e7`)
| 시각(UTC) | 관측 (`run.log` 등) |
|---|---|
| 04:07:38 | 시작 게이트: 노드 6/6 Ready. `pre-apiserver-pods-attempts.txt`: `attempt=1 rc=0 parser_rc=0 OK`(pre는 단회) |
| 04:07:39 | 재배치 설정 사전 검증, 시험 Secret 생성, 사전 접두어 `class=SECRETBOX`, provider 순서 변경 시작 |
| 04:08:19 | **재기동 관측(rollback)**: listener down + container ID 변경. 기존 Secret 모두 읽힘(시험용 제외 차이 0). 신규 Secret `class=PLAIN`(예상한 rollback 상태). 평문 Secret을 LB와 다른 CP(`10.1.93.102`)에서 각각 읽음 |
| 04:08:20 | 원래 설정으로 복원 시작 |
| 04:09:00 | **재기동 관측(restore)**: listener down + container ID 변경. **복원 설정 해시가 원본과 일치**(`2b1c6cb4…`, `00-orig-sha256.txt`·`99-restored-sha256.txt`). B59-3 `candidates=0 failure=0`. 복원 후 신규 Secret `class=SECRETBOX`. 대상 CP 직접(a, b)·LB(b)·다른 CP(b) 읽기 |
| 04:09:00 | 시험 Secret 서버 측 UID precondition 삭제 후 GET NotFound(`50-cleanup.txt`), 노드 6/6 |
| **04:09:01** | **사후 apiserver Pod 확인 1차: `NotReady: kube-apiserver-k8s-control03(false)`** (`post-apiserver-pods-attempts.txt`) |
| **04:09:06** | **2차: `OK`** (rc=0, parser_rc=0). 소유 시험 Secret 잔여 없음, 종료 |
- 사후 점검: `post-readyz.txt` 3 CP(`.102`·`.103`·`.104`) 모두 `ok`, `post-etcd-health.txt` 3 endpoint `health: true`. `61-secret-candidates.txt`·`62-secret-audit.txt`는 0바이트(후보 0).

### 10/6 FAIL과의 대조
- 10/6: 복원 재기동 관측(02:32:37Z) 1초 뒤 단회 조회에서 control03 `Ready=false` → `RESULT: FAIL`. 이번 1차 확인(04:09:01Z)도 복원 재기동 관측(04:09:00Z) 1초 뒤였고 **같은 `Ready=false`가 관측되었으며, v4.4의 제한 시간 반복 확인이 5초 뒤 2차에서 `OK`를 확인해 통과로 처리**했다. 두 회차가 같은 현상이라는 점은 10/6 FAIL 원인이 관측 시차라는 **추정에 부합**하지만 **원인을 확정하지는 않는다.**
- `parser_rc=0`은 판정 파서가 정상 종료한 정상 경로의 기록이다. B2(파서 실패 처리)를 서버에서 시험한 것이 아니다.

## 기록상 편차와 한계 (은닉 아님)

1. **precheck NO-GO 1회(입력 오류):** 12:55:56Z의 첫 precheck가 `PEER_SHAS`에 자리표시 문자열(`<control01 해시> <control02 해시>`)을 그대로 넣은 입력으로 `3CP 동일 Config 미확인: … (현재 4)`로 `NO-GO`(읽기 전용, 서버 변경 없음). 폴더를 보존했고 40초 뒤 올바른 값으로 재실행해 `GO`였다. 두 아카이브를 모두 포함했다.
2. **identity 우선 구간:** 설정 변경 시작 04:07:39Z, rollback 재기동 관측 04:08:19Z, 복원 시작 04:08:20Z, 복원 재기동 관측 04:09:00Z. 로그가 **초 단위**이고 listener down 시각이 기록되지 않아, identity 우선 설정이 실제로 로드되어 있던 정확한 구간은 이 원본으로 확정하지 못한다. control03을 거친 쓰기가 이 구간에 있었는지도 증명하지 못한다(시험 Secret b만 확인).
3. **B59-3 `candidates=0`은 변경 metadata 후보 검사이며** 모든 Secret 저장값·과거 revision/snapshot/WAL의 평문 부재를 증명하지 않는다. 업무 Secret replace는 수행하지 않았다.
4. **1회 실행 결과**이며 한 시점(2026-10-07 13:07~13:09 KST)이다. fixture는 스텁·Windows 시험이었고 Linux CI는 없다(PR #66 기록).
5. 사후 읽기 전용 확인(3 CP readyz, LB backend `UP`, Pod 3행, 노드 6/6)은 콘솔 출력 기준으로 [#19 6030768129](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6030768129)에 기록했으며, 이 폴더에는 `post-*` 파일만 서버 원본이다. LB 조회 결과는 파일로 편입하지 않았다.
6. 승인 시간표는 T0 13:00·시작 한계 13:10·복구 우선 13:15·회복 목표 13:30이며 실제 시작 13:07:38, 종료 13:09:06이다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-05 rollback·복원 | rollback-test `run.log`, `20-rolled-provider-order.txt`, `33-prefix-new-secret-rolled.txt`, `40-prefix-after-restore.txt`, `99-restored-sha256.txt` |
| AC-05 시험 Secret 정리 | `50-cleanup.txt`, `51-secrets-diff-final.txt` |
| 평문 잔여 검사(B59-3) | `61-secret-candidates.txt`, `62-secret-audit.txt` |
| 사후 Pod Ready 반복 확인(v4.4) | `post-apiserver-pods-attempts.txt`, `post-apiserver-pods.{txt,stderr,rc}`, `post-apiserver-pods-parser.{rc,stderr}` |
| 사후 상태 | `post-readyz.txt`, `post-etcd-health.txt`, `post-nodes*.txt` |
| 시작 Gate | precheck 2회 아카이브, `pre-enc-backup.txt`, `pre-3cp-config-sha.txt` |
