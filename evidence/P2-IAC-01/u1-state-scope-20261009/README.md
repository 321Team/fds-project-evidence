# P2-IAC-01 U1 N5 — state 범위 정책 readback·시뮬레이션

CODEX_ASSISTED. 이권욱 실행·분석, 독립 리뷰 전. **STATIC/SIMULATION: 범위 밖 Get/Put 허용 근거 없음. N5 실제 거부 시험은 UNDETERMINED 유지.**

## 실제 수집과 소스

- 2026-10-09 18:38:08–18:38:28 KST, 계정774055931866 / 서울 개인 CloudShell / `321team-gwonuk`.
- AWS 읽기·시뮬레이션16회 모두 rc0. 역할 전환·IAM 변경·S3 객체 쓰기/삭제·Apply·root 사용0.
- 실제 IaC role ID `AROA3IOKUF7NEM6P7ZKPK`, inline0, attached4개 모두 v1. 역할 trust 및 정책4개를 승인 HEAD `5fb64bdf186645b64664080bd09f9c5babb78fcd`의 JSON 구조와 대조하여 일치 확인. 이 HEAD의 전체 tree는 main merge `81162467bb2f99a099cb7067fbc3f63e1c0dbed8`과 동일한 것으로 기존 PR193에 수록되어 있다.
- 원본35개 manifest 일치, manifest 자체를 포함한 원본36개를 `originals/`에 byte 그대로 보존. 수신 archive SHA256 `0559453ac58544f5dc621d260e5dfa0a86cb1929b5c8e7b23aadcc25464d9786`, 10,114 bytes.
- 명령·시각·RC는 originals/execution-records.json, 실제 정책·시뮬레이터 출력은 각 stdout/stderr. receipt와 review-analysis는 파생 자료다. 해시 일치는 무결성이며 인수 또는 독립 승인과 다르다.

## N5 판정

[하영 본인 U1](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6077985000)의 없는 타 state key HeadObject 404는 거부 시험 결과를 확정하지 못한다. [AWS HeadObject 문서](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html)는 객체 부재 시 ListBucket 권한에 따라 404 또는403이 반환된다고 설명한다. 따라서 404를 GetObject 허용 또는 IAM 실패로 단정하지 않는다. 하영 원본 archive는 이번 자료에 수신되지 않았으므로 그 실행에 대한 독립 원본 리뷰 완료도 아니다.

실제 역할의 현재 identity 정책에 대한 `SimulatePrincipalPolicy` 결과:

| exact key | GetObject | PutObject |
|---|---|---|
| phase2/network/terraform.tfstate | allowed | allowed |
| phase2/u1-other/terraform.tfstate | implicitDeny | implicitDeny |

region=ap-northeast-2, SecureTransport=true, PrincipalArn=IaC 역할을 입력했다. 이 입력은 시뮬레이션 조건이며 해당 API 실호출 성공/거부가 아니다. 실제 S3 Put/Get payload 시험0.

**파싱 주의:** AWS 응답은 두 resource를 합친 상위 EvalDecision=implicitDeny와 실제 key별 ResourceSpecificResults를 함께 반환한다. 원본 summary.json은 상위 값을 보존한 간략 출력이므로 exact key 판정에 쓰지 않는다. 위 표와 review-analysis.json은 원본 ResourceSpecificResults에서 추출했다.

범위 밖 결과에는 MissingContextValues14개가 남아 있다. 이를 완전한 모든 조건 시뮬레이션 PASS로 표시하지 않는다. 현재 정책4개를 정적으로 확인하면, Get/Put Action 및 해당 타 key Resource에 동시에 맞는 Allow statement는 조건 평가 전부터0개다. 누락값은 EC2/tag/KMS/PassRole 조건 및 ListBucket의 s3:prefix에 해당하며 이 타 key에 대한 Get/Put Allow를 만들 수 없다. 검토 범위는 수집한 실제4정책·trust 및 아래 직접 버킷 접근이다.

## 버킷 정책과 시뮬레이터의 한계

- GetBucketPolicy 원문은 Deny4개만 포함하고 Allow0개다. 광범위한 bucket-policy Allow로 타 key 접근을 추가 부여한 근거가 없다.
- BucketOwnerEnforced로 ACL 비활성, public-access block4항목 true.
- [AWS SimulatePrincipalPolicy 문서](https://docs.aws.amazon.com/IAM/latest/APIReference/API_SimulatePrincipalPolicy.html)는 IAM role에 대한 resource-based policy simulation을 지원하지 않는다고 명시한다. 따라서 버킷 정책을 identity 정책처럼 합치거나, 다른 IAM user를 CallerArn으로 넣어 역할 전체 권한 검증으로 표시하지 않았다.
- 실제 버킷 정책은 별도 STATIC readback으로 확인했다. 위 allowed는 **identity 정책 시뮬레이션**이며 bucket-policy/SCP/RCP/session 등 모든 실제 평가 계층을 포함한 런타임 성공 보장이 아니다. 다른 endpoint/access point 또는 향후 정책 변경에도 이 판정을 확장하지 않는다.

## N2/noMFA·root 기록 경계

- MFA로 로그인한 CloudShell에서 새 OTP 인자를 생략한 AssumeRole 성공은 noMFA 거부 시험이 아니다. N2는 INFO, noMFA RUNTIME NOT_RUN으로 둔다.
- 실제 trust 두 Allow는 각각 지정된 사용자 ARN, 본인 session name, Bool aws:MultiFactorAuthPresent=true 조건을 모두 요구한다. false/absent에서 이 두 Allow가 매칭되지 않는 것은 STATIC 근거다. 이 자료는 STS trust의 시뮬레이션 또는 실제 noMFA 거부를 수행했다고 주장하지 않는다. 시험을 위해 장기키 발급·MFA 해제하지 않았다.
- 초기 부여 시 root 로그아웃의 정확한 시각은 수집 자료에 기록되지 않았다. 17:33:46 KST의 첫 개인 사용자 caller 증거는 그 시각의 개인 계정 사용 근거이며, 정확한 root 로그아웃 시각이나 모든 root 세션 종료의 증명이 아니다. 추정 시각을 사후 기입하지 않는다.
- root는 교육장 소유로 팀이 MFA를 관리할 수 없다는 기존 합의를 유지한다. 일상 작업은 개인 계정/배정 역할, root는 구체적인 특수 변경 범위가 별도로 승인된 경우로 제한한다.

## 후속과 승인 경계

1. 독립 리뷰어가 본 자료를 검토한 뒤 N5의 정책 범위 우려와 RUNTIME 미판정을 구분하여 수용 여부를 기록한다. 이 PR은 #9/AC4 전체 완료·티켓 종결이 아니다.
2. 하영 본인 시험 원본 제출과 U1 잔여 I2/I3/I5, 권욱 I3/I5 및 남은 안전한 I4 검증을 이어간다. 잠금 fixture는 실행자 간 작업창 확인 후 exact network .tflock에서만 수행한다. 현재 NOT_RUN.
3. PR193은 18:28:52 KST merge `b6aa39383c55ae877bb4044b4cd6efb9037d7845`로 편입됐다. 재환 독립 승인은 증적 편입 범위이며 비공개 전체 Plan의 Apply 승인으로 확대하지 않는다. Apply 전 전체 saved plan 별도 검토가 남는다.
4. [ROSA A1/A3 의견](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6077911578)은 현재 Guardrails readback에서도 근거가 확인된다. 글로벌 IAM/Marketplace 동작은 서울 밖 Deny 예외목록4개 밖에 있어 후속 정책만 추가해도 차단될 수 있다. 향후 exact A1/A3 소스가 확정되면 Guardrails를 포함한 us-east-1 조건 검증과 최소 예외 리뷰가 필요하다. 이번에는 ROSA 후보 전체 시뮬레이션·IAM 변경·Marketplace Subscribe를 실행하지 않았다.

Phase1 AC, 정본, 비용 결정권, Stage-A/ROSA 생성 GO는 변경하지 않는다. 이권욱이 직접 수집·작성했으므로 자기 검토는 독립 승인이 아니다.
