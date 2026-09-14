# Issue #7 — 실제 6대 읽기 검증 수신

[코드 PR #15](https://github.com/321Team/infra-ansible/pull/15) · [Issue #7](https://github.com/321Team/infra-ansible/issues/7)

시험 HEAD `27cf2683cce2331ae83266c627991dcf9d000ac7`의 실제 6대 결과다.
2026-09-14 09:09:49~09:12:08 UTC. 전체 판정은 **REVIEW_REQUIRED / exit 1**이다.
16개 예정 단계 중 13개 실행, 12개 PASS. 2.21.3은 8/8 PASS, 2.16.19는
앞의 4단계 PASS 후 SSH 증명 자료형에서 거부됐고 뒤 3단계는 NOT RUN이다.

## 확인된 결과

- 2.16.19 SSH CLI rc=0. 실제 6대의 key count는 문자열 "1"로 기록돼 엄격한 정수 계약을 통과하지 못했다.
- 2.21.3은 정수 1을 기록했다. SSH·hardening check·OS precheck·DNS verify가 모두 통과했다.
- 두 엔진 모두 SSH 파일 불변이 6/6 확인됐고, 모든 관측 원격 단계의 changed는 0이다.
- 설정 apply·운영 엔진 전환은 수행하지 않았다. 기존 P1-ANS-01 Done / PR #4 Closed / #6 Done을 유지한다.
- 원본 FAIL을 변환하거나 PASS로 재작성하지 않았다. 수정본은 별도 새 실행으로 검증해야 한다.

## 검토 자료

- [전체 보고서](results/verification/VERIFICATION_REPORT.json)와 [수신 대조](READONLY_AUDIT.json).
- 두 readonly_ssh/events.jsonl: 2.16.19 문자열과 2.21.3 정수의 실제 차이.
- 2.21.3의 나머지 세 단계 report.json: 정확한 6개 노드와 완료·변경·실패 카운터.
- [출처](SOURCE_PACKAGE.json), [선별 원본 매핑](SOURCE_FILE_MAP.json), 압축 sidecar.

압축 SHA256 `5e26f8f10968d1fd87615e5e29062eca72e1af9ea83eeaa37f8f39eff7ad8789`.
전체 원본 115개, Manifest 114개 및 report 원본 참조 36개 해시가 일치한다.
이 폴더는 선별 자료이며 전체 원문·압축본은 로컬에 보존했다. 팀 공용 보관 URI는 아직 없다.
results/SHA256SUMS는 원본 전체 Manifest이며 이 폴더의 SHA256SUMS는 선별 등록 파일용이다.
등록 원본은 바이트를 유지했고 키·Token 형식 검사에서 일치 항목은 없었다.
callback은 허용 필드만 기록하므로 전체 모듈 결과를 수집한 자료가 아니다.
독립 인수·병합은 대기다. 이전 격리 PASS와 이번 실제 읽기 검증은 서로 다른 실행이다.
