# P1-SEC-01 — AC-05 Secret 암호화 rollback 시험 원본: precheck(GO) 1회, rollback-test(FAIL) 1회 (2026-10-06)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). AC-05(Secretbox 암호화 설정의 rollback·복구)를 승인된 도구 `ops/p1-sec01-secretbox-rollback/` v4.3(`infra-kubernetes` PR #59, merge `f023caff4f20b7cac6a15308b735431d7166cf2c`)으로 `k8s-control03`에서 실행한 원본이다. **rollback-test의 최종 결과는 `RESULT: FAIL`이며 이 폴더는 PASS를 주장하지 않는다.** 실패는 시험 본문이 아니라 마지막 사후 점검 한 줄이다(아래 참조).

## 출처와 수신

| 항목 | 값 |
|---|---|
| 도구 | `scripts/sec01-secretbox-rollback-v4.sh` rev `v4.3-20261005`, SHA-256 `10144527bef979a48331a3447c5beef4b05d2ffb8e908b78b9b5c6596e0f3c5c` (승인 값과 일치, 두 아카이브 `00-identity.txt`의 `script_sha256`과 같음) |
| 실행 | `k8s-control03`(`10.1.93.104`), 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | control03 `/root` → ansible01 → 사용자가 zip으로 내려받아 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신·편입 시각 | 2026-10-06 (편입 정리 11:56 KST 경) |

| 회차 | 아카이브 | SHA-256 | 수집(UTC) | 파일 수 | 결과 |
|---|---|---|---|---|---|
| precheck | `p1-sec01-secretbox-precheck-20261006T020633Z.myI3CR.evidence.tar.gz` | `e5aa29d7ee03b69930717ea59a8cc1ba707eab2d9e6138265a072dc337fba5a9` | 02:06:33Z (11:06 KST) | 43 | `RESULT: GO`, `EXIT_CODE=0` |
| rollback-test | `p1-sec01-secretbox-rollback-test-20261006T023150Z.5as7sj.evidence.tar.gz` | `1fc2f816e5616f3c8d150d797dbf10a6c7e855754479da58e6b1e17e53003ade` | 02:31:50Z (11:31:50 KST) | 118 | **`RESULT: FAIL`**, `OPERATION_RESULT=FAIL`, `EVIDENCE_STATUS=COMPLETE`, `EXIT_CODE=1` |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar의 해시 값(2/2). sidecar는 서버 경로(`/root/…`)를 적고 있어 `sha256sum -c`는 이 저장소에서 쓰지 못하고 해시 값을 직접 대조했다. 아카이브 내부 파일 목록은 완결되어 있고(`EVIDENCE_STATUS=COMPLETE`), 비밀정보 패턴 검색 일치 0건이다.
- **Secret 값·키 자료는 증적에 없다.** 시험은 Secret의 값을 출력하지 않도록 설계되었고(`.etcd-raw` 임시 파일은 실행 폴더에 남지 않음, 실행 폴더 `.etcd-raw` 개수 0), 암호화 설정 파일은 해시만 기록한다.
- 콘솔에 출력된 원문(해시 확인, LB 조회, 사전 점검 출력 등)은 이 폴더에 파일로 넣지 않았다. 해당 내용은 #19 기록 코멘트에 있으며 서버 파일 원본이 아니다.

## 관측값 (원본 보존 — 판정 아님)

rollback-test(`run_id=20261006023150-006b185d`, 시작 02:31:51Z = **11:31:51 KST**, 종료 02:32:38Z). 아래는 `run.log`와 각 `*.txt`에서 읽은 값이다.

| 단계 | 관측 |
|---|---|
| 사전 | 노드 6/6 Ready. 시험 Secret 3개 생성, 사전 접두어 secretbox 확인 |
| 변경(provider 순서 identity 우선) | control03 apiserver 재기동 관측 02:32:27Z(listener down + container ID 변경). 신규 Secret 접두어 **PLAIN**(예상한 rollback 상태). 기존 Secret은 모두 읽힘(시험용 제외 차이 0). 평문 Secret을 LB와 다른 CP(`10.1.93.102`)에서 각각 읽음 |
| 복원 | 재기동 관측 02:32:37Z. 복원 설정 SHA-256 `2b1c6cb42f1699eb2043893da54eff6d37aa670f8ff1ccd219e1f735b9b63ecc` = 시험 전 원본(`00-orig-sha256.txt`, `99-restored-sha256.txt`, `pre-3cp-config-sha.txt`의 3CP 값과 동일) |
| 복원 후 | 복원 후 신규 Secret 암호화 재확인(secretbox). 읽기: 대상 CP 직접, LB, 다른 CP 모두 성공 |
| 변경 Secret 검사(B59-3) | `candidates=0 failure=0` (`61-secret-candidates.txt`, `62-secret-audit.txt`가 비어 있음) |
| 정리 | 시험 Secret 3개(a, b, c)를 서버 측 UID precondition 삭제로 정리, 삭제 후 GET NotFound 확인(`50-cleanup.txt`) |
| 사후 | 노드 6/6 Ready. **`FAIL: apiserver Pod 상태 비어 있음/NotReady`**(02:32:38Z) |

### FAIL의 원인과 해석

- `post-apiserver-pods.txt`는 `kube-apiserver-k8s-control01` true, `control02` true, **`control03` false**(RESTARTS 0)를 기록했다. 복원 재기동 관측(02:32:37Z) 1초 뒤에 Pod Ready를 한 번 읽어서, 방금 재시작한 control03 apiserver가 아직 Ready가 아니었다.
- 같은 실행의 `post-readyz*.txt`는 `10.1.93.102`, `10.1.93.103`, `10.1.93.104` 모두 `readyz: ok`이고 `post-etcd-health.txt`도 3/3 `health: true`다. 즉 시험 본문의 복원·검증과 Pod Ready 사후 점검이 같은 시각에 어긋났다. **FAIL을 PASS로 바꾸지 않는다.** 도구의 사후 점검이 재시작 직후의 일시 NotReady를 기다리지 않는 설계인지는 도구 작성 쪽의 판단 대상이다.
- 실행 후 실제 서버 상태는 실행자가 별도로 확인했다(`kube-apiserver-k8s-control01~03` 1/1 Running, control03 RESTARTS 0, readyz 3/3 ok, LB `show stat` k8s-control01~03 `UP`, BACKEND `UP`). 이 사후 확인은 콘솔 출력이며 이 폴더의 서버 원본이 아니다.

## 실행 순서와 기록상 편차 (은닉 아님)

1. **시작이 승인 시각보다 늦었다.** 승인 T0는 11:30이었고 실제 시작은 11:31:51 KST(1분 51초 늦음)이다. 이 편차는 [#19 AC-05 결과 기록](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6008210758)에 적었으며 시작 시각은 권욱(Review Owner)이 카카오톡으로 확인했다(사후 확인, 카톡 원문은 이 폴더에 없음).
2. precheck(11:06 KST)는 시험 직전 읽기 점검이며 Gate 대체 아님. 3CP 설정 해시 일치(`pre-3cp-config-sha.txt`)와 복구 사본 `/root/enc-config-prechange-20261006.yaml`(모드 600, 소유 root:root, 원본과 해시 동일, `pre-enc-backup.txt`)은 두 아카이브 안의 서버 원본에 기록되어 있다.
3. **이 폴더에는 LB 제외·복귀(`haproxy`) 조작 기록이 없다.** 시험 시간은 약 47초이며 이 아카이브에서 LB 제외 여부를 확인할 수 있는 파일은 없다. LB 백엔드 상태는 사후 콘솔 조회만 있다.

## 한계와 주의

1. 시험 중 control03을 거친 Secret 쓰기는 identity 우선 상태에서 저장될 수 있다(약 10초 구간). B59-3 검사는 `candidates=0 failure=0`이었지만 이 검사가 모든 실제 업무 Secret의 etcd 접두어를 전수 확인한 것은 아니며(변경된 Secret 중심 점검), 과거 revision·snapshot·WAL의 평문은 다루지 않는다.
2. 한 번의 실행이며 한 시점(2026-10-06 11:31 KST) 결과이다. 재시험은 하지 않았다. 재시험 여부는 Review Owner 판단 대기 중이다.
3. 이 폴더는 **SEC-AC-05의 PASS·MET를 주장하지 않는다.** 결과 `FAIL`을 그대로 보존한 원본이다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-05 rollback·복원 | rollback-test `run.log`, `20-rolled-provider-order.txt`, `33-prefix-new-secret-rolled.txt`, `40-prefix-after-restore.txt`, `99-restored-sha256.txt` |
| AC-05 시험 Secret 정리 | `50-cleanup.txt`, `51-secrets-diff-final.txt` |
| AC-05 평문 잔여 검사 | `61-secret-candidates.txt`, `62-secret-audit.txt` |
| 사후 상태 | `post-*` 파일(Pod, readyz, etcd health, nodes) |
| 사전 점검 | precheck 아카이브 `pre-*` 파일, `99-operation-provisional.txt` |
