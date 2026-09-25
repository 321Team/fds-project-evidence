# 원본 압축 파일 추가 기록 (2026-09-24)

이 PR로 편입한 두 수집회차의 원본 압축 파일은 처음에 Git에 넣지 않았고, 보관 위치가 개인 ChatGPT 라이브러리 파일 ID로만 기록돼 있었다(`SOURCE_PACKAGE.json`). 증적 정책 개정([#30](https://github.com/321Team/fds-project-evidence/pull/30))에 따라 1MB 이하 원본은 Git에 둘 수 있으므로, 팀이 접근하고 리뷰어가 원본을 직접 대조할 수 있도록 각 수집회차의 `source/` sidecar 옆에 원본 바이트를 추가한다. 기존 README, `SOURCE_PACKAGE.json`, `raw/`는 수정하지 않았다.

| 원본 | 크기 | SHA-256 | sidecar | 압축 내부 ↔ `raw/` |
|---|---|---|---|---|
| `stage-a/dad-supplement-20260916T150750Z/source/FDS_P1_LB_01_DAD_20260916T150750Z_2q4miky1.tar.gz` | 10,044 bytes | `9a8c149d3f0e48a43b6d052c3389b7f01ae9857bf30b03cfd592c16927d850a0` | 저장소 sidecar와 일치, 업로드 sidecar와 바이트 동일 | 30/30 SHA-256 일치 |
| `stage-b/preflight-20260917T031743Z/source/FDS_P1_LB_01_STAGEB_PREFLIGHT_20260917T031743Z_ui0l6jwq.tar.gz` | 15,085 bytes | `a1a7bb272a770ba44f5ae6542f0f6aee2a948cbbcf773a6f31242b83abf23281` | 저장소 sidecar와 일치, 업로드 sidecar와 바이트 동일 | 47/47 SHA-256 일치 |

- 제공: 이권욱(P1-LB-01 Lead), Claude Code 세션 업로드(2026-09-24). 재압축 없음.
- 이로써 infra-lb 리뷰에서 확인하지 못했던 "원본 tar.gz 외부 SHA-256 대조"를 이 저장소에서 할 수 있다. `collector-used.py`와 배포 v1.0 원본 대조는 여전히 범위 밖이다.
- 압축 내부 목록(`registry/ARCHIVE_CONTENTS.json` 항목)은 #30이 병합된 뒤 main 기준으로 등록한다.
