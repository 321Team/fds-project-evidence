# 원본 압축 파일 추가 기록 (2026-09-24)

이 수집회차의 원본 `ansible-pr47-readiness.tar.gz`는 처음 편입할 때 Git에 넣지 않았고, 보관 위치가 개인 ChatGPT 라이브러리 파일로만 기록돼 있었다. 증적 정책 개정([#30](https://github.com/321Team/fds-project-evidence/pull/30))에 따라 1MB 이하 원본은 Git에 둘 수 있으므로, 팀이 접근할 수 있도록 원본 바이트를 추가한다. 기존 README와 수신 파일은 수정하지 않았다.

| 항목 | 값 |
|---|---|
| 파일 | `ansible-pr47-readiness.tar.gz`, 1,361 bytes |
| SHA-256 | `d58c76fa3818c30f273115d4f18b515aeb8ed079b6e6ab712ba7fa7d598f1153` — 같은 폴더의 `.sha256` sidecar와 일치 |
| 제공 | 이권욱, Claude Code 세션 업로드(2026-09-24). sidecar 업로드본도 저장소 sidecar와 바이트 동일 |
| 내부 대조 | 압축 안의 파일 7개(`evidence/` 아래)가 `received/`의 7개와 SHA-256 모두 일치 |
| 재압축 | 하지 않음 |

압축 내부 목록(`registry/ARCHIVE_CONTENTS.json` 항목)은 #30이 병합된 뒤 main 기준으로 등록한다. #30의 점검 도구가 목록을 압축 바이트에서 다시 계산해 대조한다.
