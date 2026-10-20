# P2-ROSA-01 — infra-rosa#5 D-11d 이재환 본인 확인 원본 (2026-10-19 실행, 2026-10-20 수신)

- 책임: [infra-rosa#5](https://github.com/321Team/infra-rosa/issues/5) (P2-ROSA-01 Sub-task 3/6) · Execution Lead 이하영
- 성격: [PR #248](https://github.com/321Team/fds-project-evidence/pull/248) 병합 수집회차 `evidence/P2-ROSA-01/infra-rosa-5-bootstrap-20261019/`의 README "미수신 (Pending)" 표 중 **이재환 D-11d 2행**을 받는 후속 수집회차입니다.
  - 병합된 폴더는 닫힌 폴더라 수정하지 않았습니다(EVIDENCE_POLICY '원본 보존과 무결성').
  - 그 표의 이재환 2행은 이 폴더로 대체합니다.
  - 같은 표의 **이권욱 D-11d 행은 이 수집회차 범위가 아닙니다.**
- 결과 회신: [#5 6268210444](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268210444) (D-11d RESULT: PASS)
- 원본 전달: [#5 6281257850](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6281257850)
- 계정·비밀번호 조건: 계정 소유자(이재환)가 실행했습니다. 비밀번호는 IdP 관리자(이하영)도 압니다. 일괄 생성 동의는 GO §2·P8 조건에 따른 것입니다.

## 수신 경로와 무결성

| 단계 | 내용 |
|---|---|
| 생산 | 이재환 PC(Windows PowerShell 5.1)에서 `Start-Transcript`로 기록 |
| 전달 | 생산자가 팀 공유 폴더 `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\d11d-jaehwan-20261019\`에 6개 파일을 업로드 |
| 수신 | 2026-10-20 이하영이 공유 사본을 재해시했고, 생산자 보고 값과 6/6 일치. 바이트 그대로 `originals/`로 복사(이름·내용 변경 없음) |
| 기준 | `originals/SHA256SUMS`(생산자 작성, 4파일)와 그 파일의 SHA-256 `b8b013a7bc22eabc61ef5adc9dfaacef9447b2ff0a0fa6294c5e6d45aebf8f2e`. 생산자 `originals/README.md`(`5be5106d…9b25`)는 그 Manifest 대상이 아니라서 `REGISTRY_SHA256SUMS`에 따로 등록 |

## 파일 (`originals/`)

| 파일 | 크기 | SHA-256 | 내용 |
|---|---:|---|---|
| `d11d-jaehwan-20261019T221505.log` | 1,980 | `52a5da28e28a032ec8a0884ec343568d4865e25a15f6414e608b289bf39a8985` | 1차 transcript 22:15:05~22:16:03 KST. `Login failed (401 Unauthorized)` → `D-11d RESULT: FAIL`. 권한 질의 전 STOP |
| `d11d-jaehwan-20261019T221702.log` | 1,939 | `ab61f033cfa68a838de714b258f21d7d888bc9d4afbd33e4d9a1e62b602c70ea` | 2차 transcript 22:17:02~22:18:08 KST. `USER=jaehwan`, `SERVER=<API_URL>`, can-i 6개, `D-11d RESULT: PASS` |
| `d11d-jaehwan.ps1` | 2,591 | `4f70ce1543299df84f6b7ebb1287f0106c53d65dbdf94a1df23154843a754c15` | 실행 파일 — README d11d-ps 블록 + 값 2줄 + `oc` 경로(이 프로세스만) |
| `run-d11d-window.ps1` | 406 | `23c1bae17e348129cc9417f13135c0ea95a28ed9caa92271d887cfc2a82da91b` | 별도 콘솔 창 실행기(`Start-Transcript`) |
| `SHA256SUMS` | 367 | `b8b013a7bc22eabc61ef5adc9dfaacef9447b2ff0a0fa6294c5e6d45aebf8f2e` | 위 4개 파일 해시(생산자 작성) |
| `README.md` | 1,808 | `5be5106d38d598164f3e5e03336088c6338a4b9456796e5bf6711b9f6b399b25` | 생산자 설명 |

## 2차 결과 (transcript 그대로)

| 질의 | 기대(jaehwan) | 관측 |
|---|---|---|
| `get pods -n fds-app` | yes | yes (rc=0) |
| `create deployments -n fds-app` | no | no (rc=1) |
| `list nodes` | no | no (rc=1) |
| `get secrets -n fds-app` | no | no (rc=1) |
| `create servicemonitors.monitoring.coreos.com -n fds-app` | yes | yes (rc=0) |
| `create prometheusrules.monitoring.coreos.com -n fds-app` | yes | yes (rc=0) |

- 로그인 직후 보인 project는 `ci-cd`·`fds-app`·`monitoring-api` 3개입니다.
- 실행 파일은 전용 임시 KUBECONFIG(GUID 폴더)를 쓰고, `finally`에서 이전 `KUBECONFIG` 값 복원·logout·파일 삭제를 합니다(PR#43 S1·P9).

## 편입 시 확인·차이 기록

- **실행 블록 커밋 표기:** `d11d-jaehwan.ps1` 첫 줄 주석은 "infra-rosa main `d2f2b2b` README d11d-ps block"입니다. 생산자 회신과 생산자 README는 `f3042f6`라고 적었습니다.
  - 편입자가 infra-rosa에서 두 커밋의 `platform/rbac/bootstrap/README.md` PowerShell 블록을 비교했고, **서로 같았습니다.** 실행 내용에는 차이가 없습니다.
  - 원본 주석은 고치지 않았습니다.
- **transcript에 없는 것:**
  - 22:13 터미널 패널 시도(입력 전 취소, 토큰 없음)
  - `list nodes`의 stderr 경고 `resource 'nodes' is not namespace scoped`
  - 두 가지 모두 생산자 README와 회신에 적혀 있습니다.
- **1차 FAIL:** 비밀번호 대신 명령 문자열을 입력한 실수(401)입니다. 권한 결과가 아니며, PASS로 덮지 않고 그대로 보존합니다.

## 민감정보

- **자격증명 0건:** 편입자가 전문을 읽고 패턴 검사(OAuth `sha256~` token, JWT, 개인키, `client-key-data`, AWS access key, `password:`)를 했고 0건이었습니다. `Password:` 입력은 transcript에 남지 않습니다.
- **식별자 포함:** 생산자 PC 호스트명 `SERVER08`, Windows 사용자 `soldesk`, 내부 IP `10.1.93.29`(README), 로컬 임시 경로. 기존 P2 증적과 같은 수준이라 원본 바이트 보존 규칙에 따라 그대로 둡니다.

## 판정 범위

`D-11d(jaehwan)=PASS(2차) / 1차=FAIL(입력 실수, 보존) / ORIGINALS=RECEIVED(6/6 해시 일치) / D-11d(gwonuk)=이 수집회차 범위 아님`

해시 일치는 무결성 확인이며 시험 PASS의 단독 근거가 아닙니다. #4/#38 Full, P2-ROSA-01 AC 완료, 티켓 종결이 아닙니다.
