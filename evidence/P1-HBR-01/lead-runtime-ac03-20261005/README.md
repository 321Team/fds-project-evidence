# P1-HBR-01 AC-03 — Worker×3 로그인/Pull/Push-DENY 및 control01 Pod 시작 시험(Runtime) 원본 편입 (2026-10-05)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible` → 각 노드 개인 계정. 원본 전사·정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-03 PASS 선언이 아니며 인수 판단은 이권욱 몫**이다. 시험 스크립트 출력도 "AC-03/AC-05 Runtime 인수가 아님"이라고 명시한다.

## 근거(승인·소스)

| 항목 | 값 |
|---|---|
| Runtime 승인 | [#13 AC-03 조건부 GO](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5987917779) |
| 시작 기록 | [#13 시작 Gate 기록(T0 15:50 / 시험 중단 16:30 / Tend 17:00)](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5989479105) |
| 종료·정리 기록 | [#13 종료·정리·복구 완료 기록](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5989673353) |
| MON 비중첩 확인 | [#13 이재환](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5988307840) |
| 실행 소스 | infra-harbor-trivy PR #10 병합 `030a4ce14acdab3a58c4767455b7555aaf8ce949` (`worker-node-access-test.sh`, `control-plane-pod-start-test.sh`) |
| 대상 Review Run | `hbr-20261002-161052-d57ab5dc`, TEST_TAG `ifup-20261002T071118Z`, manifest digest `sha256:7a3b263c938493c827d8295e64f23d9386ffcbea75516ea03a6b65196636bfc6` |

## 시간 순서 (사실 그대로, KST)

| 시각 | 사건 |
|---|---|
| 09:42~09:47 | 현장 사전 점검·소스 준비(`observations/`) |
| 15:41:09 | 시작 직전 읽기 전용 확인(노드 6/6 Ready, readyz 통과, SA·Secret 존재, Harbor TLS `HTTP=401 verify=0`) — 터미널 출력, 원본 파일 없음 |
| 15:43 | #13 시작 기록 게시(T0 15:50) |
| **15:44:39~44** | **worker01 1차 시도 — 로그인 401로 Pull/Push 시험 전 중단**(`observations/worker01-attempt1-login401-terminal-transcript.txt`). 실행자 비밀번호 입력 오타. **시작 기록의 T0(15:50)보다 이르게 시작** |
| 15:47:21~22 | worker01 2차 — Pull+정확한 CRI RepoDigest PASS, Push DENY PASS |
| 15:48:59~49:04 | worker02 — PASS |
| 15:49:49~53 | worker03 — PASS |
| 15:55:34~15:57:15 | control01에서 worker01/02/03 대상 Pod 시작 시험 — 3건 PASS, Pod 삭제 확인 |
| 15:57:52 | 정리 확인: `fds-app`에 `p1-hbr-*` Pod 0개, 노드 6/6 Ready — 터미널 출력, 원본 파일 없음 |
| 15:59 | #13 종료·정리·복구 완료 기록 게시 |

## 폴더 구성

| 경로 | 내용 | 성격 |
|---|---|---|
| `server-originals/k8s-worker0{1,2,3}-node.log` | Worker-local 시험 로그(`tee`로 저장된 노드 실제 파일) | 서버 원본, 노드 터미널 출력 해시 및 ansible01 회수본과 대조 |
| `server-originals/k8s-worker0{1,2,3}-control.log` | control01 Pod 시작 시험 로그 | 서버 원본, 동일 |
| `observations/worker01-attempt1-login401-terminal-transcript.txt` | worker01 1차 시도 터미널 출력 전사 | **원본 아님**(전사). 원본 파일은 2차 시도의 `tee`가 같은 이름으로 덮어써 미보존, 당시 출력 해시 `bc193910…c16`은 대조 불가 |
| `observations/control01-precheck-20261005T094219.txt`, `workers-precheck1-…`, `workers-precheck2-…` | 09:42~09:44 읽기 전용 사전 점검 | 터미널 전사 |
| `observations/source-prep-ansible01-20261005T094744.txt` | ansible01 소스 clone(@030a4ce)·파일 8개 해시·번들 준비 | 터미널 전사, 서버 해시 없음 |

원본 로그의 CR 문자는 `worker*-node.log` 3개에 **각 21개**(ESC 문자 각 46개)이며 `nerdctl` pull의 ANSI 진행 표시 출력에 따른 것이다. `*-control.log` 3개는 CR 0개이다. 바이트 그대로 보존한다(저장소 `* -text`). 이전 초안의 "각 5개, 비밀번호 프롬프트"는 CR이 든 *줄* 수(5)를 문자 수로 잘못 적은 것이고 원인도 틀렸으므로 정정한다(권욱·이재환 리뷰 지적).

## 로그 해시 대조

노드에서 시험 직후 출력된 `sha256sum` 값, ansible01 회수본(`~/ac03-evidence-20261005/`), 공유 폴더 경유 본 PC 복사본 모두 아래와 같다.

| 파일 | SHA-256 |
|---|---|
| `k8s-worker01-node.log` | `ca2c1c1475fe299ffefca7be4ae2448f3ba2516badf41a83f6fedb22e6384ba9` |
| `k8s-worker02-node.log` | `9ab811ed7b048fce533ee7c5402558943221fd3ebfa5d625fd2d075a345baf7c` |
| `k8s-worker03-node.log` | `5ecc2880bfece664a95c743b308abee87df2fe587b197a6f62c91bb7ffa1d381` |
| `k8s-worker01-control.log` | `91cc9cdae88618420b4b02e2c005799d891b18e929a7af5c001028c48ecb27d0` |
| `k8s-worker02-control.log` | `eaaf18158d21d9daa5321eb0d9fad504c3939406dec5aee0cbdbacbfb8e991a1` |
| `k8s-worker03-control.log` | `b97bc20a468ad89db1338c0c723e77029ad02adf4b47c098be28858f6ee82228` |

## 로그가 보여 주는 것

- 세 Worker 모두 `AC03_NODE_RESULT=PASS`(로그 안의 판정 토큰): 승인 `robot$worker`로 로그인·Pull, `crictl inspecti` RepoDigest가 승인 digest와 정확히 일치, 고유 tag Push는 권한으로 DENY.
- control01(`k8s-control01`)에서 worker01/02/03 대상 Pod 3건 `AC03_CONTROL_RESULT=PASS`: Harbor manifest 직접 조회 digest와 Pod 컨테이너 digest 일치, UID 조건부 삭제 확인(`CLEANUP: confirmed deleted`).
- **프로세스 종료코드(RC 0)의 근거:** 서버 원본 6개 파일에는 RC 필드가 없고 PASS 토큰·cleanup 토큰만 있다. 각 시험의 `AC03_NODE_RC=0`·`AC03_CONTROL_RC[노드]=0` 값은 **실행자 터미널 출력(콘솔 제출, CONSOLE_SUBMITTED)**이며 별도 RC 원본 파일은 보관하지 않았다. PASS 토큰과 프로세스 RC를 같은 근거로 취급하지 않는다. 1차 시도 전사본에만 `AC03_NODE_RC=1`이 있다(전사본, 원본 아님).

## 한계·정정 (숨기지 않음)

1. **T0 이전 시작:** 시작 기록 T0 15:50보다 5분 이른 15:44:39에 첫 시도가 시작됐다. 15:44~15:50 MON 동시 작업 유무는 이재환 확인 요청 상태이다.
2. **worker01 1차 실패 로그 미보존:** 위 표와 같이 원본 소실, 전사본만 있다. 오타 판단에 따른 1회 재시도가 GO의 "인증 이상 시 STOP"에 부합하는지는 이권욱 검토 대상이다.
3. **인수 범위:** 이 시험은 로컬 검사 + Pod/Harbor digest 바인딩 + 정리의 관측이다. 이미지 pull 발생 자체나 AC-05(Push→Deploy→4/4→롤백)를 입증하지 않는다.
4. 15:41 시작 직전 확인, 15:57 정리 확인은 터미널 출력이며 원본 파일 해시가 없다(#13 코멘트가 근거).
5. 서버 측 독립 검산은 하지 않았다. 해시는 실행자 보고 + 회수본 대조이다.
6. MON 23/23 상태는 종료 시점에 재조회하지 않았다(MON Lead 기준).
7. 1차 시도의 `[sudo]` 프롬프트와 노드 로그 내 비밀번호 값은 없음을 확인했다(프롬프트 문구만 존재).
