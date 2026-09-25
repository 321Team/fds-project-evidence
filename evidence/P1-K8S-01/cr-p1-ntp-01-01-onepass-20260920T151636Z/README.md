# CR-P1-NTP-01-01 원본 — ntp-onepass-1vu26i8b

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-onepass-1vu26i8b.tar.gz`, 387,313 bytes |
| SHA-256 | `23846bb6bcbaa4c4cc5e4bf1fa770f6262743fd11d76511f91a8a73dd8653fe9` — 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 시각 | 2026-09-20 15:16:36–15:17:21 UTC (09-21 00:16:36–00:17:21 KST) |
| 관련 문서 | [CR-P1-NTP-01-01-empty-options.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-empty-options.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 기록 그대로)

- onepass 실행 `ntp-onepass-c112dd98ad56453e86f5c648e54f2cce`의 증적.
- `status=STOPPED_REVIEW_REQUIRED`, `error=Approved rollout failed or was interrupted; egress was not started`. 하위 rollout `ansible-ntp-rollout-2jj54ht7` 포함.
- 검토 소스 `eb08dc8c4ae3505dace39e76a11ef57be75e96ce`. SHA-256은 infra-ansible `docs/change/validation/ntp-empty-options/SUMMARY.json` 기록값과 일치.

## 수신 검증

- 압축 내부 파일 118개. 내부 `SHA256SUMS` 전부 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
