# Issue #6 — 실제 시험 검토 자료

코드 PR: https://github.com/321Team/infra-ansible/pull/13
시험 HEAD: 37544b443fc9b11a35210ee087cb17811e23362d.
이 폴더는 **선별 검토 자료**다. 전체 399개 원본을 Git에 등록한 것으로 보지 않는다.
전체 원문은 사용자 제출 압축본과 로컬 검증본에 보존했다.

## 검토 시작점

- [전체 MATRIX](results/matrix/MATRIX.json): PASS / 동일 baseline / 총 14회 실행.
- [baseline 2.16.19](results/matrix/2.16.19-baseline.json), [2.21.3](results/matrix/2.21.3-baseline.json): 각 14/14 PASS.
- [원문 2.16.19](results/matrix/2.16.19-baseline/regression.log), [2.21.3](results/matrix/2.21.3-baseline/regression.log).
- results/matrix의 나머지 12개 JSON: AND 결함·독립 or 목록 오류·undefined 식을 guard별로 검출.
- [수신 검증](RECEIPT_AUDIT.json), [출처·보관 한계](SOURCE_PACKAGE.json), [소스 SHA](results/SOURCE.txt).
- [이전 실패 MATRIX](prior-failure/MATRIX.json): 원본 FAIL 이력을 그대로 보존.

## 판정

전체 matrix exit=0. 두 엔진 baseline 각 14/14, 12개 결함 변형 검출 PASS.
AND guard 0은 FAIL 4개, guard 1은 FAIL 1개를 검출한다.
잘못된 목록은 guard 0에서 ERROR 1개, guard 1에서 ERROR 4개를 검출한다.
undefined는 각 guard에서 ERROR 7개를 검출한다.
각 변형의 미변경 guard 7개는 PASS이며 두 엔진 집계가 같다.
제출된 실제 관찰 196개를 모두 원문·기대값과 대조해 보고서와 일치함을 확인했다.
수신 검증은 로컬에서 자료를 읽은 것이며 새 Ansible 실행을 대신 만들지 않았다.

압축본 SHA256: e06a8d6cd3f871f4ceccfd2a97a052b4982e9180b3f6806f7a2189a4aecce3e5.
압축본 및 내부 398/398 해시 일치, 총 399개 파일.
이번 Git 등록은 아래 SHA256SUMS에 기재한 선별 자료만 포함한다.
전체 원문은 별도 압축본에서 열람해야 하며 그 보관 경로는 SOURCE_PACKAGE.json을 따른다.
압축본은 저장소 정책에 따라 Git/Release Asset에 업로드하지 않았다.
최초 전체 텍스트 등록 요청은 자동 검토 크기 제한으로 거절되어,
자료를 분할 업로드하지 않고 이번 등록을 선별 검토 자료로 축소했다.

이 폴더에서 sha256sum --check SHA256SUMS로 등록 파일을 검증한다.
루트 REGISTRY_SHA256SUMS는 이번 선별 폴더를 아직 포함하지 않는다.
패키지 출처와 전체 원본 해시 검증, 선별 Git 바이트 검증, 독립 승인 범위는 서로 다르다.

기술 시험 PASS이며 독립 리뷰·증적 편입 승인·병합은 대기다.
P1-ANS-01 Done / PR #4 Closed와 기존 승인 범위를 유지한다.
운영 apply·운영 SSH 키·실제 6노드 검증·운영 엔진 전환 범위는 포함하지 않는다.
