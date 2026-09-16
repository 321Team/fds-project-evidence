# Ansible 후속 코드·Linux 검증 — 2026-09-16

사용자 “착수”에 따른 Codex Linux 실행 기록. 실습망 서버·GitHub Actions 실행이 아니다.

- CI 코드: [infra-ansible PR #17](https://github.com/321Team/infra-ansible/pull/17), `a487c4fc5185bf0b9cd82f7f739651d4d580ba6b`.
- Egress 수정: [infra-ansible PR #18](https://github.com/321Team/infra-ansible/pull/18), `ca3a5b1c47364e5f929a13d253b956b5ed313e33`.
- main 기반: `57e7cc740e7a406387848c52f4aa56b98c516168`. 코드 수정·증적 편입 모두 독립 리뷰/병합 대기.

| 범위 | 실제 결과 | 한계 |
|---|---|---|
| PR17 구문 | 2엔진 × 16 playbook = 32 PASS | 구문만 확인 |
| PR17 단위 | 56 PASS | Linux에서 실제 실행 |
| SSH guard | 2.16.19 baseline + 6 mutations 기대결과 일치 | 2.21.3는 local RPC 시작 실패; 전체 MATRIX FAIL |
| Callback 보충 실행 | 2.16.19 29/29 기대결과 일치 | CLI 16 + 파생 13, 6개 localhost 별칭; 전체 MATRIX FAIL |
| DNS 보충 실행 | 2.16.19 localhost exit0 | 2.21.3 behavioral 미완료 |
| PR18 | 2.16.19 33/33 기대결과 일치 | 구문·CLI·assert/copy/file·중단모형; 실제 Squid/firewalld 미실행 |
| PR18 / 2.21.3 | 구문·대상 10개 기대결과 일치, localhost preflight FAIL | 후속 behavioral cases NOT RUN |

`ci-artifact/CI_RESULT.json`의 원본 FAIL을 그대로 보존한다. Python 3.12.14와 고정 wheel 12개 검증·새 venv 설치는 성공했다. Ansible 2.21.3가 localhost 작업을 시작할 때 Local RPC가 시작되지 않았고, Python 표준 multiprocessing Server 생성도 `PermissionError(errno=1)`로 실패했다. 이 환경 제한을 프로젝트 코드 결함이나 PASS로 바꾸지 않았다. 원본 로그·설치/구문·fixture 결과는 하위 경로에 있다.

`SHA256SUMS`는 이번 편입본 전체 바이트를 검증한다. 기존 내부 manifest는 원 실행의 경로를 유지한다. CI artifact에는 실행기가 정한 범위만 포함되며 원래부터 module cache 등이 제외됐다(`ARTIFACT_SCOPE.json`). callback 보충본도 임시 module cache는 제외한다. wheel/venv/배포 archive/운영 자격증명은 편입하지 않는다.

## 다음 검증

1. 독립 리뷰에서 PR18의 복원 guard, marker 순서, inventory 대상, rule 보존 및 기대결과를 확인한다. 다른 hardening 잔여는 PR18 본문을 따른다.
2. 로컬 IPC를 지원하고 운영 키/배포 권한이 없는 승인된 격리 Linux에서 두 엔진 전체 시험을 재실행한다. 보안 제한 우회나 시스템 Ansible 교체를 요구하지 않는다.
3. Runner 저장소 접근·labels/group·계정·정리 책임을 확인하고 PR17 활성화 변경을 독립 리뷰한다. 정상/고의 결함 실제 Actions Run·SHA·artifact는 아직 없다.
4. main 변경이 추가 병합되면 PR17에 반영한 새 SHA로 다시 검증한다. Squid 실측·apply/rollback 인수·#75 적용·#9 운영 엔진 전환은 별도다.

정상·의도한 거절·중단 모형을 포함한 기대결과 수를 통합 Runtime PASS 수로 해석하지 않는다. 기존 완료 티켓과 승인 기록은 변경하지 않는다.
