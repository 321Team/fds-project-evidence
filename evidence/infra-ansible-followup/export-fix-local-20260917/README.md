# Export 진단 수정·추가 로컬 시험 및 후속 CI 준비

2026-09-17. 이 디렉터리는 LOCAL/MOCK 원문과 코드 반영 후 검증을 추가한다.
기존 [실제 Actions 인수 원본](../actions-acceptance-20260917/README.md)은 변경하지 않았다.

## 현재 상태와 source 연결

- 기존 시험 source: 정상 `2750634766862d7fe19479acacc4259ee8315061`, count 결함 `c50a6b3316fabba08d5211933e3733f8026e2d95`.
  정상 CI PASS와 negative CI FAIL/Job failure에 의한 기대 결함 탐지를 구분한다.
- 추가 시험 기준 PR17: `9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6` + PR19 도구 `4da96621fd05a4943b76ca32b860a5779ec65e00`.
- 수정 반영 PR17: `a9785da3485ffd61840a82a3e9bd14ceb4edb50b`.
  실행기와 회귀시험 두 파일만 변경했다. `published-fix/SOURCE.json`에 68개 Git blob/mode를 고정한다.
- 문서 현행화 후 PR17: `6b2ac7a80be1acd187ac73cbd1cf957f708edf85`.
  문서 2개 갱신·계획 1개 추가, 이전 source 66개 blob/mode 유지. 실행기/시험 동작은 수정 commit과 동일하다.
  `documentation/DOC_PUBLICATION.json`, `docs.patch`, `DOC_VALIDATION.json`으로 연결한다.
- Runner PR19는 위 HEAD 그대로다. bundle 내부 README/manifest/이미지/PREPARED는 이번 문서 작업에서 변경하지 않았다.
- 새 source의 실제 Actions는 NOT_RUN. 독립 승인·병합·운영 Apply는 완료하지 않았다.

## 주요 관찰과 검증

| 범위 | 원문 결과 | 해석 |
|---|---|---|
| 수정 전 기존 suite | 156/156 PASS | CI57 + Runner/입력/Admin 기존99, LOCAL/MOCK |
| 저장 장애 시나리오 | 12개: 정상1, fixture 실패1, 저장 장애10 | 합성 I/O 예외 주입; 실제 디스크 고갈 아님 |
| 수정 전 관찰 | 저장 장애8개에서 결과 파일에 PASS 잔존 | 모두 rc1·불완전 manifest로 하네스의 결합 인수 거부 |
| 수정안 | 157/157 PASS, 새 회귀시험은 원본 코드에서 예상 실패 | 기존156 + 새1; 과거 실행 성적을 소급 수정하지 않음 |
| 수정안 저장 장애 재검증 | 쓰기 가능한7개 잔존 PASS 보완; 지속 쓰기 장애1개는 잔존 | best-effort 상태 진단, 원자적 저장 아님 |
| 공개된 a9785da source | 68개 파일 검증, LOCAL58/58 PASS | 통합157 성적은 바이트 동일성으로 재사용, 157개 새 실행이라고 하지 않음 |
| 기존 변조 방어 코드 | 25/25 기대 동작 | manifest 및 제한된 host-result/외부 hash 읽기 범위 |
| 새 교차 대조 모형 | 35/35 | 합성 검토 모형, 운영 Receipt/판정기에 반영되지 않음 |
| 시간초과 | readiness100 + silent100, 기존 지연 조건10회 재현 | 실제 로컬 Python 자식, 운영 Controller 변경 없음 |
| 문서 HEAD | runtime/test blob 동일성 검증 | 문서 변경 후 시험을 추가 실행했다고 주장하지 않음 |

지속 쓰기 장애에서 파일을 갱신하지 못하는 것은 알려진 제한이다. 별도 합의 없이 새로운 병합 차단 AC를 만들지 않는다.
다만 rc·Job/Check·완전한 manifest·digest·source/attempt 결합은 계속 인수 조건이다.
이 시험의 `acceptance_allowed`는 로컬 하네스 판정이며 배포된 인수 서비스가 아니다.
`passed_exit_and_preservation`은 종료·합성 원본 보존만 뜻한다. 이를 모든 진단 상태가 일치한다는 PASS로 확대하지 않는다.
실제 양 엔진/Podman/VM/GitHub 실행, 전원 손실·SIGKILL·OOM 내구성 결과로 해석하지 않는다.

## 원본 보존과 파일 구조

- `local-tests/`: 기존 결과 ZIP에서 선택한 **동일 바이트 사본**. 당시 README와 JSON의 “원격 미반영”은
  수정안 작성 시점의 이력이다. 현재 반영 여부는 위 commit과 `published-fix/`를 따른다. 이력을 고쳐 쓰지 않았다.
- 모든 저장 장애 case의 stdout/stderr/result/합성 원본 fixture를 포함한다.
- TIMEOUT_MATRIX 및 재현 코드는 포함하며 타임아웃 각 회차의 상세 로그는 원래 ZIP에 보존한다.
  Git 선별 사본은 ZIP 전체 추출본이 아니다. 모형/하네스 경로 및 합성 CI_RESULT 안의 source 값은 시험 fixture다.
- `published-fix/`: 실제 반영된 source의 58개 시험 stdout/stderr·검증 JSON·source map 및 당시 원격 재조회 기록.
- `documentation/`: 이번 문서 diff, 문서 변경 검증, 최종 source map, 다음 정상 격리 CI 계획 사본.
- `ORIGIN_INDEX.json`: 선택 사본의 출처·원래 경로·크기·SHA256. ZIP 원본의 모든 958개 manifest 항목도 편입 전 재확인했다.
- `ARCHIVE_INDEX.json`: 이미 제공한 전체 결과 ZIP의 이름/크기/SHA256과 patch hash.
- `PUBLICATION_SHA256SUMS`: 이 디렉터리에서 그 파일 자신을 제외한 전체 파일 집합과 bytes.
  저장소 `REGISTRY_SHA256SUMS`에는 기존 1707개 행 뒤에 이번 파일만 추가한다.

루트 README는 현재 통합 해석이고 `local-tests/README.md`는 이전 시험 시점의 원문이다.
SHA256은 사본 무결성을 증명하며 독립 승인·입력 provenance·최신 서버 상태를 대신하지 않는다.

## 후속 실행 인계

PR17의 [격리 CI 준비 계획](https://github.com/321Team/infra-ansible/blob/6b2ac7a80be1acd187ac73cbd1cf957f708edf85/docs/ci/ARTIFACT_EXPORT_CI_PLAN.md)을 기준으로 새 source의 정상 Actions를 준비한다.
새 Run/Attempt/Job은 아직 없으므로 기존 PR20 고정 Start v1.1 admin 명령이나 과거 Run을 재사용하지 않는다.
현재 호스트의 PREPARED/bundle/image 검사를 통과하면 기존 v1.3 이미지 재사용을 검토하며 새 prepare를 자동 반복하지 않는다.
count 결함 실제 재시험 범위는 이전 증적·변경 영향과 리뷰 결과로 확정한다. 여기서 면제를 확정하지 않는다.

PR17·PR19·evidence PR13의 최종 HEAD별 독립 리뷰는 남아 있다. 과거 COMMENTED는 APPROVED가 아니다.
일반 자동 Workflow 활성화, Issue #5 AC 종결, merge, 운영 Apply/엔진 전환은 별도 판단이다.
