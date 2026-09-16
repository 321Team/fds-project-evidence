# Ansible 리뷰 반영 및 착수 조건 재점검 — 2026-09-16

사용자 “차단사항 없으면 착수”에 따라 최신 리뷰·실행 조건을 대조하고, 기존 코드 보완 범위 안에서 리뷰 의견 2건을 반영했다. 병합·Workflow 활성화·운영 적용은 수행하지 않았다.

| 대상 | 이번 검토 HEAD | 변경 / 검증 |
|---|---|---|
| [infra-ansible PR17](https://github.com/321Team/infra-ansible/pull/17) | `169571801d1b0cee0ba75137380149a48d6b56dd` | 빈 Runner labels의 Job 조건·JSON fallback 보완; 단위 56/56 PASS, YAML/문자열 조건·JSON 로컬 모형 7/7 기대 일치 |
| [infra-ansible PR18](https://github.com/321Team/infra-ansible/pull/18) | `d5147ebff0febbb8ab2afca28fe64d68301e033c` | 원본 백업 검증 공통화; 2.16.19 45/45 기대 일치, 2.21.3 10개 통과 뒤 localhost preflight FAIL |

## 리뷰 대응

- [PR17 의견](https://github.com/321Team/infra-ansible/pull/17#issuecomment-5693557465): labels가 빈 문자열이면 Job 조건이 false가 되도록 추가했고, fromJSON 입력은 비어 있지 않은 sentinel 배열로 폴백한다. 실제 Runner에 `ansible-ci-unconfigured` label을 부여하지 않는다. 제안된 빈 배열을 안전한 Runner 선택으로 가정하지 않았다. 비어 있지 않은 잘못된 JSON은 자동 수정하지 않는다. 비활성·동일 저장소·fork·수동·빈 값·정상/비정상 JSON의 로컬 모형 결과이며, GitHub 평가 순서나 실제 skip/dispatch를 검증한 것은 아니다. Runner labels 배열은 모든 label과 일치하는 Runner를 선택한다([GitHub 구문](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idruns-on)). 논리 연산과 fromJSON은 [공식 표현식 문서](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions)를 참고했다.
- [PR18 의견](https://github.com/321Team/infra-ansible/pull/18#issuecomment-5693573027): apply/rollback의 중복 assert를 `validate-baseline.yml`로 옮기고 양쪽에서 `follow:false` stat 결과를 명시적으로 전달한다. rollback은 stat → 공통 검증 → 첫 marker 변경 순서다. 기존 33개에 각 call site의 실제 regular/missing/symlink/directory/originally-absent/unexpected 파일 검사 6개씩을 추가했다. 원본 include의 변수·조건을 유지해 연결 누락도 실패한다.

## 검증 범위

- `ci/`: 단위시험 원문/exit0, Workflow 로컬 모형 코드·결과. 새 HEAD에서 전체 CI matrix를 재실행하지 않았다. 기존 32 syntax·56 unit·부분 2.16.19 결과는 [이전 실행](../local-20260916/README.md)의 `a487c4f`에 귀속된다.
- `egress-2.16.19/`: 새 HEAD clean checkout의 구문·CLI·assert/stat/copy/file·marker 중단 모형. 허용·의도한 거절·모형을 포함한 45개 기대결과이며 Squid/firewalld/SSH Runtime PASS 수가 아니다.
- `egress-2.21.3/`: 새 HEAD clean checkout. 구문4/bash1/recap5 이후 양성 localhost preflight가 rc250으로 실패하여 후속 behavioral은 NOT RUN. 원본 `RESULTS.json`은 FAIL로 보존한다.
- `environment/local-ipc.json`: 표준 Python multiprocessing Server의 새 로컬 소켓 생성도 PermissionError(errno=1). 이전 라운드와 같은 환경 제약이며 런타임 우회·시스템 엔진 교체를 하지 않았다.
- 모든 편입 파일은 UTF-8이며 wheel/venv/cache/운영 키는 포함하지 않는다. 하위 manifest는 원본, 이번 회차 `SHA256SUMS`와 저장소 `REGISTRY_SHA256SUMS`는 편입 바이트 검사용이다. 해시 일치는 시험 성공·독립 승인이 아니다.

## 착수 판정

리뷰 코드 보완·격리 로컬 시험은 진행 가능하여 완료했다. 세 PR 모두 Draft이며 현재 댓글은 정식 APPROVED 리뷰가 아니다. 다음 조건은 남아 있다.

1. 로컬 IPC를 지원하는 승인된 격리 Linux에서 두 엔진 전체 검증.
2. Ansible 저장소 Runner 접근·labels/group·작업 계정·운영 자격증명 격리·종료 후 정리 확인, Workflow 활성화 변경의 독립 리뷰 및 실제 정상/고의 결함 Actions Run. 저장소 Actions는 재조회 시 0건.
3. 최신 코드·증적 HEAD의 독립 승인. main 추가 병합 시 통합한 새 SHA로 필요한 재검증.
4. Squid 실제 적용은 Alertmanager client source 실측, PR18에 명시한 잔여 hardening의 처리 판단 및 apply/allow-deny/TLS/logging/rollback/re-apply/idempotency 인수 조건에 따른다. #74 서비스 인수 전 #75 운영 적용과 #9 엔진 전환은 HOLD.

기존 `local-20260916/` 증적·실패 원문·완료 티켓·담당/일정·과거 승인 기록은 보존한다.
