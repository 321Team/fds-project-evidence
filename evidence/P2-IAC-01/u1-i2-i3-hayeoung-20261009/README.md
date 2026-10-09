# P2-IAC-01 — 하영 본인 IaC 역할 U1-I2(Plan)·U1-I3(lock fixture) — 2026-10-09

출처 티켓: [infra-terraform#9](https://github.com/321Team/infra-terraform/issues/9) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)
결과 게시: [I2 결과](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6083161408) · [I3 작업창](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6083409808) · [I3 결과](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6083475317)
앞선 U1-I1/I4: [`../u1-hayeoung-20261009/`](../u1-hayeoung-20261009/README.md)

## 공통

| 항목 | 값 |
|---|---|
| 실행자 | 이하영. `321team-hayeoung` 콘솔 MFA 로그인 → 실행마다 OTP를 입력해 `FDS-IaC-Operator/321team-hayeoung`로 AssumeRole. root 미사용 |
| 환경 | AWS CloudShell 서울, 계정 `774055931866` |
| 대상 | `fds-tfstate-774055931866-ap-northeast-2` / `phase2/network/terraform.tfstate` + native `.tflock` |
| source | infra-terraform main `81162467` network 6파일. 묶음 SHA256 `a3aae730e5bfe8378d8243f90e24d73fc93587c9bdc0add8bdc551ec76bbe933`, 파일별 해시는 권욱 network Plan(`../network-plan-20261009/source-manifest.json`)과 동일 |
| Terraform | 1.16.4 linux_amd64, 공식 zip SHA256 `dc94af0eef1147718ad7c8daea792ed199e3e0492eec180d0adafa2a65a879df` 검증 후 설치 |
| AWS 변경 | 시험 lock 객체 1개 생성 후 조건부 삭제(I3)와, Terraform이 Plan마다 lock을 잡았다 놓은 것뿐. **state 본문 생성·수정·삭제 0, Apply 0, 자원 생성 0, 비용 0** |
| 자격증명 | 두 실행기 모두 임시 자격증명을 메모리(프로세스 환경)에서만 사용합니다. I2는 AssumeRole 응답을 메모리에서 `Credentials` 제거 후 저장했고, I3 실행기는 출력 저장 전 자격증명 문자열을 `[REDACTED]`로 바꿉니다. MFA 코드는 저장하지 않았습니다(명령 기록에 `REDACTED`). 편입본 전체에서 `ASIA…`·평문 `SecretAccessKey`/`SessionToken` 0건 |

## U1-I2 — 본인 역할 network Plan

`originals/fds-u1-i2-hayeoung-20261009-143709/evidence/` · 실행기 `u1_i2_hayeoung.py`(같은 폴더에 자기 사본 저장)

| 항목 | 값 |
|---|---|
| 시각 | 2026-10-09 23:37:35 – 23:38:51 KST |
| 사전 | state·lock prefix 비어 있음(`before_keys=[]`) |
| fmt / init / workspace / validate | rc0 / rc0 / `default` / valid |
| plan | `-var=execution_enabled=true`, rc2, **managed create 20 / update 0 / delete 0** |
| plan 파일 | SHA256 `98c3c72583e82ee1d4ab71db5a90e89b0d9614c64d0a89431bd1f9ea70215802`. CloudShell 비공개 보관, **Git 미편입** |
| 사후 | `after_keys=[]` → lock 정상 해제, **state 미생성** |
| 판정 | `PLAN_CAPTURED` |

작업창: #9에는 10-10 00:10 작업창을 공지했지만 실제 실행은 그보다 33분 이른 23:37이었습니다. 시작 시 state·lock이 비어 있었고 충돌은 없었습니다. 실행 후 #9에 정정과 작업창 해제를 기록했습니다.

## U1-I3 — 시험 lock 충돌·정리·재시도

`originals/fds-u1-i3-hayeoung-20261009-144222/results/`

실행 코드:
- 권욱 실행기 `tools/u1_lock_fixture.py`(infra-terraform main, PR #19) **원문 그대로**. SHA256 `645341054d3f5369b5950f38d1fc2fa5578f6a6a0334d6dbf3f6608a3f9aaa84`. 실행 때 각 결과 폴더에 `runner.py`로 자기 사본을 저장합니다.
- 하영 래퍼 `wrapper/u1_i3_hayeoung.py`. SHA256 `27d57ae88fbf34f693f174dff44c0af8963a5625841e3a6094eb4f98bf2bedfd`(CloudShell 실행 출력의 `WRAPPER_SHA256`와 동일한 로컬 사본). 래퍼가 바꾼 것은 다음뿐입니다.
  1. 실행 주체 `CALLER` → `321team-hayeoung`
  2. 소스를 git 대신 I2와 같은 network 6파일 묶음에서 읽음. 실행기의 `source-files`/`source-blob-*` 호출만 대체하고, 나머지 preflight 검사는 원문대로 실행
  3. 본인 MFA AssumeRole 자격증명을 프로세스 환경변수로만 제공
  4. 작업 위치를 `/tmp`로 이동(아래 첫 STOP 참고). 끝난 뒤 결과를 홈으로 복사하고 provider 캐시(`.terraform`)는 제외

| 회차 | 폴더 | 시각(KST) | 결과 |
|---|---|---|---|
| 1 점검 | `originals/fds-u1-lock-wu07syp7/` | 23:42:39 – 23:42:56 | **STOP** `init failed`. CloudShell 홈(1GB, 여유 622MB)에 AWS provider 설치 중 `no space left on device`. AWS 변경 없음 |
| 2 점검 | `.../results/fds-u1-lock-obozx9my/` | 23:53:21 – 23:53:53 | `READ_ONLY_PREFLIGHT_PASS` (래퍼가 작업 위치를 /tmp로 옮긴 뒤) |
| 3 실행 | `.../results/fds-u1-lock-od9ndvdh/` | 23:56:39 – 23:57:41 | **`FIXTURE_COLLISION_RETRY_PASS`** |

3회차 세부(실행 기록 `execution-records.json`):

| 단계 | 결과 |
|---|---|
| 사전 | prefix 비어 있음, lock `NoSuchKey` |
| 시험 lock 생성 | `put-object --if-none-match '*'` rc0. ID `1254e486-b63b-4918-a763-0d97664056f3`, ETag `"bc153d109d90f85e084d05382bc1a77a"`, VersionId `BkTDUlNeaQx1C5YcVxiDRdOdAp_n53FE` (`owned-lock-receipt.json`) |
| 충돌 | `plan -lock-timeout=5s` rc1. `Error acquiring the state lock` / `StatusCode: 412` / `ID: 1254e486-…` / `Who: …/FDS-IaC-Operator/321team-hayeoung` |
| 정리 | 원문·ETag 재대조 → `delete-object --if-match` rc0 → `NoSuchKey`. version ID 지정 삭제 아님 |
| 재시도 | `plan -lock-timeout=60s` rc2, `show -json` managed create 20 |
| 사후 | lock `NoSuchKey`, prefix 비어 있음 |
| 작업창 | `window_confirmation` = [#9 6083409808](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6083409808). 권욱의 "바로 진행 가능" 확인(메신저, 하영 전달)으로 23:55–00:15 KST 공지. 처음 게시 때 UTC를 KST로 잘못 적어 같은 댓글을 수정함 |

## 수신 방식과 무결성

- CloudShell에서 위 세 위치를 `tar czf`로 묶고 `base64 -w 76`으로 출력했습니다. 사용자가 그 출력을 복사해 PC 파일로 저장했고, 로컬에서 디코드했습니다.
- 제외 항목: `*.tfplan`(Plan 바이너리, 비공개 보관), `.terraform`(provider 캐시).
- 로컬 디코드 압축본 SHA256 `a66dc7c80cdbf986da49d52a2fee11ef9f33a27da1fa732be0892ee57df1c2f1`, gzip 무결성 OK, 파일 138개입니다. **CloudShell 쪽 압축 해시 출력과의 대조는 하지 못했습니다**(사용자 콘솔 값 미수신).
- 대신 각 폴더의 원래 `SHA256SUMS`로 바이트를 확인했습니다. **116/117 일치**이고, 나머지 1개는 일부러 제외한 `retry.tfplan`입니다. Manifest가 덮지 않는 18개(I3 폴더의 `network/` 소스 사본)도 source 해시와 모두 일치합니다.
- `originals/` 아래 원래 `SHA256SUMS` 파일들은 바이트 그대로입니다. 폴더 Manifest는 최상위 `SHA256SUMS`입니다.

## 이 편입이 뜻하지 않는 것

- **U1-I5(실제 Terraform 프로세스 강제 종료 후 lock 복구)는 NOT_RUN**입니다. noMFA 실측 거부도 NOT_RUN입니다.
- I3는 실행기 설계대로 "시험 lock과 Plan의 충돌·정리" 시험이며, 두 Terraform 프로세스의 실제 경쟁이 아닙니다.
- 권욱 본인 I3·I5를 대신하지 않습니다. #9·#35 종결이나 Apply GO가 아닙니다.

AI 사용: CLAUDE_ASSISTED. 작성·실행자 이하영의 자기 승인이 아니며 독립 리뷰 대상입니다.
