# CR-P1-NTP-01-01 원본 — ntp-chronyd-environment-xkmf5tss

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-chronyd-environment-xkmf5tss.tar.gz`, 2,715 bytes |
| SHA-256 | `3f69e141aed26d018b8e8831da1210268ec53c84e964882e12a998431896f90a` — 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 시각 | 2026-09-20 15:41:43–15:41:47 UTC (09-21 00:41:43–00:41:47 KST) |
| 관련 문서 | [CR-P1-NTP-01-01-empty-options.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-empty-options.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 기록 그대로)

- 위 onepass 중단 후 읽기 전용 chronyd 서비스·환경 조회.
- `status=COMPLETE`, 6대 모두 COMPLETE, chronyd `active/running`, errors 0.
- SHA-256은 infra-ansible `docs/change/validation/ntp-empty-options/SUMMARY.json` 기록값과 일치.

## 수신 검증

- 압축 내부 파일 8개. 내부 `SHA256SUMS` 전부 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
