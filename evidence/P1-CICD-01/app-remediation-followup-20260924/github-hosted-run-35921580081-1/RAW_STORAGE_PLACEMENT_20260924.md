# 원본 artifact 정식 보관 위치 배치 기록 (2026-09-24)

[RAW_STORAGE_DECISION_20260924.md](RAW_STORAGE_DECISION_20260924.md)에서 지정한 정식 보관 위치에 원본을 배치하고 해시를 대조한 기록이다. 기존 결정 문서와 receipt는 수정하지 않았다.

| 항목 | 값 |
|---|---|
| 위치 | `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\01차 프로젝트\02 프로젝트 결과물\` |
| 원본 | `candidate-images-bbe349c8815ed2ade3de87a1b312221c34f4361b-1.zip` |
| sidecar | `candidate-images-bbe349c8815ed2ade3de87a1b312221c34f4361b-1.zip.sha256` (같은 위치) |
| 크기 | 278,490,138 bytes — 기대값과 일치 |
| SHA-256 | `22c0952ccafa9dc5d65506f821e5c125179d9bd4b7bcbfcd193dda36d5415eb8` — 기대값·sidecar와 일치 |
| 대조 방법 | Windows PowerShell `(Get-Item).Length`, `Get-FileHash -Algorithm SHA256`, `Get-Content <sidecar>` |
| 수행 | 이권욱(Lead), 2026-09-24. 출력은 Claude Code 세션에서 기대값과 대조 |

## 결과

- 이 원본의 팀 접근 보관 위치는 위 공유 디렉터리다. 결정 문서의 "기한 전 조치"를 완료했다.
- cicd-runner01의 사본은 예비 사본으로 남긴다. 2026-10-31 임시 허용 기한은 더 이상 정식 보관의 조건이 아니다.
- 이 대조는 Lead의 수행 결과다. 원본 수신 대조는 이미 이하영이 독립적으로 수행했다(receipt 참조). 공유 위치 사본에 대한 별도 독립 대조는 하지 않았다.
- 보관 위치만 바뀐다. CVE BLOCK 판정, APP BLOCK·Runtime AC 1/10·Delivery NOT_VERIFIED는 그대로다.
