# CR-P1-NTP-01-01 원본 — ansible-ntp-readonly-evidence.at9v4_pp

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ansible-ntp-readonly-evidence.at9v4_pp.tar.gz`, 34,657 bytes |
| SHA-256 | `07579fcc1681af67abcde83fef040a6be88959766082749742523a396320f818` — 같은 폴더 `.sha256` sidecar와 infra-ansible 문서 기록값과 일치 |
| 수집 시각 | 2026-09-18 12:06:05–12:15:03 UTC (21:06:05–21:15:03 KST) |
| 관련 문서 | [CR-P1-NTP-01-01-field-migration.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-field-migration.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 기록 그대로)

- 6대 대상 읽기 전용 수신 기록. `runtime_apply=NOT_RUN`, `acceptance=NOT_ASSESSED`.
- `status=INCOMPLETE_REVIEW_REQUIRED`, `precheck_rc=2`, `finalize_rc=0`, `all_six_host_observations_complete=true`.
- 실행 소스 `63797f3fcb7cfaa3ec8281b2ec6faa32948d84b3`(tree `49bd1495…`), 관측 HEAD·tree 동일. Ansible 엔진 2.16.19. 관측 22건, 명령 45건.
- 문서에 적힌 시각 21:14:44–21:15:00 KST는 이 수집 구간의 일부다.

## 수신 검증

- 압축 내부 파일 204개. 내부 `SHA256SUMS` 203/203, `role-precheck/SHA256SUMS` 4/4 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
