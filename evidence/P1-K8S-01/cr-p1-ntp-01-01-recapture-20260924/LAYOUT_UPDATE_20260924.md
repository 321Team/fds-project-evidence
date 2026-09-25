# 경로·형식 보완 기록 (2026-09-24)

이 수집회차는 처음에 `evidence/CR-P1-NTP-01-01/recapture-20260924/`로 편입됐다. 증적 정책 개정([#30](https://github.com/321Team/fds-project-evidence/pull/30))에 맞춰 경로와 형식을 보완한다. 수신 바이트와 기존 파일(README, `EXPECTED.sha256`, `SCRIPTS.sha256`, `CHECKOUT.txt`, 수집 스크립트, 실행 로그, `raw/` 압축 7개)은 수정하지 않았다.

## 1. 경로 이동

- CR-P1-NTP-01-01은 baseline에 따로 등록되지 않은 CR이다. NTP 결정·인수 기준은 [P1-K8S-01(#10)](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)에 있으므로, 상위 티켓 경로로 옮겼다(이권욱 결정, 2026-09-24).
- 이전 경로: `evidence/CR-P1-NTP-01-01/recapture-20260924/`
- 새 경로: `evidence/P1-K8S-01/cr-p1-ntp-01-01-recapture-20260924/`
- 파일 16개의 Git blob과 mode는 이동 전후가 같다. 폴더 안에 자기 경로를 기록한 파일이나 상대 링크는 없다.

## 2. 추가한 파일

| 파일 | 내용 |
|---|---|
| `raw/<압축파일>.sha256` 7개 | 각 압축 파일의 SHA-256 sidecar. 값은 기존 `EXPECTED.sha256`과 같고, 만들기 전에 실제 바이트와 7/7 대조했다 |
| `SHA256SUMS` | 이 폴더의 Manifest(자기 자신 제외). 루트 `REGISTRY_SHA256SUMS`에는 이 Manifest만 등록한다 |
| 이 문서 | 보완 경위 |

## 3. 남은 형식 조건

- 압축 7개의 내부 목록(`registry/ARCHIVE_CONTENTS.json` 항목)은 #30이 병합된 뒤 main 기준으로 등록한다. #30의 점검 도구가 목록을 압축 바이트에서 다시 계산해 대조한다.
- 1회차(09:29Z) 수집본은 여전히 편입 대상 밖이다(원본은 각 노드 `/root`에 보존, README 참조).
