# Issue #7 구조화 결과 — 격리 CLI PASS 수신

[코드 PR #15](https://github.com/321Team/infra-ansible/pull/15) · [Issue #7](https://github.com/321Team/infra-ansible/issues/7)

시험 HEAD: `27cf2683cce2331ae83266c627991dcf9d000ac7`.
서버 단위시험 27/27 PASS, 두 엔진 28회 실제 CLI + 26개 파생 입력의 총 54개 판정 PASS다.
실제 운영 6대 결과가 아니라 **같은 Linux 서버의 local 별칭 6개**로 실행한 격리 시험이다.

## 검토 순서

- [MATRIX](results/matrix/MATRIX.json): 54개 기대결과 일치, 두 baseline 동일, exit 0.
- results/matrix/의 엔진별 baseline: 정상 6개 별칭의 완료·변경 수 원문.
- expected_negative: rc=7·condition=true·실패 hook·ignored 1개/노드 증명.
- expected_expression: 동일 태그·ignore_errors가 있어도 표현식 오류는 REVIEW_REQUIRED.
- [수신 검증](RECEIPT_AUDIT.json): 28개 report 원본 해시 112개 및 모든 54개 판정 대조.
- [출처와 보관 한계](SOURCE_PACKAGE.json), [선별 원본 매핑](SOURCE_FILE_MAP.json).

## 무결성과 범위

압축 SHA256: `be5c98f5455fab020dfa31c95082ae5de9f5a3c1f2839c502400d5297cf75b3e`.
217개 원본 파일, 상위 Manifest 216개·중첩 Manifest 205개 해시가 일치한다.
의존성은 두 고정 엔진과 Python 3.12.14이며 소스 상태는 실행 전후 clean으로 보고됐다.
수신 검토는 제출 자료를 읽어 확인한 것이며 검토 PC에서 새 Ansible 실행을 만들지 않았다.

이 폴더는 선별 검토 자료다. 전체 217개 원본은 압축본과 로컬 검증 폴더에 보존했다.
results/SHA256SUMS는 원본 전체 Manifest이므로 이 선별 폴더만으로 전체를 검증할 수 없다.
이 폴더의 SHA256SUMS는 등록한 선별 원본과 새 수신 문서를 검사한다.
루트 REGISTRY_SHA256SUMS에는 이번 폴더를 추가하지 않았다.
원본 파일을 수정하거나 정규화하지 않았으며 full archive는 Git/Release Asset에 업로드하지 않았다.
키 내용·Token에 대한 제한된 형식 검사는 일치 항목이 없었다. 전체 보관 URI는 아직 없다.

두 이전 FAIL 압축본도 보존하며 과거 FAIL을 PASS로 덮어쓰지 않는다.
이 결과는 **격리 시험 기술 PASS**다. 실제 6대 읽기 비교, 이하영님의 독립 검토,
증적 편입 승인·병합은 대기다. 운영 apply·운영 엔진 전환을 수행하지 않았다.
P1-ANS-01 Done / PR #4 Closed / Issue #6 Done을 유지한다.
