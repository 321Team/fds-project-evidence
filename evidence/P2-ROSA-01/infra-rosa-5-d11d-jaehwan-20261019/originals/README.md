# D-11d 재환 본인 확인 원본 — infra-rosa#5 (이재환, 2026-10-19 KST)

결과 회신: https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268210444
계정 소유자가 실행했고, 비밀번호는 IdP 관리자도 압니다(GO §2).

| 파일 | 내용 |
|---|---|
| `d11d-jaehwan-20261019T221505.log` | 1차 transcript. 22:15:05~22:16:03 KST, `Login failed (401 Unauthorized)` → `D-11d RESULT: FAIL`. 입력 실수(비밀번호 대신 명령 문자열을 입력)였고, 권한 질의 전에 STOP했습니다 |
| `d11d-jaehwan-20261019T221702.log` | 2차 transcript. 22:17:02~22:18:08 KST, `D-11d RESULT: PASS`. can-i 6개가 기대값과 같습니다 |
| `d11d-jaehwan.ps1` | 실행 파일. infra-rosa main `f3042f6` README의 d11d-ps 블록 그대로입니다(블록 SHA256 `3f6d0724…3031`). 바꾼 것은 `$API_URL`·`$EXPECTED_USER` 2줄과, 이 프로세스에서만 `oc` 경로를 잡는 머리 3줄입니다(UTF-8 BOM) |
| `run-d11d-window.ps1` | 별도 콘솔 창에서 위 파일을 부르고 `Start-Transcript`로 기록하는 실행기 |
| `SHA256SUMS` | 위 4개 파일의 해시(이 README 제외) |

- **환경:** 재환 PC(SERVER08, 10.1.93.29), Windows PowerShell 5.1
- **oc:** 4.22.17, `openshift-client-windows.zip` SHA256 `528417b2bcee69e57bbf227c12e2e56104afb108faa48829388fed49b281b48e`(mirror.openshift.com 공식 `sha256sum.txt`와 일치)
- **비밀값:** 비밀번호·토큰·kubeconfig는 들어 있지 않습니다. `Password:` 입력은 화면과 transcript에 남지 않습니다.
- **기록되지 않은 시도:** 22:13 터미널 패널 시도는 입력 전에 취소돼 transcript가 없습니다.
- **기록되지 않은 경고:** `list nodes`의 stderr 경고 `resource 'nodes' is not namespace scoped`는 transcript에 들어가지 않았습니다.
