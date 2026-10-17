# 역할 185 단일 회차 실패·회수 원본 대조

판정: **ROLE185_FAILED_OWN_CLEANUP_CONFIRMED**. 첫 MON 묶음 실패로 전체 185 검증은 미충족이다. 자기 컨테이너 제거와 실행기 종료는 별도 확인했다. 현장 수정·재시작·재회수·새 창 제안은 하지 않았다.

## 대상과 원본

- 호스트 `cicd-runner01`, 실행 계정 `ansible-verify` UID1001/GID1002.
- 회차 `p1-role-b5653943c28b4ae8`, boot `188c5f37-daf8-4fda-8edd-2634ead61801`.
- source HEAD `32f8d21e6951178e51a8e82aadf4fe70368ca389`.
- 후보 tar `f019e7ea053cce1097521786c01a06b00123e16ef1c7ac8549d936cdfa1ea966`, manifest `cc361f09c33efea6965f126c8ea284342eac8ce6dba3520ea285b0571dc5d7c7`.
- CID `d507a95d7392fb9567a58079d108c7cec316db6064b67642f1ca5cd0589684c9`.
- 실제 시작 2026-10-16 **08:50:36.420 KST**, 컨테이너 종료 **08:50:56.721 KST**, 제거 응답 **08:50:57.213 KST**, 정확 부재 응답 **08:50:57.283 KST**.
- **08:53:49 KST 사후 읽기**: 같은 boot·계정·rootless 저장소·CID에 `exists rc1`, 실행기 0, 관측/프로세스 읽기 오류 0.
- **08:53:59 KST 읽기 수집**: 서버 원본 645개 + 명시적 수집 파생 영수증 1개. `runtime-originals-20261015T235358062170.tar` SHA256 `b887a4194a25cf7e191733f9942409fc3f2d39fcd786ede48c7709051740f639`.
- 645개 원본 전체의 크기/SHA, 공급 manifest 476개 해시·원래 mode, 실제 공급 파일 집합, 호스트 명령 영수증 20개와 stdout/stderr 해시를 대조했다. 수집본은 `originals-20261015T235358062170/`에 있다.
- 중앙이 전달한 사용자의 콘솔 결과(stage/plan rc0, execute rc1, FIXTURE_FAILED, OWN_CONTAINER_REMOVED, evidence COMPLETE)는 별도 수집한 operator 로그와 host FINAL에 일치한다. 전달된 회신을 독립 기술 증적으로 대체하지 않았다.

## 최초 실패와 원인

**관측 사실**: `mon-2.16.19/orphan-refused-before-copy.log`의 첫 실제 `ansible.builtin.stat`가 `UNREACHABLE`로 끝났다. `/root/.ansible/tmp` 생성 명령 rc1이다. 같은 오류가 `copy-defence-preserves-existing.log`, `fresh-baseline-can-backup.log`에서 반복됐다. 마지막 백업 파일이 생성되지 않았는데 harness 122행이 `original.read_bytes()`를 실행하여 `FileNotFoundError`가 발생했다. MON subprocess rc1 → container `COMMAND_FAILED:mon-2.16.19:1` → host `FIXTURE_FAILED` 순이다. timeout·OOM·외부 신호가 원인인 기록은 없다.

**코드·환경 결속**: `TERMINAL.json`은 HOME=/scratch/home, rootfs 읽기 전용, `/root` 쓰기 mount 없음, `/scratch`와 `/results`만 지정된 쓰기 경로임을 보여준다. `run-egress-recovery.py` 43행은 roles_path만 있는 ansible.cfg를 만들고 remote_tmp를 지정하지 않는다. 패키지 안의 Ansible 2.16.19/2.21.3 원본은 기본 remote_tmp=`~/.ansible/tmp`, 사용자 홈 확장, `$HOME`과 구별되는 사용자 tilde 확장을 명시한다. 발췌와 각 wheel/member SHA는 `ENGINE_SOURCE_EXCERPTS.json`에 저장했다. 라이브러리 import·추가 실행은 하지 않았다.

**판단**: 고정 격리 실행환경과 fixture 임시 경로 계약이 맞지 않은 것이 직접 차단사항이다. 실제 로그는 경로 생성 실패를 입증하지만 underlying mkdir stderr의 세부 errno는 보존되지 않았다. 읽기 전용 루트와 해당 경로 선택은 수집한 환경/코드에 부합한다. 이 결과만으로 운영 MON/NTP 역할 자체가 잘못됐다고 판단할 수 없다.

**사전검사가 놓친 이유**: `localhost-cli-preflight`는 assert(true)만 실행했다. 패키지의 assert action은 `_requires_connection=False`이므로 실제 모듈 전송·임시 디렉터리 생성 경로를 시험하지 않는다. 실제 preflight 로그는 정상이나 그 뒤 stat 실행 가능성을 보증하지 않는다.

## 수행 범위와 집계 한계

| 구분 | 실제 결과 |
|---|---|
| Stage / plan | 각 rc0 |
| 격리 gate | ISOLATION passed=true, source/manifest/bind identity 일치 |
| 엔진 설치·버전·parser 준비 11명령 | 각 rc0. 역할 185에 합산하지 않음 |
| MON 2.16.19, 계획 45건 | 부분 실행 후 rc1. 14개 하위 명령 로그가 남았으나 개별 rc/RESULTS 미보존 |
| MON 2.21.3, 계획 45건 | 미시작 |
| NTP legacy 48 / flow 25 / serial 1 / transport 2 / wrapper 19 | 모두 미시작 |
| 185개 역할 사례의 인정 가능한 PASS | **0건 확정**, 나머지를 185 FAIL로 분류하지 않음 |
| 자기 회수 | create1/start1/rm1 각 rc0, force/stop/다른 CID 조작 없음 |
| Phase 1 인수 / 운영 Runtime / GitHub CI | 이번 결과로 완료 또는 PASS 선언하지 않음 |

14개 하위 로그는 syntax4, bash1, recap5, localhost preflight1, backup 관련3이다. 마지막3개는 임시 디렉터리 생성 실패를 직접 기록한다. Python 메모리의 사례 목록은 RESULTS.json에 쓰이기 전에 예외로 소실됐다. 원본 로그의 정상 문구나 코드 도달 사실을 개별 rc/PASS 집계로 소급 생성하지 않았다. 실행되지 않은 나머지6묶음의 합계는140건이고 첫45건은 부분 실행 상태다.

호스트의 `evidence=COMPLETE`는 호스트 명령/회수 영수증 저장에 대한 값이다. **MON 사례별 최종 결과가 완전하다는 뜻이 아니다.** `SESSION_FAILURE.json`은 있고 `SESSION_RESULT.json`과 7묶음 결과 파일은 모두 없다. 이 구분은 `EVIDENCE_AUDIT.json`에도 반영했다.

## 한 번에 처리할 수정 검토 범위

### R1 — fixture별 명시적인 임시 경로 (다음 후보 실행 차단)

- MON의 ansible.cfg와 NTP legacy/flow/serial/module transport의 각 ansible.cfg 생성부에서 `remote_tmp`를 해당 새 출력 디렉터리 아래 전용 경로로 명시하는 안을 권장한다. `/results`의 회차별·시험별 디렉터리 또는 검증된 `/scratch` 하위로 제한하고 기존 격리 통제와 185 사례/역할 의미를 유지한다.
- NTP 4종은 ANSIBLE_* 환경변수를 지운 후 자기 cfg를 생성한다. 따라서 컨테이너에 `ANSIBLE_REMOTE_TEMP` 하나만 추가하면 전체 해결이라는 주장은 성립하지 않는다. NTP의 같은 실패는 이번 회차에서 관측되지 않았고 **정적 영향 검토**다.
- `/root` 또는 rootfs를 쓰기 가능하게 바꾸거나 privileged/SELinux/namespace 통제를 완화하는 대안은 불필요하다.
- 수정 시 fixture source HEAD와 공급물 manifest/tar가 바뀐다. 현재 승인된 f019/cc361f나 이번 실패 증적을 새 후보의 승인·성공으로 사용하지 않는다.

### R2 — 실제 모듈 preflight와 실패 증적 보존 (다음 후보 실행 차단)

- 기존 preflight 사례 안에서 stat 등 실제 모듈을 실행한 후 결과를 assert하도록 보완한다. 새 업무/AC나 사례 수 추가는 필요 없다.
- 하위 명령의 argv·예상 rc·실제 rc를 각 명령 종료 직후 저장한다. 예상과 다른 rc면 `finish(error=...)`로 현재까지의 FAIL/미수행 상태를 남기고 중단한다. Timeout/실행 예외도 실패 기록으로 연결한다.
- 백업 생성 실패 뒤 파일을 읽는 2차 예외가 최초 오류를 가리지 않게 한다. 누락된 과거 RESULTS를 새로 만들지 않는다.
- 적용 가능한 최소 제안 diff를 `PROPOSED_FIX_NOT_APPLIED.patch`에 제공한다. **적용·구문검사·MOCK·CI·Linux 시험을 수행한 패치가 아니다.** 다음 변경 담당자가 fixture 격리경로와 오류 처리 차이만 검토하고 필요한 검증을 선정해야 한다.

수정 검증은 두 엔진의 실제 모듈 임시 경로, NTP 환경 정리 뒤 경로 보존, 예상치 않은 rc/timeout에서 최초 실패와 부분 결과 보존, 고정185 사례/격리 불변에 집중한다. 기존 성공한 별도 Linux21/27 MOCK/CI를 근거 없이 재실행할 필요는 없다. 전체185 실검증은 여전히 미충족이며 이번 창에서 재실행하지 않는다.

## 인계와 잔여

- 중앙: 이번 **실패+정확 자기 회수** 원본의 독립 검토 및 R1/R2 수정 담당/변경 범위 결정.
- 구현 담당: 수용된 범위로 새 source/후보를 작성·검증하고 버전을 다시 결속. 이번 원본/고정 후보는 보존.
- 이번 작업: 읽기 수집·원본 대조·원인/수정 범위 정리 완료. 서버 추가 명령 실행, 재회수, 파일 삭제, PR 게시, 새 작업창 확정은 하지 않음.
- 수집 준비 스크립트의 Windows 긴 경로 문제 1건은 로컬 경로 접두어만 보완했다. 서버 실행 실패와 무관하며 역할 시험 재실행이 아니다.

근거 파일: `EVIDENCE_AUDIT.json`, `HOST_COMMAND_AUDIT.json`, `EVIDENCE_COLLECTED-20261015T235358062170.json`, `observe-20261015T235348074330-{operator,svc}.stdout`, 수집본 `results/SESSION_FAILURE.json`, `results/ISOLATION.json`, `results/mon-2.16.19.stderr`, MON 3개 실패 로그, `TERMINAL.json`, `OWNED_IDENTITY.json`, host FINAL/RECOVERY_RESULT/0016-rm/0017-container 원본. 수집 파생물은 서버 원본과 별도 표기했다.
