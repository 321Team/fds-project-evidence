# 원본 압축 파일 추가 기록 (2026-09-24)

이 수신 기록의 원본 `collect-record.tar.gz`는 처음 편입할 때 Git에 넣지 않았고, 개인 첨부 보관만 기록돼 있어 독립 검토자의 접근이 미확인이었다. 증적 정책 개정([#30](https://github.com/321Team/fds-project-evidence/pull/30))에 따라 1MB 이하 원본은 Git에 둘 수 있으므로, 팀이 접근할 수 있도록 원본 바이트를 추가한다. 기존 README·RECEIVER_REVIEW.json·SHA256SUMS·`submitted/`는 수정하지 않았다.

| 항목 | 값 |
|---|---|
| 파일 | `collect-record.tar.gz`, 1,204 bytes |
| SHA-256 | `58ed389299582dc6d69d5d19c94d08c82df730c27c5a693b54408d0cca61b758` |
| sidecar | `collect-record.tar.gz.sha256` 추가. 업로드 sidecar 원문 바이트이며 기존 `submitted-archive.sha256`과 바이트 동일. 점검 도구가 요구하는 같은 이름 sidecar 규칙을 맞추기 위한 사본이다 |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |
| 내부 대조 | 압축 안의 파일 5개가 `submitted/`의 5개와 바이트 모두 일치. 내부 `SHA256SUMS` 검증 통과. 절대경로·`..`·링크 없음 |
| 재압축 | 하지 않음 |

압축 내부 목록(`registry/ARCHIVE_CONTENTS.json` 항목)은 #30이 병합된 뒤 main 기준으로 등록한다. #30의 점검 도구가 목록을 압축 바이트에서 다시 계산해 대조한다.
