# P1-SEC-01 — AC-04 보완 TCP 시험 원본: mgmt 1회, edge 2회 (2026-10-06)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). AC-04(Worker 관리·노드 포트 차단) 보완으로, 승인된 수집기 `ops/p1-sec01-ac04-extra-negative/` v3(`infra-kubernetes` PR #60, merge `2fae629e57fc4ee3419bebc9a4b9a6d6a236dbcd`)를 2026-10-06에 실행한 결과 원본이다. 출발지별로 같은 Worker의 **대조 포트 연결**과 **차단 대상 포트(9100, 9101, 10250) 연결**을 짧은 TCP 접속으로 비교한다. 클러스터 객체와 정책은 만들거나 바꾸지 않는다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 수집기 | `scripts/collect-ac04-extra-negative.sh` rev `v3-20261005`, SHA-256 `4ba0ac9ad98c9a1dce7b4cf94ec7632ac0408aafbf6a7a934534cc142da699d0` (승인 값과 일치. 실행 파일을 가져온 것이며 `00-environment.txt`의 `script_sha256`과 같음) |
| 실행 | 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 수신 검증·편입 정리는 Claude Code 보조 |
| 출발지 | `mgmt`: ansible01(expected_src `10.250.10.10`). `edge`: edge01(expected_src `10.1.93.50`) |
| 전달 경로 | ansible01·edge01의 `~/p1-sec01-ac04-extra-negative/` → 사용자가 zip으로 내려받아 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신·편입 시각 | 2026-10-06 (편입 정리 11:52 KST 경) |

| 회차 | 아카이브 | SHA-256 | 수집(UTC) |
|---|---|---|---|
| mgmt | `p1-sec01-ac04-extra-neg-mgmt-20261006T010716Z.htSA0H.tar.gz` | `e5050ad9c41437cad51dababa5bc650026a0fe8e1c1b4ba41d95d55800c850bb` | 01:07:16Z (10:07:16 KST) |
| edge 1회차 | `p1-sec01-ac04-extra-neg-edge-20261006T010755Z.KJeBlh.tar.gz` | `0c9ee6f855d9a7f0f142ba5644b8a3108256eccff860055349c32f88293afe0d` | 01:07:55Z (10:07:55 KST) |
| edge 2회차 | `p1-sec01-ac04-extra-neg-edge-20261006T010806Z.3lPYV2.tar.gz` | `1a9ad6a1117a7e1d201c5800a9ae60a9b620dfbd1b12696ff7bd6fecdc695175` | 01:08:06Z (10:08:06 KST) |

## 수신 검증

- 각 아카이브 바이트 SHA-256 = 서버 sidecar(`.sha256`)와 일치. 아카이브 내부 `SHA256SUMS` 전 항목 일치(각 15개 파일). 비밀정보 패턴 검색 일치 0건.
- `completion.txt`는 수집기가 아카이브 밖에 쓰는 완료 파일이며 세 회차 모두 `COLLECTOR_STATUS=COMPLETE`, `SEAL_STATUS=COMPLETE`이다.
- 콘솔에 출력된 원문(clone HEAD 확인, 해시, 실행 중 출력)은 이 폴더에 파일로 넣지 않았다. 해당 내용은 #19의 AC-04 기록 코멘트에 있으며 서버 파일 원본이 아니다.

## 관측값 (원본 보존 — 판정 아님)

| 회차 | 종료코드 | `AC_VERDICT`(수집기 정의) | 대조 연결 | 차단 대상 9건 |
|---|---|---|---|---|
| mgmt | 0 | `BLOCKED_VALID` (`valid_block=9`) | Worker 3대 `:22` 모두 `CONNECTED` | 9/9 `TIMEOUT`(약 3.0초) |
| edge 1회차 | 10 | `INCONCLUSIVE` (`valid_block=3 inconclusive=6`) | `:30080` — `10.1.93.107` `CONNECTED`, `10.1.93.105`·`10.1.93.108` `ERROR`(rc=1, 약 2~3ms, 메시지 "연결이 거부됨") | 9/9 `TIMEOUT` |
| edge 2회차 | 10 | 위와 동일 | 위와 동일 | 위와 동일 |

- **edge는 Worker 3대 중 2대에서 대조 연결이 성립하지 않았다.** `10.1.93.105`·`10.1.93.108`의 `:30080`은 즉시 거부되었다. 이 시험 시점에 fds-app Pod가 모두 `k8s-worker02`(`10.1.93.107`)에만 있어(`kubectl` 조회, 2026-10-06 사후 확인) 다른 두 Worker에는 해당 포트를 받는 로컬 endpoint가 없었던 것으로 **추정**한다(`externalTrafficPolicy: Local`). 이 추정을 직접 확인한 원본은 이 폴더에 없다.
- 수집기는 거부 메시지를 한국어 로캘 때문에 `ERROR`로 분류했다. 수집기의 정의된 동작이며 수정하지 않았다.
- 같은 Worker에서 대조 연결이 성립하지 못한 행은 수집기 정의대로 `INCONCLUSIVE`이며 차단 근거로 쓰지 않는다. 따라서 edge 쪽 유효 차단 행은 `10.1.93.107` 3건뿐이다.

## 실행 순서와 기록상 편차 (은닉 아님)

1. **Gate 기록보다 실행이 먼저였다.** 시작 전 Gate 기록을 #19에 올리기 전에 시험을 실행했다. 이는 [#19 AC-04 기록](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6007261478)에 그대로 적었다.
2. **edge01에서 두 번 실행했다**(10:07:55, 10:08:06). 결과는 두 회차 모두 같다. 두 번 실행한 사유는 실행자가 확인 중이며 이 README는 사유를 추정해 적지 않는다. 두 아카이브를 모두 포함하고 하나를 고르지 않았다.
3. 첫 시도에서 edge01이 꺼져 있어(`No route to host`) 켠 뒤 다시 전달했다. 이 시도에는 시험 데이터가 없다.

## 한계와 주의

1. **`TIMEOUT`은 차단 주체를 구분하지 못한다.** Calico 정책, 업스트림 방화벽, 대상 무응답을 이 시험만으로 가를 수 없다. 같은 Worker에서 대조 연결이 `CONNECTED`였다는 점이 보조 근거일 뿐이다.
2. mgmt의 대조 포트는 `:22`(SSH)이고 edge의 대조 포트는 `:30080`(NodePort)이라 대조의 성격이 다르다.
3. 시도는 대상당 1회, 제한시간 3초이며 한 시점(2026-10-06 10:07~10:08 KST) 결과이다.
4. 이 폴더는 **SEC-AC-04 전체 PASS를 주장하지 않는다.** edge 6건이 `INCONCLUSIVE`이고, HEP 단독 차단 등 정책 수준 증명은 이 시험의 범위가 아니다.
5. LB에서 출발하는 시험은 하지 않았다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-04 mgmt 출발 | mgmt 아카이브 `results.tsv`, `verdict-rows.tsv`, `99-summary-provisional.txt` |
| AC-04 edge 출발 | edge 두 아카이브의 `results.tsv`, `verdict-rows.tsv`, `00-route-source.txt` |
| 실행 환경·출발 IP | 각 아카이브 `00-environment.txt`, `00-route-source.txt` |
