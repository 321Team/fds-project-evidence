# DEC-P2-REG-01 — infra-rosa#12 창 B cold-pull·Apply 원본 (2026-10-22 KST)

- 책임: [infra-rosa#12](https://github.com/321Team/infra-rosa/issues/12) (DEC-P2-REG-01 Sub-task 4/4, Pull Route/TLS/Credential Test) · Execution Lead 이하영
- 대상: ROSA HCP `fds-rosa-hcp` (cluster ID `2th4q1q4qf7ra35862s1u9q7f6n0vnmc`), `fds-app` namespace, On-Prem Harbor `10.1.93.54`
- 경로: VPN_RUN `20261022T1500`(`FDS_HARBOR=on`, 이재환), route `10.1.93.0/24 → eni-0017c49242017af9b`, Relay SG `sg-0f1e8a5dbecabccee` TCP 443·5432
- 실행 위치: 이하영 개인 AWS CloudShell(ap-northeast-2). 묶음은 CloudShell에서 만든 뒤 팀 공유 폴더(`\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트`)를 거쳐 바이트 그대로 옮겼다(재압축 없음, 2026-10-23 공유 사본 재해시 일치).
- 시작 기록: [6334082290](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6334082290) · 종료 보고: [6336767294](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6336767294) · 이권욱 원본 검토: [6337348436](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6337348436)

## 결과 요약
| 단계 | 결과 | 원본 | 보고 |
|---|---|---|---|
| ⑤~⑦ saved Plan Apply 1회 | `Apply complete! Resources: 3 added, 0 changed, 0 destroyed.` — `sgr-0676480144d0cc693`(443), `sgr-08dac1aa3eff391a5`(5432), `r-rtb-01e3140bb2a0b3bb62517319121`, readback 충족 | `window-b-apply-20261022T163622.tgz` | [6335511367](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6335511367) |
| ⑧ 앱1 after 61 (1차) | STOP — P1 timeout, 원인 MTU 블랙홀 | 결과 묶음 `coldpull-path-after-…-xd6FA2` | [6335539066](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6335539066) · [진단 6335653365](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6335653365) |
| MSS 클램핑 | 이권욱 1회 GO → 이재환 vpn-gw01 MSS 1360 2규칙 | (infra-vpn, 이 묶음 밖) | [GO 6336181470](https://github.com/321Team/fds-project-baseline/issues/37#issuecomment-6336181470) |
| ⑧ after 61 (재개) | transaction-api `aKZfn4` PASS, fds-engine `bGuG1n` PASS (+ 의도치 않은 중복 `h0vivg` PASS) | 결과 묶음 | [6336603565](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6336603565) |
| ⑧ 62 transaction-api `Bi6z4q` | A1·A2 거부, C1 cold, C2-DL·C3 OK / **C2-RUN FAIL**(`DATABASE_URL` 미설정, exit 1) | 결과 묶음 | [6336627527](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6336627527) |
| ⑧ 62 fds-engine `SJ8fym` | PASS (A1·A2 거부, C1 cold, C2-DL·C2-RUN·C3 OK) | 결과 묶음 | [6336767294](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6336767294) |
| 정리 | 창 B NP UID `038d645c-7316-4e9b-823d-538764f86c25` 삭제, 키트 임시 객체 0, 임시 cluster-admin 회수 17:49:21 KST 확인 | 결과 묶음 `np-b` | 위 종료 보고 |

## 파일
| 파일 | 크기 | SHA-256 | 내용 |
|---|---:|---|---|
| `window-b-coldpull-results-20261022.tgz` | 279,798 | `2c2987f1…1249` | 키트 RUN 11개(precheck 3·before 2·after 4·pull 2, STOP·중복 포함) + `np-b` |
| `window-b-apply-20261022T163622.tgz` | 2,436 | `1cbad46f…34da` | Apply 직전 확인·init·Apply·readback |
| `*.tgz.sha256` | | | 묶음 SHA-256 sidecar |
| `SHA256SUMS` | | | 이 폴더 파일 해시 |

## 편입하지 않은 원본 (비공개 경로 유지)
saved Plan·state 계열은 비공개 경로만 사용한다([이권욱 6335225449](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6335225449)). 해시만 기록한다.

| 원본 | SHA-256 | 비고 |
|---|---|---|
| `window-b-plan-harbor-window-20261022T155320.tgz` | `63ad5d742bcada4fc95144eefa39ece73a3628431ed8778a3b798a475ee8831a` | 1차 STOP(assume-role MFA 코드 무효, Plan 미생성) |
| `window-b-plan-harbor-window-20261022T160232.tgz` | `f206511218f3bdb2135ba15beb7e2ac987fe01da21f25e8a3adcf544526ba211` | 2차 PASS, saved Plan `d7004262d512b4c63b5bfa01c7b6a098df8416474f12bf0ba3ebc738316aa5f2` |

## 판정 범위
`APPLY=PASS(3 added) / AFTER61=PASS(api,engine) / PULL_ENGINE=PASS / PULL_API=DL_PASS_RUN_FAIL(DATABASE_URL) / CLUSTER_ADMIN=REVOKED`

창 B 실행 증적이다. transaction-api 기동은 창 C(#47)에서 확인했다. 해시 일치는 무결성 확인이며 시험 PASS의 단독 근거가 아니다. DEC-P2-REG-01·P2-ROSA-01 전체 AC 완료나 티켓 종결이 아니다.

## 민감정보
- **자격증명 0건:** 편입 전 압축을 풀어 `password|token|dockerconfigjson|PRIVATE KEY|DATABASE_URL|postgres://|aws_secret|authorization:` 패턴을 검사했다. 일치는 `automountServiceAccountToken: false`, EC2 `http_tokens: required`, Secret **type 이름**뿐이다.
- `coldpull-pull-*/secret-a2.json`(A2 "틀린 인증" 시험용)은 키트가 만든 무작위 값이다. 디코드 결과 사용자 `robot$fds-coldpull-wrong`, 비밀번호 `not-a-credential-…`(33자)로 실제 자격이 아님을 확인했다. 정상 pull Secret 값과 P2 Robot secret은 들어 있지 않다.
- **식별자 포함:** AWS 계정 ID·IAM ARN·내부 노드 호스트명·Secret/객체 UID. 이 저장소의 기존 P2 증적과 같은 수준이며 원본 바이트 보존 규칙에 따라 그대로 둔다.
