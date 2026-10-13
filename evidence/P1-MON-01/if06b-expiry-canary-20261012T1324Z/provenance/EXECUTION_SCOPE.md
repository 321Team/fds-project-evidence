# Phase 1 MON IF06B 실제 적용 범위

CODEX_ASSISTED · 2026-10-12 KST · 실행 범위를 한 번에 확정하기 위한 준비본. 새 코드 리뷰·Lead GO를 요구하는 문서가 아니다.

읽기 수집과 사용자 확인을 마쳤다. 이번 작업으로 control01의 실행기 공급·RBAC·token·canary를 적용한 것은 아니다. 확정된 사용자 의사(권장안 진행, 콘솔 인수 가능, 두 호스트 직접 인증)는 유지한다. 프로젝트 지침 6의 실제 서버 Runtime 적용 구분에 따라 아래 실제 변경 범위를 한 묶음으로 명시한다.

## 대상과 변경

| 항목 | 구체 범위 |
|---|---|
| 코드 | PR85 merge `92c182fc58de999536e56d90012bb2686d9f07cf`; 실행안 r3의 명령·실패 분기 재사용 |
| 공급 | 기존 ansible01 → svc_ansible → control01 `.102` 경로. `supply-92c182f.tar` + `if06b-aux-r1.tar` + 이 폴더의 `input.session.candidate.json`을 전달 후 `input.json`으로 배치. SHA256은 입력표·READINESS_STATUS.json 참조 |
| 새 경로 | `/home/svc_ansible/if06b-in-20261012T2110-mon01`, `/var/lib/fds-change/if06b-20261012T2110-mon01`, `/var/lib/fds-change/if06b-survival-20261012T2110-mon01`, `/run/fds-if06b-20261012T2110-mon01`. 기존 경로 재사용·덮어쓰기 없이 생성 성공 확인 |
| 임시 권한 | `monitoring-api/p1-mon-if06b-guardian` ServiceAccount, 동명 ClusterRole·ClusterRoleBinding 각1개. 검토된 rbac YAML 3개 그대로. 한 개씩 생성 응답 UID 확인 후 다음으로 진행 |
| token | root 전용 파일 `/run/fds-if06b-20261012T2110-mon01/token`. 요청 TTL 900초, 실제 허용 상한900초. 실행 직전 남은 시간 ≥210초(lease90+cleanup60+여유60). token 내용 출력·공유·관리 키 사본 생성 없음 |
| 실제 시험 | worker03 host-origin `.108 → .30 TCP 443/8443`을 허용하는 기존 canary GNP `p1-mon-if06b-worker03-to-monitor01-canary` 1회. 443 양성 대조1회 → gate 재확인 후8443 1회 → 회수 뒤 post-deny1회. 실패 시 후속 요청 중단 |
| 고정 예산 | lease90 / cleanup60 / API request10 / max-age10 / readback2초. 캡처300초, 배경20 / 요청합계20 / 후관측20초. watch poll2/window200. survival300/5. 회차 중 연장·동일 회차 재실행 없음 |
| 관측 | worker03 ens160, gateway ens160·ens224, monitor01 ens160. 네 지점 별도 결과. 요청 출발 포트45143/45843은 직전 미사용 확인. 기존 승인 CA 사용 |
| 역할 | Codex가 기존 경로의 명령·증적 처리 지원, 이권욱이 두 외부 호스트 직접 인증 및 control01 콘솔 수동 인수 대기. 장애 시 통보는 이 대화와 실행 터미널. 타 담당자에게 새 책임 부과 없음 |

남는 권한: 이 token의 **GNP create 권한은 이름으로 제한할 수 없으므로 유효 기간에 다른 GNP도 생성할 수 있다.** get/delete는 canary 이름, namespace get은 kube-system으로 제한한다. 고정 manifest, 짧은 실제 수명, root 전용 파일, 생성 영수증·정리가 통제 수단이다.

## 실행 순서와 중단·복구

1. 새 공급 경로 생성·해시·소유/모드 대조. RBAC dry-run·부재 확인 → 한 개씩 생성 영수증 확인 → 허용/금지 권한 검사 → token 발급·실제 수명 판정. 어느 단계든 실패하면 다음 변경0, 소유가 확인된 객체만 기존 실행안대로 정리한다.
2. `validate` → 별도 MON 세션의 `survival-check` → `preflight`. 기존 검증을 로컬 결과로 대체하지 않는다. 생존 시험은 그 시험 세션만 닫으며 Harbor 세션이나 계정 전체를 종료하지 않는다.
3. **Harbor 변경·사후 확인과 다음 예정 변경이 겹치지 않는 구간을 확인**한다. 21:15 기록상 Harbor는 실패 원인 분석·사후 확인 중이므로 현재 시험은 시작할 수 없다. T19 기존 보호 복원 근거, fresh MON 기준선, HEP/GNP·gateway·monitor 상태를 대조한다. 부족하면 token을 미리 발급해 대기하지 않는다.
4. 네 캡처 준비·공통 관측 여유 → `run` → ARMED 즉시 watch → CREATE OWNED UID/RV 및 gate 통과 이후에만 요청. 8443 직전 다시 판정. 요청 중 MON 악화/abort/시간 부족이면 후속 요청0·감독의 조기 회수 경로로 간다.
5. 회수 NotFound·post-deny·정책 전후 대조·원본 결과를 보존한다. 감독이 살아 있거나 락이 보유돼 있으면 수동 삭제하지 않는다. 감독 소실/해제 또는 검토된 재부팅 분기가 성립할 때만 이권욱이 기존 관리 인증으로 현재 UID/RV/spec을 대조하고 조건부 회수한다.
6. canary 부재·감독 종결 후 생성 영수증 UID로 임시 Binding → Role → SA를 정리하고 token 파일을 처리한다. 불확실 객체/기록 실패는 추정 삭제·재시도하지 않고 인수 상태로 보존한다.

캡처300초는 지점별 시작부터이며 시작 시차·저장 지연까지 무조건 보장하는 숫자가 아니다. 공통 유효 구간이 부족하면 시작하지 않고, 벗어난 관측은 NOT_VERIFIED로 남긴다. lease+cleanup150초 역시 모든 수동 인수까지 끝난다는 보장이 아니다.

완료 판정은 실제 생성·회수·정리·증적 확인 후 별도다. 이번 범위에 Phase 2, 영구 정책·방화벽 변경, 서비스 재기동, Harbor 변경, 티켓 AC 종결은 없다.

## 현재 근거

- `SESSION_INPUT_SHEET_FILLED.md`: 원본 r5에 실측과 선택안을 연결한 사본. 원본 실행안·두 tar 불변.
- `READINESS_STATUS.json`: 원본·산출물 해시와 수행/미수행 구분.
- `verified-host-inputs.json`, `gateway-receipt/`, `monitor-receipt/`: gateway22·monitor11개 읽기와 원본67/34개 해시 검증.
- control01 기준선23/23·실패증가0, monitor heartbeat12.6초·활성 alert0은 준비 시점 결과이며 회차 직전값으로 재사용하지 않는다.
