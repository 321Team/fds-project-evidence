# P1-DNS-01 source-intake 증적 PR #16 병합 후속 정정

작성: 2026-09-25 KST. 대상 수집회차: [`evidence/P1-DNS-01/source-intake/received-20260918T032605Z/`](../../evidence/P1-DNS-01/source-intake/received-20260918T032605Z/README.md).

이 기록은 [PR #16](https://github.com/321Team/fds-project-evidence/pull/16) 독립 리뷰(이하영, 2026-09-23 18:40 KST, HEAD `f5f1537`)가 남긴 후속 요청 3건에 대한 정정·확인이다. 수집회차의 원본 64개와 관리 자료 3개(`MANIFEST.json`, `README.md`, `RECEIPT_SHA256SUMS`)는 수정하지 않는다. 관리 자료를 고치면 `RECEIPT_SHA256SUMS`와 루트 대장의 해시가 어긋나므로, 정책의 "정정은 새 기록으로" 원칙에 따라 이 문서로 보완한다.

## 병합 상태

- PR #16: 검토 HEAD `f5f1537408a17672aed8581e7cbe2962bd4951f5`, merge commit `bb219153af16e1088eb2589bf8994031e51ab1cb`(2026-09-23 18:48 KST, 병합 판단 이권욱).
- 수집회차 README의 "편입 상태는 독립 리뷰·병합 대기"와 "infra-dns PR #1이 관리한다"는 작성 당시 표현이다. infra-dns [PR #1](https://github.com/321Team/infra-dns/pull/1)은 2026-09-25 02:17 KST에 merge commit `7ea2e7826a78db274375685cd1d422cb22f58ce7`로 병합됐다(이하영 APPROVED, HEAD `4206231`).
- 병합은 증적 보존 범위다. P1-DNS-01의 Done / 2026-09-03, AC 판정, Runtime Gate를 바꾸지 않는다.

## 후속 1 — `RECEIPT_SHA256SUMS` 줄바꿈

- 사실: 66줄 모두 CRLF로 끝난다. 파일 SHA-256은 `d3906465ebaae214de17c0096d163e99f112882ed4e8310b6709f01b58781978`이다.
- 검증 도구에 따라 결과가 다르다(2026-09-25 확인).
  - GNU coreutils 9.4 `sha256sum -c RECEIPT_SHA256SUMS`: 66/66 OK. 줄 끝의 CR을 허용한다.
  - Perl `shasum -a 256 -c RECEIPT_SHA256SUMS`: 66개 모두 "could not be read". 파일명에 CR이 붙은 것으로 읽는다.
  - 리뷰어 환경에서도 전 항목 실패가 보고됐다.
- 도구와 관계없이 쓸 수 있는 확인 명령(수집회차 폴더에서 실행): `tr -d '\r' < RECEIPT_SHA256SUMS | sha256sum -c -` → 66/66 OK.
- 기록된 해시 값은 정상이다. 수집회차 README의 `sha256sum -c RECEIPT_SHA256SUMS` 안내는 위 명령으로 읽는다.

## 후속 2 — dns02 원본 Zone 해시의 재현성

- `stage2/dns02/fds.internal.source`는 Secondary가 전송으로 받은 raw 형식 사본(822 bytes, SHA-256 `9f654c78…`)이다. 수집 당시 mtime은 2026-09-18 12:21:02 KST이며 수집 전후 변화는 없었다(`zone-stat-before/after.txt`).
- raw 사본은 Zone 전송이나 refresh 때 다시 쓰일 수 있다. 같은 serial에서 다시 수집해도 이 파일 해시는 재현된다고 보장되지 않는다.
- 앞으로 dns01·dns02 내용 비교의 기준은 `named-checkzone`의 정규화 결과 해시다. 이번 수집의 값은 양쪽 모두 `7161d50eaaed299d4cc14eb409a5351e7c260aff572db04e8a3802c97c09b954`이다. 주 Zone Source의 비교 기준은 dns01 text 원본(`f4bbbc48…`, infra-dns `zones/fds.internal.zone`)이다.

## 후속 3 — dns02 수집 계정

- dns02 수집 계정 `server08`은 의도한 계정이다. 2026-09-24 DNS Lead 이권욱이 "dns02가 server08"이라고 확인했다(infra-dns 리뷰 세션 답변).
- 근거 대조:
  - infra-dns `docs/DNS_SCOPE.md`: dns02 `10.1.93.53` / server08 Secondary, dns01 `10.1.93.52` / server01 Primary.
  - 수집 절차 `docs/DNS_CONSOLE_SECOND_STEP.md`: dns01 `server01_dns01`, dns02 `server08` 기존 관리 계정.
  - 수집 기록: `stage2/dns02/SESSION.json` uid 1002, `stage1/dns02/SESSION.txt`와 `stage2/dns02/COMMANDS.json`에 `server08` 표기.
- 이 확인은 계정 사용의 의도에 대한 것이다. 계정 권한 범위나 sudo 설정의 적정성을 새로 판정하지 않는다.

## 참고 — 수집기 실행 조건(사실 기록)

수집기(infra-dns `091ecee`, SHA-256 `9458d9aa…`)는 코드 독립 리뷰 전에 운영 서버에서 실행됐다. 결과는 infra-dns `zones/fds.internal.zone` 관리 Source로 쓰였다. 2026-09-23 중앙 정책 §3.2 4-1의 순수 검증기 조건 3(결과를 운영 입력으로 쓰지 않음)에 해당하지 않는다. 이 정책은 소급 적용하지 않으며, 이 기록은 판정이 아니라 사실 보존이다. 수집기 코드는 이후 infra-dns PR #1 독립 리뷰(HEAD `4206231`, 수집기 파일 무변경)를 거쳐 병합됐다.

## 범위와 복구

새 수집·서버 접속·Runtime 시험을 수행하지 않았다. 원본과 기존 관리 자료를 변경하지 않았다. 복구는 이 기록을 추가한 PR의 revert이다.
