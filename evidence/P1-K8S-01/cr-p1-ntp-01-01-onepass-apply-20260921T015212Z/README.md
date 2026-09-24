# CR-P1-NTP-01-01 원본 — ntp-onepass-nyol0g41 (실제 적용 실행)

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-onepass-nyol0g41.tar.gz`, 505,525 bytes |
| SHA-256 | `e5739fabc66670b846a59290b864eceac21097d4c89d5dbc37700ce007bd7d23` — 같은 폴더 `.sha256` sidecar와 일치 |
| 실행 시각 | 2026-09-21 01:52:12–01:56:21 UTC (10:52:12–10:56:21 KST) |
| 원본 위치 | ansible01 `server01_ansible` 홈의 `ntp-onepass-nyol0g41.tar.gz`(파일 시각 2026-09-21 10:56:21 KST). `RESULT.json`의 `run_id`로 이 실행임을 확인 |
| 관련 문서 | [CR-P1-NTP-01-01-post-egress.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-post-egress.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 `RESULT.json` 그대로)

- `run_id=ntp-onepass-f9392ba915da49a19e0fe502e7616cfb`, `change_id=CR-P1-NTP-01-01`, `apply_requested=true`.
- 하위 rollout `ansible-ntp-rollout-z2f7cea3`: `child_status=COMPLETE_ROLLOUT_VALIDATED`. `ingress_ready=true`, `egress_completed` 6대.
- `status=STOPPED_REVIEW_REQUIRED`, `error=verify/k8s-control01: remote STOP; see retained response`, `runtime_acceptance=REVIEW_REQUIRED`, `uncertain=false`.
- `ipv6_negative`, `reboot_resync`, `sync_loss_injection`은 모두 `NOT_RUN`.
- 검토 소스 `0e17e2d7713484352c84f72d9ddc55aab6187386`, wrapper `80935766c37215d6e89fec20b0a21523b8a08491`.
- 이 실행 이후의 읽기 전용 상태는 [post-egress 기준 수집본](../cr-p1-ntp-01-01-post-egress-20260921T021303Z/README.md)에 있다.

## 수신 검증

- 압축 내부 파일 186개. 내부 `SHA256SUMS` 185/185, 하위 rollout 59/59, wrapper 11/11 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. 적용 결과의 인수, NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
