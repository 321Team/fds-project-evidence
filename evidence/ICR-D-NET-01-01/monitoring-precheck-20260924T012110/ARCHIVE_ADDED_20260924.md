# 원본 압축 파일 추가 기록 (2026-09-24)

이 수집회차의 원본 `ICR_MON_Precheck_N11a7g.tar.gz`는 처음 편입할 때 Git에 넣지 않았고, 사용자 첨부 보관만 기록돼 있어 독립 검토자의 접근이 미확인이었다. 증적 정책 개정([#30](https://github.com/321Team/fds-project-evidence/pull/30))에 따라 1MB 이하 원본은 Git에 둘 수 있으므로, 팀이 접근할 수 있도록 원본 바이트를 추가한다. 기존 README·RECEIPT·SHA256SUMS·`original/`은 수정하지 않았다.

| 항목 | 값 |
|---|---|
| 파일 | `ICR_MON_Precheck_N11a7g.tar.gz`, 9,443 bytes |
| SHA-256 | `c7ef76c9e7a4b314df96e946ee4db5d7b71e96bb22224903b713cace31a2b724` — 같은 폴더의 `.sha256` sidecar와 일치 |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24) |
| 내부 대조 | 압축 안의 파일 8개(`ICR_MON_Precheck_N11a7g/` 아래)가 `original/`의 8개와 바이트 모두 일치. 내부 `SHA256SUMS` 검증 통과. 절대경로·`..`·링크 없음 |
| 재압축 | 하지 않음 |

압축 내부 목록(`registry/ARCHIVE_CONTENTS.json` 항목)은 #30이 병합된 뒤 main 기준으로 등록한다. #30의 점검 도구가 목록을 압축 바이트에서 다시 계산해 대조한다.
