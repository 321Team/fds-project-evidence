# 편입 전 가림 기록 (2026-10-13, 이하영)

- 대상: `assume-role.stderr` 1개
- 이유: AWS 오류 메시지가 입력된 MFA 일회용 코드 값(7자리, 형식 오류로 거부·만료됨)을 그대로 되돌려 출력했다. 스크립트는 argv의 코드를 `REDACTED`로 저장하지만 AWS stderr 본문까지는 가리지 못했다.
- 처리: 코드 값만 `REDACTED(7 digits)`로 바꿨다. 나머지 바이트는 그대로다.
- 원본 해시(CloudShell 생성 `SHA256SUMS` 기재값): `253770620e93045b3bc6c2723e99e45a1428063e1b5a48b64f296b51fb15658c`
- 가린 뒤 해시: `ff82ea97d5c27c758dd2a47574079fc761cdf4b139b3cc456080f58be448604d` — 이 폴더 `SHA256SUMS`의 해당 줄을 이 값으로 바꿨다. 다른 줄은 원본 그대로다.
- 원본 묶음 `evidence-vpn-replan-merged-20261013-164729.tar.gz`(`052169dd…`)은 Git 밖 비공개 보관.
