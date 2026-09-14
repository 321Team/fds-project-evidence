# Issue #7 — 동일 커밋 격리·실제 6대 검증 PASS

[코드 PR #15](https://github.com/321Team/infra-ansible/pull/15) · [Issue #7](https://github.com/321Team/infra-ansible/issues/7)

시험 HEAD: `357965058cdcaa129b14c29a09b3e4e19215195f`.
2026-09-14 09:41:33~09:45:59 UTC. 격리와 실제 읽기 검증 모두 같은 커밋으로 실행됐다.

## 판정과 검토 시작점

- [격리 MATRIX](results/matrix/MATRIX.json): 32회 실제 CLI + 26개 파생 입력 = 58/58 PASS.
- [실제 6대 보고서](results/verification/VERIFICATION_REPORT.json): 16/16 단계 PASS_READONLY_SCOPE.
  두 엔진 각각 SSH 읽기·hardening check·OS precheck·DNS verify를 포함한 8개 단계를 완료했다.
- [서버 단위시험](results/unit-tests.log): 28/28 PASS.
- 두 readonly_ssh/events.jsonl: 키 개수 정수 1/1 및 키 파일 불변이 실제 6대에서 확인됐다.
- ssh_proof_wrong_count/report.json: 잘못된 개수 2는 명령 rc=0이어도 REVIEW_REQUIRED다.
- [격리 수신 대조](COMBINED_MATRIX_AUDIT.json), [실제 읽기 수신 대조](COMBINED_READONLY_AUDIT.json).

모든 관측 원격 단계의 changed=0이고 failed/unreachable/rescued/ignored=0이다.
두 엔진의 SSH 키 파일 불변은 각각 6/6 확인됐다. 설정 apply·운영 엔진 전환은 수행하지 않았다.
hardening은 check mode, DNS는 verify phase였다. 기존 서버 main checkout 반영은 별도다.

## 무결성·출처·보관 한계

압축 SHA256: `8830318685902f64548e29423d9479d68d5606ea231e8e8fdeba4cef4f287a89`.
전체 367개 파일, 상위 Manifest 366개·격리 Manifest 229개 해시 일치.
원본 참조는 격리 128개 + 읽기 48개 = 176개 해시를 대조했다.
Python 3.12.14 및 두 엔진의 고정 의존성을 확인했고, 실행 전후 소스 clean이 보고됐다.

원본 압축본·Manifest·제외한 전체 원문은 로컬에 보존했다. 이 Git 폴더는 선별 검토 자료다.
원본 전체 Manifest는 이 선별 폴더에 복사하지 않았다. 전체 재검증에는 압축본이 필요하다.
[출처와 보관 위치](SOURCE_PACKAGE.json) 및 [선별 원본 매핑](SOURCE_FILE_MAP.json)을 따른다.
SHA256SUMS는 이번 선별 원본과 수신 문서를 검증한다. 루트 REGISTRY_SHA256SUMS는 변경하지 않았다.
전체 압축본은 Git/Release Asset에 업로드하지 않았고 팀 공용 보관 URI는 미등록이다.
callback은 허용 필드만 기록하며 전체 모듈 결과 덤프가 아니다.
원본 바이트를 보존했고 제한된 키·Token 형식 검사에서 일치 항목은 없었다.

이전 격리 PASS와 실제 부분 실패는 각각 기존 회차 경로에 보존한다. 과거 FAIL을 고쳐 쓰지 않았다.
이번 기술 검증은 PASS이며 이하영님의 독립 리뷰·증적 편입 승인·병합은 대기다.
P1-ANS-01 Done / PR #4 Closed / #6 Done을 유지하고 #8 → #5 → #9를 별도로 진행한다.
