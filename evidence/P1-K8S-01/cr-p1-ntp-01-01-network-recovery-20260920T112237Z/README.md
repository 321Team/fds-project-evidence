# CR-P1-NTP-01-01 원본 — ntp-network-recovery-w5e5yw5h

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-network-recovery-w5e5yw5h.tar.gz`, 346,178 bytes |
| SHA-256 | `39de5839e0a2c9249ca984a4a3fbf6553b43767f05c7c4cfc3584b254fa49930` — 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 시각 | 2026-09-20 11:22:37–11:23:58 UTC (20:22:37–20:23:58 KST) |
| 관련 문서 | [CR-P1-NTP-01-01-onepass.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-onepass.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 기록 그대로)

- 읽기 전용 네트워크 회복 점검 수집. `runtime_apply=NOT_RUN`.
- `status=COLLECTION_INCOMPLETE`, `ansible_rc=2`. 6대 모두 `transport_ok=false`, `payload_valid=true`, gap 기록(control01 7건, 나머지 각 1건).
- 실행 소스 `eb08dc8c4ae3505dace39e76a11ef57be75e96ce`, 수집 전후 HEAD·tree 동일.
- infra-ansible 문서에는 이 수집본의 SHA-256이 없다. 업로드 sidecar 값으로 고정한다.

## 수신 검증

- 압축 내부 파일 41개. 내부 `SHA256SUMS` 전부 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
