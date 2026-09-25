# CR-P1-NTP-01-01 원본 — ntp-onepass-j0juc9np (사전 입력 검사에서 중단)

Record ID: **P1-K8S-01** (NTP는 [2026-09-16 #10 Lead 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 따라 P1-K8S-01 하위). 변경 기록: CR-P1-NTP-01-01, 실행 주체 이권욱.

| 항목 | 값 |
|---|---|
| 원본 | `ntp-onepass-j0juc9np.tar.gz`, 893 bytes |
| SHA-256 | `940944fb1a463ff79167e3914435acdedbd8af7a4b9f298ec9e464af56990e23` — 같은 폴더 `.sha256` sidecar와 일치 |
| 실행 시각 | 2026-09-20 14:01:54 UTC (23:01:54 KST) |
| 원본 위치 | ansible01 `server01_ansible` 홈의 `ntp-onepass-j0juc9np.tar.gz`(파일 시각 2026-09-20 23:01:54 KST) |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |

## 내용 요약 (압축 내부 `RESULT.json` 그대로)

- `run_id=ntp-onepass-d029102a5f2d49d9a8a393e8ba632cb0`, `apply_requested=true`.
- `status=STOPPED_REVIEW_REQUIRED`, `error=Actual existing preparation/governance reference required: network_policy_ref`.
- `child_started=false`, `ingress_ready=false`, `egress_completed` 0대. 원격 명령 기록(`COMMANDS.json`)은 빈 목록이다. 입력 참조 검사에서 멈춰 서버 변경 전에 중단된 실행으로 읽힌다.

## 수신 검증

- 압축 내부 파일 3개. 내부 `SHA256SUMS` 2/2 일치. 절대경로·`..`·링크 없음. 비밀정보 패턴 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

이 편입은 원본 보존이다. NTP 인수 판정, P1-K8S-01 AC 체크, 티켓 상태는 바꾸지 않는다.
