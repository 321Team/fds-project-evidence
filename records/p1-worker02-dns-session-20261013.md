# Phase 1 worker02 DNS 단일 회차 실제 결과 — 2026-10-13

이권욱 / CODEX_ASSISTED. **worker02 한 대에서 새 백업 → check → 실제 적용 → 재적용 → 복구 check → 동일 원본값 복구 → 사후 확인을 완료했다.** 실제 구간 02:53:41–02:57:01 KST(약 199.7초). 현재 DNS가 이미 목표와 같아 적용·재적용은 관리 변경0이며, 복구는 동일 값의 `nmcli connection modify` + `device reapply` 두 태스크를 실제 실행했다. **실패 상태를 만든 복원 시험·전체 Ansible 운영 전환·AC 인수 완료는 아니다.**

## 실행 근거와 범위

[PR76](https://github.com/321Team/infra-ansible/pull/76)의 승인 HEAD `0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea`, 이하영/hayeounglee 독립 코드 승인·병합 및 [regression CI SUCCESS](https://github.com/321Team/infra-ansible/actions/runs/37895578228/job/113706062449)를 재사용했다. 기존 NM 동일값 reapply의 비차단 의견을 별도 차단/반복 리뷰로 바꾸지 않았다. 서버의 고정11파일 SHA·clean source·실행 경로 untracked0과 CLI4종2.21.3을 전후 대조했다. 현 main으로 소스를 바꾸거나 전역 RPM/PATH/엔진을 전환하지 않았다.

사용자는 실행안의 **“가능 — 해당 단일 회차 진행”**으로 worker02 NM/DNS 동시 변경 배제·콘솔 인수를 확인했다. [확인 기록](../evidence/P1-ANS-01/worker02-dns-session-20261013T025341/runtime/USER_AUTHORIZATION.json)은 [범위안](../evidence/P1-ANS-01/worker02-dns-session-20261013T025341/preparation/EXECUTION_SCOPE.md)과 입력 SHA에 결속했다. Harbor idle 및 사후 종료 상태를 확인하고 시작/종료를 전달해 구간을 분리했다. 앞선 이미지 작업 승인을 DNS 변경에 전용하지 않았다.

- 회차: `w02-20261013T024523-85942d67`
- controller: ansible01/server01_ansible, source `/home/server01_ansible/worker02-session-plan-3hetha3t/source`
- 후보 engine: `/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin` (2.21.3, 회차 명시 선택)
- 대상: worker02 `10.1.93.107` / svc_ansible+sudo, `ens160` / `fds-k8s-worker02`
- 원본=목표 DNS: `10.1.93.52,10.1.93.53`; search `fds.internal`; ignore-auto-dns `yes`. 고의 drift 없음.

## 각 단계의 실제 결과

| 단계 | 시작–완료 KST | worker02 ok | changed | failed/unreachable/rescued |
|---|---|---:|---:|---|
| prepare | 02:53:41–02:53:53 | 34 | 1 | 0/0/0 |
| apply-check | 02:54:29–02:54:40 | 35 | 0 | 0/0/0 |
| apply | 02:54:56–02:55:08 | 38 | 0 | 0/0/0 |
| reapply | 02:55:22–02:55:34 | 38 | 0 | 0/0/0 |
| rollback-check | 02:56:00–02:56:05 | 13 | 0 | 0/0/0 |
| rollback | 02:56:12–02:56:20 | 22 | 2 | 0/0/0 |

localhost는 매 단계 guard1개/changed0이며 다른 managed-host는 실행하지 않았다. prepare의changed1은 새 백업 생성이며 DNS 변경이 아니다. 최초 apply는 백업 생성 후 67.8초에 시작해15분 제한 안이었다. 두 check 단계는 실제 적용/복구 완료의 증거로 합산하지 않는다. 실제 apply/reapply에서는 관리 변경0·사후 검증 정상, rollback에서는 원본 해시 바인딩을 통과한 뒤 동일값 재설정·재적용2태스크와 조회를 실행했다. 전체 ignored0, timeout/자동 재시도/자동rescue 발생0이다.

실행 원문은 [runtime의20개 영수증](../evidence/P1-ANS-01/worker02-dns-session-20261013T025341/runtime/)과 controller에서 실제 수신한 [33개 파일](../evidence/P1-ANS-01/worker02-dns-session-20261013T025341/runtime/controller-files/)에 있다. [VERIFICATION.json](../evidence/P1-ANS-01/worker02-dns-session-20261013T025341/runtime/VERIFICATION.json)은 명령·시각·rc·원 출력·SHA·recap/백업/사후 관계를 연결한다. 시각은 각 호스트 원시 UTC를 KST로 변환했으며 PC 수신 시각은 별도 receipt로 보존했다. 시계의 동기 정확도나 신뢰된 타임스탬프를 새로 검증했다는 주장은 하지 않는다.

## 사후 상태·보존 자료

- apply/reapply/rollback 각각 뒤 **새 SSH 연결3회**: ControlMaster=no/ControlPath=none, strict host-key/기존 키/sudo 경로. persistent/live DNS와 내부 FQDN·short-name→`.109`, DNS2대 직접 질의, 외부 이름 해석 및 `.109:6443` TCP 확인 성공.
- 주소·route·NM connection UUID와 비DNS 필드, NetworkManager/kubelet/containerd PID·active 진입 시각 전후 동일. SELinux Enforcing 유지. 이 선택 필드 대조를 전체 호스트 형상 전수 검증으로 확대하지 않는다.
- **02:56:29 KST** Node6/6·시스템Pod3/3·앱Pod6/6 Ready, 기존9Pod UID·배치/restart 및4Deployment UID/spec 유지. 앱별 worker01/02/03 각1개 유지. 이번 HTTP/MON 재측정은 없으며 앞선 회차 결과를 현재 관측으로 옮기지 않는다.
- 백업: `/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions/w02-20261013T024523-85942d67/original-resolver.json`, SHA-256 `ce6295bcc88b8129003f50cb4cbd4be36d18c32413bbcf46e9926a552a1ea5b2`. 실제 읽기 원문/해시 및 최종 재조회 동일. root0:0/0600, parent0700, SELinux `unconfined_u:object_r:var_lib_t:s0`. 최초 CR 원본과 다른 회차는 변경하지 않았다.
- controller 원 로그/영수증33파일: `/home/server01_ansible/p1-worker02-dns-20261013-r1`, server01_ansible 소유, directory0700/file0600. 원 bytes로 내려받아 각 해시를 대조했다. 백업·회차 원문은 보존하며 인증정보 내용은 수집하지 않았다.

## 판정 경계와 다음 순서

**RUNTIME: 이번 단일 회차 성공.** 준비4개 읽기·source11파일·기존 CI/독립 코드 승인을 재사용하고, 실제20개 receipt·controller33파일을 새로 검증했다. STATIC/MOCK/기존 CI를 실제 실행으로 대체하지 않았다. 승인된 source의 wrapper/role이 실제 대상에서 실행됐지만 이번 전달·기록용 helper 자체는 별도 독립 코드 리뷰를 받지 않았다. 증적 편입은 기존 PR208 리뷰어 hayeounglee·supreme33-kr가 검토하며 새 중복 요청을 만들지 않는다. 증적 CI/REVIEW/MERGE는 편입 HEAD의 실제 상태를 따른다.

현재=원본=목표에서 동일값 복구 경로를 실행했으므로 서로 다른 상태의 복원, 적용 실패/자동rescue, SSH 단절·콘솔 복구·재부팅 지속성은 이번에 실증하지 않았다. 기존 code MOCK의 해당 실패 경로 결과는 별도 근거다. 엔진 전체 role 호환/운영 호출 경로·전역 전환·독립 최종 인수·AC 종결은 남아 있다.

다음은 기존 인계 범위의 **Delivery/Runner 실제 입력·운영 호출 경로·복귀 조건 정리 → 필요한 한정 회차 → 기존 HA/Final E2E 및 최종 인수**다. 후보 앱 배포·전역 엔진 전환을 이번 DNS 허용으로 시작하지 않는다. 불필요한 동일 DNS 재실행이나 장애 유발·Phase2 작업은 추가하지 않는다.

읽기 전용 재검증: `python3 runtime/verify_results.py <수집회차>/runtime`. collector/session_step는 당시 실행 기록이며 재실행 안내가 아니다. [OID02 결과](p1-oid02-preload-20261013.md)의 당시 DNS 미실행 상태는 이 후속 기록으로 연결하고 원 기록을 보존한다.
