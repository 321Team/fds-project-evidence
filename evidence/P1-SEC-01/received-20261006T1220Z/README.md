# P1-SEC-01 — AC-01 PSA version label 정합화 변경 원본: monitoring-api·monitoring-node·kube-system (2026-10-06)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). Review Owner [변경 GO 6014740196](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6014740196)(조건 C1~C3)에 따라 누락돼 있던 PSA **version label**만 추가한 변경의 실행 원본이다. level(enforce/audit/warn)은 바꾸지 않았다. 이 폴더는 관측 원본이며 **AC-01 MET 판정이 아니다.**

## 출처와 수신

| 항목 | 값 |
|---|---|
| 실행 | `k8s-control01`, 계정 `server02`(sudo), 2026-10-06 21:0x~21:12:33 KST(종료 `05-end-time.txt` `2026-10-06T21:12:33+0900`). 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 명령 안내·수신 검증·편입 정리는 Claude Code 보조 |
| 승인 | 변경 GO [6014740196](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6014740196), 시작 Gate [6015798547](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6015798547), 종료·결과 기록 [6015973377](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6015973377) |
| 전달 경로 | control01 `~/psa-label-20261006.tar.gz` → ansible01(`scp`) → 사용자가 zip으로 공유 폴더에 올려 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-06 21:2x KST |

| 아카이브 | SHA-256 |
|---|---|
| `psa-label-20261006.tar.gz` (28개 파일) | `aba01e3275a505b140aba648a22584eab5cd32caa93994cdb6bb39c9135c3514` |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar(`.sha256`) = control01 콘솔 출력 = ansible01 재계산 = 수신 후 재계산(일치). 비밀정보 패턴 검색 일치 0건.
- 이 도구는 **스크립트가 없다.** 실행한 `kubectl` 명령은 [변경 GO 6014740196](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6014740196)과 결과 기록 6015973377의 절차대로 콘솔에서 직접 입력했으며, 아카이브에는 각 명령의 출력과 시험 Pod 정의만 있다. 명령 자체의 입력 원문(셸 history)은 아카이브에 없다.
- 아카이브에는 `kubectl` 기본 출력이라 `managedFields`가 없어 적용 명령의 실행 시각을 파일만으로는 확인할 수 없다. 대신 적용 후 세 Namespace의 `resourceVersion`이 `4189924`(monitoring-api) → `4189925`(monitoring-node) → `4189926`(kube-system)으로 **연속**이며 이는 적용 순서와 같다.

## 관측값 (원본 보존 — 판정 아님)

| 단계 | 파일 | 관측 |
|---|---|---|
| 서버 버전 | `00-version.txt` | Client·Server `v1.36.4`, rc=0 (C2-a 조건 충족) |
| 사전 상태 | `01-pre-state.txt`, `pre-*.yaml` | 세 Namespace 모두 version label 3개 부재. level: kube-system `enforce=privileged, audit/warn=restricted`, monitoring-api `restricted ×3`, monitoring-node `enforce=privileged, audit/warn=restricted`. UID: kube-system `e1669cff…`(10/2 [evidence#99](https://github.com/321Team/fds-project-evidence/pull/99) 원본과 같고 rv `2079679`도 같음), monitoring-api `f7e863e5…`(rv `1115753`), monitoring-node `2a0dae5d…`(rv `1115754`) |
| 서버 dry-run(권고) | `03-dryrun-monitoring-api.txt` | `namespace/monitoring-api labeled (server dry run)` — 경고 없음 |
| 적용(C1) | `04-apply-*.txt` | Namespace마다 **한 명령**, `--overwrite` 없음, `--resource-version`은 사전 rv. monitoring-api·monitoring-node·kube-system 순으로 3건 모두 `labeled`, 오류 없음 |
| label 전후 | `02-label-diff.txt`, `pre-*.yaml`, `post-*.yaml` | 세 Namespace 모두 `audit-version`·`enforce-version`·`warn-version: v1.36` **3줄만 추가**. `enforce`·`audit`·`warn` level 값은 diff에 없음(불변) |
| monitoring-api 준수 Pod | `t1-compliant.*`, `psa-compliant.yaml` | server dry-run **허용** — `pod/psa-compliant created (server dry run)`, rc=0 |
| monitoring-api 위반 Pod | `t2-privileged.*`, `psa-privileged.yaml` | server dry-run **거부** — `violates PodSecurity "restricted:v1.36"`(privileged, allowPrivilegeEscalation), rc=1 |
| 종료 | `05-end-time.txt` | `END 2026-10-06T21:12:33+0900` (창 21:00~21:30 안, 롤백 없음) |

## 한계와 주의 (은닉 아님)

1. **시험 Pod 정의는 이번에 새로 만든 최소 정의다.** 09-26 [evidence#49](https://github.com/321Team/fds-project-evidence/pull/49)의 `psa-compliant`/`psa-privileged`와 **이름·container 이름(`c`)이 같을 뿐 같은 정의인지는 확인하지 못했다.** #49의 시험 스크립트(`01-psa-violation.sh`)는 서버에만 있고 이번에 열거나 실행하지 않았다. Pod는 `--dry-run=server`로만 제출되었고 **실제로 생성되지 않았다.**
2. **거부 사유가 두 가지다.** 위반 Pod는 `privileged`와 `allowPrivilegeEscalation`을 함께 위반한다(정의를 만들 때 `allowPrivilegeEscalation: false`를 `privileged: true`로 치환해 후자가 빠짐). 시험 목적(restricted 위반 거부)에는 영향이 없다.
3. `monitoring-node`·`kube-system`은 enforce가 privileged라 restricted 위반 거부 시험을 하지 않았다. `fds-app`·`ci-cd`·level·전역 admission config·옛 ClusterRole·문서 주석은 변경하지 않았다.
4. `monitoring-api`·`monitoring-node`에는 `kubectl.kubernetes.io/last-applied-configuration` 주석이 있고 이 주석의 label 목록에는 version label이 없다. 향후 manifest를 `kubectl apply`할 때 선언된 version 값과 이 변경이 충돌하는지는 이번 범위에서 확인하지 않았다(저장소 `01-namespace.yaml`은 `v1.36`을 선언).
5. 한 시점(2026-10-06 21:1x KST) 결과이다. PSA는 admission 시점에만 적용되어 실행 중인 Pod를 퇴거하지 않는 것이 **설계**이나, 이번에 변경 전후 Pod 상태(재시작 횟수·Ready)를 수집하지 않아 **"Pod 영향 없음"은 관측으로 확인한 사실이 아니다.** 같은 시간대의 MON 23/23 등 별도 기록(#17)을 참고할 수 있다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-01 PSA version label (B19-PSA-01) | `02-label-diff.txt`, `pre-*.yaml`, `post-*.yaml`, `04-apply-*.txt` |
| AC-01 위반 Pod 차단 유지(monitoring-api) | `t1-compliant.*`, `t2-privileged.*` |
| 핵심 요구 1 (kube-system PSA) | `pre-kube-system.yaml`, `post-kube-system.yaml` |
