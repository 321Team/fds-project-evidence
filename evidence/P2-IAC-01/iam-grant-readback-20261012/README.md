# P2-IAC-01 — IaC 역할 부여 원본 + 3인 IAM 사용자 정책 내용 readback (#9 종결 근거) — 2026-10-12

출처 티켓: [infra-terraform#9](https://github.com/321Team/infra-terraform/issues/9) (Sub-task 2/6, Hard Gate 1·2) · 원티켓 [fds-project-baseline#35](https://github.com/321Team/fds-project-baseline/issues/35)
관련 리뷰: [6115764768](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6115764768)(B1·B2), [6116249967](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6116249967)(ARN 충돌), [6116387633](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6116387633)(종결 전 확인 조건)

## 1. IaC 역할 부여 원본 — `grant-original/fds-approved-grant-mafyuau8/`

| 항목 | 값 |
|---|---|
| 생산·실행자 | 이권욱 (CloudShell, 2026-10-09 17:18:39–17:22:09 KST, [부여 기록](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6077294756)) |
| 전달 | 권욱 → 공유 폴더 `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\` ([전달 보고 6116387633](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6116387633)) |
| 하영 수신 | 2026-10-12 11:19:57 KST, 공유 폴더에서 비공개 로컬 경로로 복사 |
| archive | `fds-approved-grant-mafyuau8.tar.gz` **107,026 bytes**, SHA256 `e9fa0ab95bbfe0df5469b3e89867840e009a4a8889f1ba068d538572bfc3a343` — 권욱 보고값과 **일치** |
| 내부 manifest | `final-manifest.json` **349/349 일치**(파일 350 = 349 + manifest) |
| 쓰기 10건 | `execution-20261009/mutate-01..10.receipt.json` 모두 `exit_code: 0`: CreatePolicy×4 → CreateRole(closed trust) → AttachRolePolicy×4 → UpdateAssumeRolePolicy(최종 MFA trust) |
| 활성화 게이트 | `activation-gate.json` `PASS_CLOSED_READBACK`, RoleId `AROA3IOKUF7NEM6P7ZKPK`, attachments 4 / inline 0 / boundary 0 / profiles 0 / unexpected 0 / `policy_source_match` 4 |
| 승인 근거 | `authorization.json`: PR18 HEAD `5fb64bdf`, 정책·trust 원본 SHA256 7개 |
| 비밀정보 | `AKIA`/`ASIA` 키, 평문 `SecretAccessKey`·`SessionToken` 0건 |

archive 자체는 Git에 넣지 않았습니다. 하영 로컬 비공개 경로와 위 공유 폴더에 보관합니다. 저장소에는 **풀어낸 파일을 바이트 그대로** 넣었고, `final-manifest.json`으로 원본과 대조할 수 있습니다.

**한계:** 이 archive의 사용자 inventory(`before-/after-inventory`)는 2026-10-09 기준이며 **권욱·하영 2인만** 포함합니다(재환 없음, MFA 장치 목록 없음). 그래서 아래 2번으로 3인 현재 상태를 따로 수집했습니다.

## 2. 3인 IAM 사용자 상태·정책 원문 readback — `readback-original/fds-iam-readback-20261012T022246Z/`

| 항목 | 값 |
|---|---|
| 실행자 | 이하영, CloudShell 서울, caller `arn:aws:iam::774055931866:user/321team-hayeoung`(개인 IAM 사용자, root·역할 세션 아님) |
| 시각 | 2026-10-12 11:22:46 – 11:23:26 KST (`meta.txt`) |
| 수집기 | `iam-readback-3users.sh` **v3** SHA256 `75ff2479c8738b0f2e9a52ae7c4f98f6e8b4322b4a921b8d3ce26a5a307b4721`(meta 기록). v2(`8ef7bfca…`)에 리뷰 6116249967의 full-ARN 해시 키 수정만 반영. 로컬 MOCK에서 같은 이름의 AWS·고객 관리형 정책 2건 모두 수집, tar 실패 시 RC1 확인 |
| AWS CLI | `aws-cli/2.37.6` |
| 수신 | CloudShell `base64 -w 76` 출력 → 클립보드에서 직접 디코드(30,491 bytes, SHA256 `72a2016dd2594933eadc08cd7ab9c8065761c9ba389dee716a1ccffe750abc98`), gzip OK. **CloudShell 쪽 archive 해시 출력과의 대조는 하지 못했습니다**(콘솔 값 미수신). 대신 내부 `SHA256SUMS` **90/90 일치**(파일 91 = 90 + manifest) |
| 결과 | 30개 항목 모두 rc0 / OK. **DENIED·ERROR 0건** |

### 2-1. 사용자별

| 사용자 | MFA 장치 | Access Key | 직접 연결 관리형 | 사용자 inline | 그룹 |
|---|---|---|---|---|---|
| 321team-gwonuk | 1 | **0** | 0 | 0 | FDS-Human-Bootstrap |
| 321team-hayeoung | 1 | **0** | 0 | 0 | FDS-Human-Bootstrap |
| 321team-jaehwan | 1 | **0** | 0 | 0 | FDS-Human-Bootstrap |

### 2-2. 그룹 `FDS-Human-Bootstrap` 정책 — ARN ↔ 기본 버전 ↔ 원문 연결

| 정책 | 종류 | DefaultVersionId | meta 파일 | 원문 파일 (SHA256 앞 16자리) | 원문 검토 |
|---|---|---|---|---|---|
| `arn:aws:iam::aws:policy/ReadOnlyAccess` | AWS 관리형 | v190 | `policy-2a3bda39…-meta.stdout` (`af6ee2cddadc7f09`) | `policy-2a3bda39…-v190-document.stdout` (`34eaf8b1472d5aee`) | Allow 3문. `Action: "*"` 없음. AWS 관리형 읽기 전용입니다. 이름에 Get·List·Describe가 없는 항목(예: `apigateway:GET`, `codecommit:GitPull`)도 조회성입니다. 쓰기·관리 권한 아님 |
| `arn:aws:iam::774055931866:policy/FDS-Human-ReadOnly-Guard-v1` | 고객 관리형 | v1 | `policy-e9f127e3…-meta.stdout` (`8cbd61fecaa8eb18`) | `policy-e9f127e3…-v1-document.stdout` (`33c575b9fbf88676`) | summary는 `WILDCARD_ACTION_PRESENT`이지만 원문 4문 **모두 `Deny`**입니다: 승인 외 그룹원 전면 거부, MFA 없으면 bootstrap 외 거부(`BoolIfExists`), 본인 외 bootstrap 거부, 서울 밖 거부. 권한 부여 없음 |
| inline `FDS-Assume-ReadOnly-Audit-v1` | 그룹 inline | — | — | `group-…-FDS-Assume-ReadOnly-Audit-v1-document.stdout` (`a617eded8b18f86d`) | `sts:AssumeRole` on `role/FDS-ReadOnly-Audit`, MFA 조건 |
| inline `FDS-Human-Direct-ReadOnly-v1` | 그룹 inline | — | — | `group-…-FDS-Human-Direct-ReadOnly-v1-document.stdout` (`83afbb2d83f06dc4`) | 서울 EC2 Describe 일부, Audit 역할·ELB 서비스 역할 조회, `iam:ListRoles`, `aws-marketplace:ViewSubscriptions`. 모두 MFA 조건. 쓰기 없음 |
| inline `FDS-SelfService-Password-MFA` | 그룹 inline | — | — | `group-…-FDS-SelfService-Password-MFA-document.stdout` (`09fad154f0cf9c5c`) | 본인 비밀번호·MFA 관리, 본인 Access Key 목록 조회. MFA 없이 MFA 해제 거부 |

**판정 (원문 검토 기준):** 3인 모두 직접 연결 정책이 없고, 유일한 그룹의 정책 5개 원문에 관리자급 Allow(`Action: "*"` Allow, IAM·정책 변경 Allow 등)가 없습니다. 그래서 **"상시 Administrator 직접·그룹 부여 없음"으로 판단합니다.** 판단 근거는 summary 표시나 해시 일치가 아니라 위 원문 검토입니다. 독립 리뷰에서 같은 원문으로 확인해 주세요.

### 2-3. IaC 역할 `FDS-IaC-Operator` (현재 상태)
- 연결 정책 4개: State-PassRole, Vpn, Network, Guardrails. inline 0. RoleId `AROA3IOKUF7NEM6P7ZKPK`(부여 원본과 같음).
- trust: 두 Allow 모두 본인 사용자 + 본인 RoleSessionName + `aws:MultiFactorAuthPresent=true`. **처분안의 "trust MFA 조건 불변"을 2026-10-12 시점으로 확인**했습니다.
- 정책 4개의 원문은 이번 실행에서 다시 받지 않았습니다. 1번 부여 원본의 `policy_source_match 4`(PR18 원본과 일치)로 연결합니다.

### 2-4. CloudTrail 조회 가능 여부
- `cloudtrail lookup-events --max-results 1 --no-paginate`: **ALLOWED**(1건 반환, 이벤트 본문 미저장).
- 하영 사용자는 그룹의 `ReadOnlyAccess`로 CloudTrail 조회가 가능합니다. 같은 그룹인 3인 모두 같은 근거입니다. → [복구 절차 v2](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6109083724) 2번의 "CloudTrail 조회 주체" 조건 입력.

## 3. NOT_VERIFIED / 정정

| 항목 | 상태 | 이유 |
|---|---|---|
| CloudShell 쪽 readback archive 해시 대조 | NOT_VERIFIED | 콘솔 값 미수신. 내부 manifest 90/90으로 파일 무결성은 확인 |
| `FDS-ReadOnly-Audit` 역할의 권한 정책 원문 | NOT_VERIFIED | 이번 수집 범위 밖. 역할 존재·trust는 부여 원본 inventory에 있음(아래) |
| IaC 역할 정책 4개 현재 원문 | 이번 실행 미수집 | 부여 원본 `policy_source_match 4`로 연결. 부여 이후 변경 여부는 현재 attached 목록·버전 미대조 |
| noMFA RUNTIME, N5 RUNTIME | NOT_RUN / UNDETERMINED 유지 | 처분안 수용(6109083724) 그대로. 그룹 Guard의 `DenyWithoutMFAExceptBootstrap`은 사용자 측 STATIC 근거로 추가됨 |

**정정 — `FDS-ReadOnly-Audit`는 이미 존재합니다.** #9에서 하영이 "PR15 제안 단계, 미부여"라고 적었는데 사실과 다릅니다. 부여 원본 inventory(`role-FDS-ReadOnly-Audit.stdout`)에 따르면 이 역할은 **2026-10-03 생성**됐습니다(RoleId `AROA3IOKUF7NABRSEKO6P`). trust 대상은 3인 사용자 + MFA 조건이고, 그룹 inline으로 AssumeRole이 허용돼 있습니다. PR15 초안과는 별개로 먼저 있던 역할입니다. 권한 정책 원문은 위처럼 NOT_VERIFIED입니다.

## 파일
- `README.md` — 이 문서
- `grant-original/fds-approved-grant-mafyuau8/` — 부여 원본 350파일(바이트 그대로)
- `readback-original/fds-iam-readback-20261012T022246Z/` — readback 원본 91파일(바이트 그대로)
- `SHA256SUMS` — 이 폴더 전체 해시

AI 사용: CLAUDE_ASSISTED. readback 실행·편입 작성자 이하영, 부여 원본 생산자 이권욱. 둘 다 자기 승인 아님. 독립 리뷰: 이재환.
