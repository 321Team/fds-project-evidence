# P2-IAC-01 network 실제 Plan — 2026-10-09

CODEX_ASSISTED. 실행자 이권욱, 개인 321team-gwonuk MFA → FDS-IaC-Operator.
**PLAN_CAPTURED_REVIEW_REQUIRED / APPLY NOT_RUN / 전체 U1·Stage-A 인수 미완료.**

## 실제 실행

- 2026-10-09 17:57:05–17:57:57 KST, 서울 개인 CloudShell.
- Terraform 1.16.4 linux_amd64. 공식 ZIP SHA256 dc94af0eef1147718ad7c8daea792ed199e3e0492eec180d0adafa2a65a879df 대조.
- provider hashicorp/aws 6.66.0, 검토된 lock + init -lockfile=readonly. 설치 로그의 HashiCorp signature 확인.
- 실제 source HEAD 5fb64bdf186645b64664080bd09f9c5babb78fcd(PR18 승인 HEAD).
- 현재 main 81162467bb2f99a099cb7067fbc3f63e1c0dbed8과 전체 Git tree 4a166c32b28ceb32b6fa47e8cfb8a48a1b556e19가 동일하다.
- CloudShell에 GitHub 인증을 저장하지 않고 로컬 Git bundle을 전달했다. bundle SHA256 977d7980ad24cd5c6722e304deba261c99bfc205e8ebe322f515ed5ca002bc2d.
- sparse checkout 범위 terraform/network. 실제 사용 6파일은 해당 commit blob 원문 byte와 일치, 실행 전 status clean.
- backend: fds-tfstate-774055931866-ap-northeast-2 / phase2/network/terraform.tfstate / default workspace / native S3 lock.
- 명시 입력 execution_enabled=true는 이번 Plan 회차에만 사용. 소스 기본값 false 유지. credential은 환경에서만 전달하고 파일에 저장하지 않았다.
- 원래 공통 사용자/역할 정책 변경0, root 사용0. Apply/VPC/NAT/EC2/ROSA 생성0.

## 결과와 기술 검토 범위

| 항목 | 결과 |
|---|---|
| fmt / init / workspace / validate | rc0, default, valid=true |
| 실제 Plan | rc2, create20 / update0 / delete0 |
| Plan 바이너리 SHA256 | 18b65922fc358fca901e05e5d890b0605851ed58d1c455161e2c8c9e9dabfc40 |
| 자원 구성 | VPC1, Subnet4, IGW1, RouteTable4, Association4, Route4, NAT1, NAT용 EIP1 |
| 실제 AZ lookup / VPC precondition | PASS |
| Subnet 생성 후 postcondition | unknown — Apply 후 실제 생성 시 검증할 항목, 현재 PASS 아님 |
| 현재 state/lock 객체 | 실행 전후 exact prefix 목록 모두 빈 결과 |
| 잠금 이력 | 17:57:44 생성(304 bytes), 17:57:50 삭제 표식 생성, 현재 lock 없음 |
| 전체 U1 / 업무 AC | 미완료 |

검토된 범위: VPC10.20.0.0/16, 서브넷4개의 CIDR/zone ID, 자동 공인IP=false, 서울, 프로젝트 소유 태그, public NAT1+EIP1 및 private 기본 route3, transport IGW route1. 실제 생성이 없으므로 값이 아직 unknown인 자원 ID를 actual handoff로 사용하지 않는다. VPN/On-Prem route, Relay, SSM 문서, Harbor SG, probe는 이 network Plan에 없다. Private b/c의 az1 NAT 경유는 기존 단일 NAT 설계이며 후속 비용 판단은 권욱/교육장 리포트 기준이다.

잠금 객체의 과거 version1개와 현재 DeleteMarker1개가 S3 version history에 남아 있다. 현재 lock 부재와 과거 버전 영구삭제를 구분하며, 버전 삭제·force-unlock은 하지 않았다. Metadata 관측은 당시 해당 key의 생성/삭제 이력이고 CloudTrail caller attribution의 대체물이 아니다. Plan 출력·시각과 연결해 정상 native lock lifecycle을 확인했다.

## 수신·무결성·제외

원본 archive 25,460 bytes:
6b1ef479633624f06fb9c66f372852a041815b680ea776ca86db78cd04442935

개인 CloudShell 파일을 기존 UI 읽기 경로로 분할 읽고 로컬에 동일 바이트로 보관했다. 원격/로컬 archive SHA 및 원본 manifest60/60·파일 집합 일치. hash는 무결성 검증이고 기술 승인 또는 인수 증명이 아니다.

선택 원본 목록은 receipt.json에 있다. stdout/stderr와 실행 argv/RC/시각을 보존했다. assume-role.stdout의 Credentials는 수집 시 제거한 응답이며 원래 credential 응답을 공개·저장하지 않았다. 이 회차 wrapper는 이권욱의 실행 보조 도구로, 별도 독립 코드 리뷰 완료로 표시하지 않는다.

전체 network.tfplan, 전체 Plan JSON/text 및 state 정보는 Git에 편입하지 않는다. private 원본은 실행자 CloudShell과 로컬 private-evidence에 보존한다. plan-review-projection.json은 허용 목록으로 추출한 **파생 검토 자료**이며 전체 Plan 원문이 아니다. 독립 리뷰어가 전체 Plan까지 확인할 때에는 기존 승인된 비공개 전달 경로로 별도 제공하고, 이 projection 확인만으로 전체 원문 검토 완료를 표시하지 않는다. 신설 공유 권한이나 credential 전달은 하지 않는다.

이 PR의 SHA256SUMS는 편입된 선택 사본·파생 자료의 해시이며 원격 원본 manifest와 구분한다. 원격 source/버전/명령 등은 execution-summary/source-receipt/receipt에 연결한다.

## 실행 준비 중 발견한 비차단 재현성 항목

전체 checkout에서 validation/relay-agent-rpm-20261008 아래 download.json, terraform/capture-manifest.json, terraform/summary.json이 변경으로 표시됐다. index 원본 CRLF와 *.json eol=lf 속성이 충돌하는 상태를 확인했다. 원본 증적 byte를 변경하지 않았으며 network 6파일의 clean sparse checkout과 blob byte 대조로 실행 범위를 고정했다. 별도 소스 저장소에서 해당 증적 경로의 -text 보존 예외를 검토할 수 있다. 이번 Plan 소스 변경이나 새 Runtime 차단으로 확대하지 않는다.

## AC·잔여·독립성

- AC1 fmt/validate 실제 수행 근거 확보.
- AC2의 Plan 산출·변경 내용 점검까지 확보. **독립 리뷰된 승인 Plan 및 Apply 일치 판정은 미완료**.
- AC4 중 역할·credential 경계·native lock 정상 생성/해제의 일부 증거. state Put, lock 경쟁 거부, 오류 복구, noMFA 실제 거부는 미실행.
- 하영의 본인 MFA 역할 시험을 이권욱 결과로 대체하지 않는다.
- 재환 Network 역할 결속, network Apply 후 실제 handoff, vpn Plan·Apply·Runtime은 별도.
- 이권욱이 실행·자료 작성에 참여했으므로 자기 검토를 독립 승인으로 표시하지 않는다. 독립 검토 후 편입하며 이 PR만으로 #35/#9/#10 종결·Apply GO·Phase1 인수조건을 변경하지 않는다.
- source/input/state나 실행조건이 바뀌면 기존 saved plan 재사용을 전제하지 않는다.

근거: [PR18](https://github.com/321Team/infra-terraform/pull/18), [개인 MFA 시험](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6077501470), [보관 해소/후속](https://github.com/321Team/fds-project-baseline/issues/35#issuecomment-6077608415), [SEC root 예외와 Plan 선행조건](https://github.com/321Team/infra-terraform/issues/9#issuecomment-6077299965).
