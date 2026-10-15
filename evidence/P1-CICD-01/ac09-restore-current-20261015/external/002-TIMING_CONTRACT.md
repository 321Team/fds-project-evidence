# AC09 시각 증적 — 수용된 방식의 실행 절차

2026-10-15 · ROUND5. **방식 수용 완료 / 실제 회차 원본 미수집 / Runtime GO 없음.**

이하영의 [15:02:48 결정6185621755](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755)과 [SEC 적용 addendum](../../../reviews/phase1-sec-20261015/AC09_SEC_TIMING_ADDENDUM.md)을 적용한다. 정확 PATCH 송신 계측 코드 변경은 요구되지 않는다. 기존15/30/45분 조건과 별도 W+60 현행복구 후보의 구분은 유지한다. 과거 ROUND4의 답변 대기 표현은 당시 기록이다.

## 실제 사용하는 시계와 읽기 경로

| 호스트 | 기존 계정·주소 | 시간값의 출처 |
|---|---|---|
| cicd-runner01 | server01_cicd-runner / 10.250.10.20 | 원 claim/checkpoint `mtime_ns`, native 회차 기록 |
| k8s-control01 | server02 / 10.1.93.102 | 관리 GET 시작·완료 관측 시각 |
| k8s-worker01 | svc_ansible / 10.1.93.105 | 해당 노드 Pod의 kubelet `terminated.finishedAt` 등 |
| k8s-worker02 | svc_ansible / 10.1.93.107 | 동일 |
| k8s-worker03 | svc_ansible / 10.1.93.108 | 동일 |
| edge01 | svc_ansible / 10.1.93.50 | 기존 허용 경로 HTTP 관측의 시작·완료 시각 |

15:20:37 관리 GET에서 현행 두 UID·각Ready3·Pod6개가 worker01/02/03에 각각2개 배치된 것을 확인했다. [조회 원문](fresh-preparation/placement/stdout.json). control02/03의 API metadata 생성시각을 시한 계산에 사용하지 않으므로 전수 시계 시험을 추가하지 않는다. 실제 회차의 Pod UID→node와 관측 호스트를 다시 결속한다. 새 노드·관측 호스트가 생기면 그 시계 원문을 확보하거나 이미 결속한 관측 호스트의 보수적 완료상한을 사용한다. 없으면 해당 시각의 엄격 상한은 미입증이다.

Windows→기존 fds-ansible01→각 호스트 정상 SSH 경로. 계정·키·known_hosts는 기존 경로를 재사용한다. sudo/새 권한/파일 배치/chrony 설정·재시작·makestep 없이 Python stdin으로 읽는다. [clock_readonly.py](clock_readonly.py)는 호스트/계정 확인 뒤 `chronyc -n tracking`, `chronyc -n sources -v`, `systemctl show chronyd.service chrony.service`를 각각1회 수행한다. 각 명령 timeout5초, 원 stdout/stderr bytes·RC·명령·SHA와 boot_id·wall/monotonic_raw 시각을 로컬에 보존한다.

**15:16:59~15:17:01의 [준비 조회](clock-access-preparation/COLLECTION.json)는 PREPARATION이다.** 정상 경로6대·내부18명령 rc0, tracking Leap Normal을 확인했지만 실제 회차 전후 원본을 대신하지 않는다.

## 실제 회차에서 한 번씩 실행할 명령

실행 위치: Windows의 이 `round5` 폴더. 아래 Python은 기존 확인된 런타임이다. 중앙이 exact W/실제 회차 표지를 확정한 뒤 `$roundLabel`에 그 값을 넣는다. **현재는 실행하지 않는다.** 이 수집기는 승인·작업창을 부여하거나 예약하지 않는다.

```powershell
$clockPython = 'C:/Users/soldesk/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$roundLabel = 'UNSET_중앙이확정한실제회차표지'
& $clockPython -X utf8 -B collect_clocks.py --phase BEFORE_R1 --round-label $roundLabel --hosts runner control01 worker01 worker02 worker03 edge01 --out actual-before-r1
```

**R1 직전**, 실제 진입점검 직후에 수행한다. 출력 폴더 존재 또는 UNSET 표지이면 거부한다. 원문의 Run 번호가 아직 배정 전이면 실제 W/중앙 승인 원문을 먼저 결속하고, 배정 즉시 R1/R2 Run/Attempt1·plan·approvalSHA를 별도 회차 인덱스에 연결한다. 원본 파일 자체를 덮어쓰지 않는다.

실제 복귀·완료 또는 실패 종료를 인수한 **종료 직후**, 같은 호스트와 회차 표지로 별도 명령1회:

```powershell
& $clockPython -X utf8 -B collect_clocks.py --phase AFTER_FINISH --round-label $roundLabel --hosts runner control01 worker01 worker02 worker03 edge01 --out actual-after-finish
```

오류/미수집 원문도 보존한다. 자동 반복·다른 계정으로 우회하지 않는다. 현재 복원과 실제 통지 시한은 수집 성공을 기다리느라 지연하지 않는다. 새 호스트 필요 시 정상 경로와 실제 사용근거를 중앙에 연결한다.

## 원 journal의 metadata·원본 결속

[journal_original_read.py](journal_original_read.py)는 정해진 Runner claim root의 **두 고정 plan 중 하나**만 읽는다. 실제 Run/Attempt1·workflow SHA·approval SHA·claim SHA·연속 sequence/previous SHA·대상 UID를 대조한다. 파일은 기존 소유자0600·단일hardlink·NOFOLLOW·크기1MiB 이하, directory0700을 확인하고, 읽기 전/후 동일 inode/size/mtime_ns/ctime_ns를 검사한다. 최대64개. 원 bytes/base64/SHA와 **원 서버 metadata**를 함께 보존한다. 복사본mtime 사용 금지. claim/socket/lock에 쓰거나 연결하지 않는다. 전체 receipt/Run 승인 판정은 원 실행 증적과 별도로 결속하며 이 수집기가 승인 검증을 대행하지 않는다.

첫 PATCH_PENDING 뒤 시작하한을 확보할 때와 최종 writer 종료 후 완전한 chain을 인수할 때 구분된 로컬 출력폴더로 읽을 수 있다. writer 진행 중 파일목록이 바뀌거나 결속이 깨지면 이미 받은 원본을 보존하고 `NOT_VERIFIED`로 남긴다. 성공한 파일 조회도 writer 종료 자체를 증명하지 않는다. 최종 수집은 실제 writer 종료 확인 후 한다.

```powershell
$actualR1Run = 0
$actualR1ApprovalSha = 'UNSET_실제approval바이트SHA256'
$actualWorkflowSha = 'UNSET_실제Run의workflowSHA'
& $clockPython -X utf8 -B collect_journal.py --round R1 --run-id $actualR1Run --approval-sha256 $actualR1ApprovalSha --workflow-sha $actualWorkflowSha --out actual-r1-journal-final
```

R2는 `--round R2`와 그 실제 Run/approval SHA, 새 출력폴더 `actual-r2-journal-final`을 사용한다. 0/UNSET 값은 거부된다. 현재 실제 회차 journal을 읽지 않았고 합성 Run/승인을 생성하지 않았다.

## 오차 기록과 보수적 계산

[chrony 공식 문서](https://chrony-project.org/doc/4.8/chronyc.html)의 tracking 해석에 따라, 기준 시계가 정확하다는 전제하의 **해당 관측 시점** 오차 추정값은 다음을 사용한다.

`E_snapshot = abs(System time) + Root dispersion + 0.5 * abs(Root delay)` (초)

음수 delay가 있더라도 오차를 줄이지 않도록 절대값을 취한다. 필드·단위·유한 숫자·동기 상태·reference/stratum을 원문과 연결한다. [준비 시점 계산표](CLOCK_ACCESS_SUMMARY.json)는 접근 확인용이며 실제 회차의 E가 아니다.

두 시점 rc0 또는 E 두 값의 max만으로 **회차 전체** 오차 상한/연속성을 자동 입증하지 않는다. 전후 boot_id·chronyd 상태/PID·wall/monotonic 경과·reference 변화, 필요 시 기존 접근 가능한 시계 로그와 해당 timestamp 생산 호스트를 대조한다. 실제 구간에 적용할 `E_host`와 근거·적용 구간·미확인을 회차 계산표에 기록한다. 근거가 부족하면 E=0/고정 유리한 값/새 임계값으로 채우지 않고 **UNPROVEN**으로 둔다. 이 검토를 새 Runtime 인수기준이나 전노드 시험으로 확대하지 않는다.

| 값 | 계산·기록 |
|---|---|
| 정확 송신값 | P_exact, R2firstPATCH_exact = NOT_MEASURED |
| R1 시작 하한 L | 첫 R1 PATCH_PENDING 원mtime − 해당 Runner 시계 오차 E |
| R1 송신 상한 | 첫 R1 APPLIED 원mtime + 해당 Runner E; 값 없으면 미확보 |
| R2 첫 PATCH 상한 U2 | 첫 R2 APPLIED 원mtime + 해당 Runner E |
| 마지막 이전 Pod 종료 | 실제 terminated.finishedAt 및 kubelet host·오차, 없으면 마지막 존재~첫 전체 부재 관측 구간 |
| 회수 상한 Udone | 이전 Pod 전체 부재·현행 각Ready3·직접 업무404·전용metrics200/target6 완료 관측마다 생산 host의 E를 더한 뒤 가장 늦은 값 |
| 15/30분 입증 | U2−L≤900초, Udone−L≤1800초. 필요한 오차·원본·결속이 모두 확보된 범위에 한함 |

최종 기록은 `TIMING_METHOD=ACCEPTED_6185621755`, `ORIGINAL_COMPLETENESS`, `TIMING_PROOF=PROVEN/시한 미입증`, `ACTUAL_OVERRUN/EXPIRY`를 분리한다. 원본/오차·결속 부족은 **시한 미입증 / SEC 사후 검토**이며 자동 사고도 PASS도 아니다.

**실제 벽시계 기준 P+30 미회수 즉시 SEC 통지·현행복원 우선, W+45 이후 잔여노출은 사고 기록/SEC 재판단**은 그대로다. 운영 중 보수적인 시작하한을 쓸 수 있으면 더 이른 대응에 사용한다. 유효 하한도 불명확하면 숫자를 만들어 대기하지 않고 현재 노출·시간 근거 부족을 중앙에 바로 인계한다. 정확 W의 만료는 구간 증적 연구나 수집 실패로 미뤄지지 않는다.
