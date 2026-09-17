# Ansible 리뷰 보완 점검 — 2026-09-17

판정: 기존 리뷰의 코드 지적은 현재 소스에 반영되어 있다. 미검토로 명시된 주요 경로를 추가 정적 검토하고 기존 로컬·모의 시험 **114/114 PASS**를 확인했다. 새 운영 코드 결함은 확인하지 못했다. PR18의 오래된 상태 문구를 정정하고 리뷰별 근거를 연결한다. 이 점검은 작성 측의 보완 점검이며 독립 승인, 전체 저장소 무결점 보증, 운영 적용 승인으로 해석하지 않는다.

## 확인한 리뷰와 소스

확인 시각과 원문은 `REVIEW_SNAPSHOT.json`에 보존한다. infra-ansible 열린 PR 6건과 관련 evidence PR13을 확인했다. infra-ansible PR20/21/22는 TEST ONLY / DO NOT MERGE다.

| PR | 점검 HEAD | 정식 리뷰 | 이번 대응 |
|---|---|---|---|
| infra-ansible #17 | `6b2ac7a80be1acd187ac73cbd1cf957f708edf85` | supreme33-kr COMMENTED, 해당 HEAD | 고정 runner labels 확인, verification-kit.py 의존 경로 보완 검토·15개 시험 |
| infra-ansible #18 | `d5147ebff0febbb8ab2afca28fe64d68301e033c` | supreme33-kr COMMENTED, 해당 HEAD | 공통 baseline guard와 실제 call site/회귀 코드 대조, 오래된 본문 정정 |
| infra-ansible #19 | `4da96621fd05a4943b76ca32b860a5779ec65e00` | supreme33-kr COMMENTED, 해당 HEAD | 토큰·launcher·proxy·input guard·결과/정리 경로 정적 검토와 99개 로컬·모의 시험 |
| infra-ansible #20 | `2750634766862d7fe19479acacc4259ee8315061` | 0건 | 기존 정상 시험 증적 연결 |
| infra-ansible #21 | `c50a6b3316fabba08d5211933e3733f8026e2d95` | 0건 | 기존 count 결함 시험 증적 연결 |
| infra-ansible #22 | `31895081e30e27481e7c17407047c9454e3b247a` | 0건 | 최신 export-fix 정상 시험 인수 기록 연결 |
| fds-project-evidence #13 | `159915926599c2a7bc283e8b111c18d6ab77102c` | hayeounglee COMMENTED, 과거 HEAD | stdout 질의의 기존 해소 근거 유지, 본 회차 증적 추가 |

조회한 PR들의 inline review comment는 0건이며 정식 REQUEST_CHANGES는 없다. COMMENTED는 승인으로 승격하지 않는다. 추가 증적 커밋이 생기면 evidence PR13 HEAD만 변경되며 위 값은 점검 입력 HEAD로 남는다.

## 기존 지적과 보완 점검

### PR17: runner labels와 검증 키트

[runner labels 의견](https://github.com/321Team/infra-ansible/pull/17#issuecomment-5693557465)은 과거 fromJSON 입력이 비었을 때의 파싱 문제다. 현재 템플릿은 `runs-on: [self-hosted, Linux, X64, fds-ci, ansible-isolated]`의 고정 labels와 정확한 변수 값 비교를 사용하며 fromJSON을 사용하지 않는다. 따라서 빈 배열 fallback을 새로 넣을 필요가 없다. 해당 템플릿의 일반 활성화 여부와 TEST ONLY workflow 실행을 구분한다.

[제한적 리뷰](https://github.com/321Team/infra-ansible/pull/17#pullrequestreview-5232880227)에서 미검토로 남긴 `tools/verification-kit.py`의 소스/commit 결합, archive 경로·형식·파일 집합 검증, wheel hash와 offline 설치, 실행 환경 정리, prepare/run 재검증을 읽었다. `tests/test_verification_kit.py` 15개를 현재 PR17 파일 바이트로 실행했다. 실제 새 wheel 설치나 두 엔진 전체 Actions를 이번 점검에서 수행한 것은 아니다.

### PR18: 공통 baseline guard와 문서 정정

[중복 검증 통합 의견](https://github.com/321Team/infra-ansible/pull/18#issuecomment-5693573027)은 현재 HEAD에 반영되어 있다. apply/rollback은 follow:false stat 결과를 공통 `roles/egress_proxy/tasks/validate-baseline.yml`에 전달한다. 공통 guard는 필드·타입·host·기존 config 메타데이터·firewall rule 이력 및 백업 regular/존재 조건을 확인한다. rollback은 검증 뒤, 변경 전에 marker를 무효화한다.

[현재 리뷰](https://github.com/321Team/infra-ansible/pull/18#pullrequestreview-5232889844)에서 제외했던 공통 guard와 `tests/run-egress-recovery.py`를 추가 대조했다. 실제 apply/rollback call site를 사용하는 regular/missing/symlink/directory/originally-absent/unexpected 백업 사례, orphan 보존, force:false, baseline 필드 오류, rule 이력, 중단 복원 모형을 확인했다.

PR 본문의 “정식 리뷰 0건”, “전체 Actions Run 0건”, “2.21.3 재검증 대기”는 오래된 상태다. [같은 PR18 HEAD의 서버 원본 검토](https://github.com/321Team/fds-project-evidence/blob/f3b5ea69f5119fc89e15f128c086f1c8eba97fea/evidence/infra-ansible-followup/cicd-runner01-podman-20260916T110635Z/README.md)에서 **2.16.19와 2.21.3 각각 45/45**를 이미 인수했다. 같은 소스의 동일 시험을 재실행하지 않고 원본을 재사용한다. 이것은 syntax/localhost CLI/task 및 중단 모형이며 Squid/firewalld/SSH 운영 검증은 아니다. 이전 환경 차단 원문은 과거 이력으로 보존한다.

### PR19: 리뷰에서 제외한 주요 경로

[현재 리뷰](https://github.com/321Team/infra-ansible/pull/19#pullrequestreview-5232900696)는 container.py 위주다. 이번에는 다음을 보완했다.

- 현재 Start payload가 사용하는 `tools/ansible-admin-token/admin-token.py`와 common.py: 고정 repo/API, 발급 전 계정 검사, raw 오류/credential 비노출, packet schema/만료/0600, 부분 쓰기·증적 실패 시 packet 제거. 예전 runner 디렉터리의 admin-token.py와 구분했다.
- `tools/ansible-runner-input/safe_input.py`: 고정 계정·basename, descriptor 기반 nofollow, owner/mode/hardlink/size/JSON 중복/schema 검사, 읽기 전후 inode와 metadata 대조.
- launcher/common/account 검사: root 호출자와 전용 비sudo 계정 분리, 고정 cwd와 정리된 환경, manifest 확인, root 소유 설치 사본, bounded original archive/digest 검사, 세션 종료와 CI 성공 판정의 분리.
- proxy: 고정 CONNECT allowlist와 443, 헤더/병렬 처리 제한, DNS 응답 전체의 공개 IP 검사, 검증한 IP에 직접 연결, private/혼합 응답 차단.
- runner/container: token stdin 전달, private native logs, 필요한 prepare 로그만 제한 수집, private IPC/격리 검사, 반환 결과 allowlist, 정확한 CID만 정리, 불확실한 정리 시 workspace 보존, PREPARED/image/bundle 결합.

99개 시험은 로컬 subprocess/파일 경계 및 mocked API·등록·IPC 정책 시험이다. 실제 GitHub 토큰 발급, Podman 실행, 실제 Runner 등록/해제는 이번 점검에서 하지 않았다. 기존 실제 Runtime 인수는 해당 원본 소스·bundle·image에만 귀속한다.

### Evidence PR13: stdout 질의

[기존 COMMENTED 리뷰](https://github.com/321Team/fds-project-evidence/pull/13#pullrequestreview-5219964286)의 stdout 5줄 질의는 이전 보완에서 시험 내부 CLI 호출의 2개 CI summary와 3개 guard summary로 대조됐다. 이번 작업은 이 기술적 해소를 독립 승인으로 바꾸거나 과거 실패 로그를 수정하지 않는다.

## 이번 로컬 시험

원문은 `validation/`에 stdout/stderr 별도로 보존했다. `VALIDATION.json`에 실제 명령, exit code, source Git blob/mode 재검증 결과를 남겼다. 각 시험은 `python3 -I -B <아래 파일>`로 실행했다.

| 입력 | 파일 | 결과 |
|---|---|---:|
| PR17 | tests/test_verification_kit.py | 15/15 |
| PR19 | tools/ansible-admin-token/test-admin-token.py | 22/22 |
| PR19 | tools/ansible-runner-input/test_safe_input.py | 20/20 |
| PR19 | tools/ansible-runner/test-kit.py | 37/37 |
| PR19 | tools/ansible-runner/test-registration.py | 13/13 |
| PR19 | tools/ansible-runner/test-ipc.py | 7/7 |
| 합계 | 6묶음, 모두 exit 0 | **114/114** |

기존 `test_timeout_has_nonzero_rc_and_diagnostics`에는 0.3초 안에 자식 Python 첫 로그가 도착한다고 가정하는 시험의 시간 의존성이 남아 있다. 이번 실행에서는 통과했다. 앞서 준비한 readiness 기반 보완안이나 이번 PASS를 근거로 기존 시험의 모든 환경에서의 안정성을 주장하지 않는다. 운영 timeout/logging 결함으로 판정할 근거도 아니다. 이번 변경은 증적·진행 기록 보완이며 배포 bundle/manifest/서버 명령은 변경하지 않았다.

## 기존 실제 인수 근거와 남은 판단

[최신 export-fix 정상 실행 최종 인수](https://github.com/321Team/fds-project-evidence/blob/159915926599c2a7bc283e8b111c18d6ab77102c/evidence/infra-ansible-followup/export-fix-receipt-35195838409-1/README.md): PR22 HEAD `31895081...`, Run `35195838409` attempt1, Job/Check `105118736321` success, unit58, artifact831개 hash 일치, Runtime/격리/로컬 정리와 Runner26 원격 부재 확인. 이번 114개와 같은 시험 집계로 합산하지 않는다.

- PR17/18/19와 evidence PR13의 독립 검토·승인 및 병합 판단은 여전히 남는다. 기존 리뷰의 제한 범위를 보완했지만 리뷰어의 상태를 대신 변경하지 않는다.
- PR18의 baseline schema/version/hash 결합, standalone verify 연결, 운영 서비스/config 복원 사후검사 등은 기존에 별도 범위로 남긴 hardening이다. 이번 focused fix가 그 전체를 완료한 것은 아니다. 실제 apply와 #74/#75 운영 인수는 HOLD다.
- 기존 count negative는 PR21의 `c50a6b...` 소스에 귀속한다. 최신 export-fix 정상 소스에서 동일 negative를 직접 실행한 것으로 승계하지 않는다. 이미 마련한 변경 영향 근거로 재시험 범위를 독립 검토한다.
- main/운영 apply/엔진 전환/일반 Workflow 활성화/병합은 이번 작업에 포함하지 않는다.

공개하는 파일은 점검 결과와 기존 공개 리뷰/시험 원문이다. 자격증명이나 token packet을 수집하지 않았다.
