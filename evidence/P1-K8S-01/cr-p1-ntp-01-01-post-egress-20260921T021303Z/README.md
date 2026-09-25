# CR-P1-NTP-01-01 원본 — ntp-pr31-post-egress-pdv_sd3n

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-pr31-post-egress-pdv_sd3n.tar.gz`, 139,505 bytes |
| SHA-256 | `11ea3cf62d3709d902120aca58264f6160725f5045568d4040d4119e54c7b7a9` — 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 시각 | 2026-09-21 02:13:03–02:13:11 UTC (11:13:03–11:13:11 KST) |
| 관련 문서 | [CR-P1-NTP-01-01-post-egress.md](https://github.com/321Team/infra-ansible/blob/dda4f6c6623d60831a670a97a1d57c70b0e045fd/docs/change/CR-P1-NTP-01-01-post-egress.md) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 기록 그대로)

- 실제 적용 실행 `ntp-onepass-f9392ba915da49a19e0fe502e7616cfb`(6대 NTP 전환·egress 설정 후 control01 커널 경로 검사에서 중단) 이후의 읽기 전용 상태 수집.
- `status=COMPLETE`, 6대 모두 `ssh_rc=0`, 잘림 0, `configuration_changes=false`.
- post-egress 후속 검증의 **기준 수집본**이다. SHA-256은 문서 기록값과 일치.
- f9392ba9 실행 자체의 적용 증적 archive는 이 폴더에 없다(미제출).

## 수신 검증

- 압축 내부 파일 14개. 내부 `SHA256SUMS` 전부 일치. 절대경로·`..`·링크 없음.
- 비밀정보 패턴(개인키·password/token 대입·클라우드 키) 검색 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 동기화 인수조건 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
