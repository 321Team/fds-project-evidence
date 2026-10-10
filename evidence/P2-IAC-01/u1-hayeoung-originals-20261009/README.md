# P2-IAC-01 — 하영 본인 IaC 역할 시험 원본 보충 — 2026-10-09

이 폴더는 병합·봉인된 [`evidence/P2-IAC-01/u1-hayeoung-20261009/`](../u1-hayeoung-20261009/README.md)(PR #194, merge `6d7bec65c2992c9bb95f9ca261dc9e091133eeb0`)의 **보충 자료**입니다. 기존 폴더는 수정하지 않았습니다.

출처 티켓: [infra-terraform#9](https://github.com/321Team/infra-terraform/issues/9) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)

## 보충하는 내용

| 기존 폴더의 기록 | 이 폴더에서 보충 |
|---|---|
| "원격 37파일의 바이트 미수신" | 원본 **35개 수신**, CloudShell 해시 목록과 **35/35 일치** (N1/N2 AssumeRole stdout 2개는 일부러 미수신) |
| "원격 stdout 원본은 미수신이므로 사후 마스킹 완료 여부를 독립 확인하지 못했습니다" | CloudShell에서 값을 출력하지 않고 **개수만 센 콘솔 출력** 확보. 파일 바이트는 여전히 미수신 |

기존 폴더의 실행 정보·결과표·N2/N5 해석은 그대로 유효합니다. N5 판정(RUNTIME UNDETERMINED)은 바뀌지 않습니다.

## 원본 수신 방법

- 원본 위치: CloudShell `/home/cloudshell-user/u1-hayeoung-20261009-090652` (실행 2026-10-09 18:06:52–18:07:43 KST, 실행자 이하영)
- CloudShell 파일 다운로드 권한이 없어 터미널 출력으로 받았습니다.

1. 사용자가 CloudShell에서 다음을 실행했습니다(콘솔 출력).
   ```
   tar czf - --exclude=N1-wrong-session-name.stdout --exclude=N2-no-mfa-token.stdout . | sha256sum
   → 81b286ca3263feb1f9a7762430a15bf9c6dea3e7109e2de75e3da6de5a907776
   ```
2. 같은 압축을 `base64 -w 76`으로 출력해 콘솔에서 복사·전달받았습니다.
3. 로컬에서 디코드한 압축본 SHA256이 위 값과 **일치**합니다.
4. 압축을 푼 35개 파일이 CloudShell의 원래 해시 목록과 **35/35 일치**합니다.

참고: 첫 시도에서는 채팅으로 전달된 한 줄짜리 base64에 글자 일부가 빠져 해시가 맞지 않았습니다. 이 결과는 버렸고, 76자 줄로 다시 받은 출력만 사용했습니다.

## 파일

- `originals/` — CloudShell 원본 35개를 바이트 그대로 둡니다.
- `originals/remote-SHA256SUMS.txt` — CloudShell의 원래 `SHA256SUMS`(37행)입니다. **바이트는 그대로이고 이름만 바꿨습니다**(SHA256 `b759d905c1bd1e5d27452647c86a4b7dc9e8d1ff95f322864890d05934b55650`). 미수신 2개 때문에 이 목록을 폴더 Manifest로 쓸 수 없습니다.
- `SHA256SUMS` — 이 폴더 전체(README + `originals/` 36개)의 해시입니다.

미수신 2개:
- `N1-wrong-session-name.stdout` (원격 해시 `e3b0c442…` = 빈 파일)
- `N2-no-mfa-token.stdout` (원격 해시 `aa172139…`, 484 bytes)

AssumeRole 응답 원문이라 자격증명이 들어 있을 수 있어 받지 않았습니다.

## 사후 마스킹 확인 (콘솔 출력)

2026-10-09 사용자가 CloudShell에서 값을 화면에 내지 않고 개수만 셌습니다.

```
N1-wrong-session-name.stdout bytes=0 REDACTED=0 SECRET_UNMASKED=0 TOKEN_UNMASKED=0
N2-no-mfa-token.stdout bytes=484 REDACTED=2 SECRET_UNMASKED=0 TOKEN_UNMASKED=0
```

- N2의 `SecretAccessKey`·`SessionToken` 두 값이 `REDACTED`이고, 가려지지 않은 자격증명 줄은 0개입니다.
- 이 판단은 **콘솔 출력**에 근거합니다. 두 파일의 바이트를 받아 독립 재검증한 것이 아닙니다.
- 기존 폴더의 정정 기록은 여전히 유효합니다. 실행 스크립트는 응답을 **먼저 파일에 쓴 뒤** `sed`로 가리는 구현이므로, 마스킹 전까지 N2 평문 자격증명이 CloudShell 홈(0700) 파일에 있었습니다. 이 보충은 "그 뒤 가려졌다"는 사실만 추가합니다.
- 받은 35개 파일과 이 폴더 전체에서 자격증명 문자열(`ASIA…`, `SecretAccessKey`, `SessionToken`)은 발견하지 않았습니다.

## 이 보충이 뜻하지 않는 것

- 전체 U1 PASS, N5 RUNTIME 거부 확정, noMFA 거부 실측이 아닙니다.
- #9·#35 종결, Plan/Apply GO가 아닙니다.

## 참고: 병합 후 브랜치에 남은 커밋

PR #194 병합(20:23 KST) 뒤, 작성자가 병합 사실을 모른 채 같은 브랜치 `evidence/p2-iac-u1-hayeoung-20261009`에 커밋 2개(`c833614`, `5201fe1`)를 올렸습니다. 이 커밋들은 봉인 폴더를 수정하려 한 것으로, 점검 도구에서 SEALED 오류가 났습니다. main에는 들어가지 않았으니 **무시**하시면 됩니다. 그 내용은 이 폴더가 규칙에 맞게 대신합니다.

AI 사용: CLAUDE_ASSISTED. 작성자 이하영의 자기 승인이 아니며 독립 리뷰 대상입니다.
