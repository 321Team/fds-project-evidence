# P2-ROSA-01 — 창 C 하영 몫 원본: SA pull 연결·DB Secret·배포·C-STOP (2026-10-22 KST)

- 책임: [baseline#47](https://github.com/321Team/fds-project-baseline/issues/47) 창 C(하영 몫) · [infra-rosa#12](https://github.com/321Team/infra-rosa/issues/12) PR52 SA 연결 · Execution Lead 이하영
- 대상: ROSA HCP `fds-rosa-hcp` (cluster ID `2th4q1q4qf7ra35862s1u9q7f6n0vnmc`), `fds-app` namespace UID `222bf961-73d9-4743-972f-2d44da216af2`, 실행자 named `hayeoung`(`fds-app` admin)
- 실행 위치: 이하영 개인 AWS CloudShell(ap-northeast-2). 묶음은 공유 폴더(`\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트`)를 거쳐 바이트 그대로 옮겼다(2026-10-23 공유 사본 재해시 일치, 이권욱 수신 확인 [6356726338](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6356726338)).
- 재환 몫(G·W0·A2-ON/OFF·A4·녹화) `p47-windowC-20261022.tgz`는 이 폴더에 넣지 않는다(이재환 반출 [6355690272](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6355690272)).

## 결과 요약
| 단계 | 결과 | 원본 위치 | 보고 |
|---|---|---|---|
| PR52 SA pull 연결 | `LINK_PASS`, 앱 SA 2개 before/intent/after/ACK | `sa-pull-link-20261022T183115/` | [6337501483](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6337501483) · [판정 6338327553](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6338327553) |
| S DB Secret | receipt 3개(생성 1·재생성 2). **metadata·key 이름만**, 값 없음. 현재 UID `5d2e6388-3c06-4b76-b0ec-490ed262c22d` | `db-secret-receipts/` | [6339778956](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6339778956) · [6340363512](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340363512) |
| D 배포 | fds-msa `69e28c49` 렌더 `app.yaml`, Deployment·Service·Route(승인 host, Admitted True) | `c-deploy/d-20261022T204317/` | [6340066460](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340066460) |
| restart 2회 → Ready | 마지막 재시작 21:06:56 KST 뒤 API 3개 Ready | `11-restart.txt`, `12-restart2.txt` | [6340363512](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340363512) |
| C-STOP | 22:00:44~55 KST, UID test + `replicas 0`, 앱 Pod 6→0 | `14-cstop.txt` | [6341388160](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6341388160) |

## 편차 (덮지 않음)
- D는 HOLD 중 20:43:19에 실행됐다. S 재생성·restart 각 2회는 GO 발행 전 하영 책임으로 진행했다([6340172259](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340172259)).
- PR52 SA 연결은 GO 창(20:00~20:20)보다 이른 시각에 실행됐고 현 상태 유지로 수용됐다([6338327553](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6338327553)).
- 이권욱 판정: 소급 승인이 아니며 결과만 보존한다([6340597438](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340597438)). 이 편입도 소급 승인이 아니다.

## 파일
| 파일 | 크기 | SHA-256 | 내용 |
|---|---:|---|---|
| `window-c-results-20261022.tgz` | 30,480 | `5d462b33…cc16` | `sa-pull-link-…/`, `db-secret-receipts/`, `c-deploy/`(D 실행 폴더·`app.yaml`·배포 입력 `msa42-deploy-69e28c49.tgz`) |
| `window-c-results-20261022.tgz.sha256` | | | 묶음 SHA-256 sidecar |
| `SHA256SUMS` | | | 이 폴더 파일 해시 |

## 판정 범위
`SA_LINK=LINK_PASS / DB_SECRET=CREATED(값 미포함) / D=APPLIED(HOLD 중 실행) / READY=API3 / C_STOP=DONE(22:00:55)`

창 C 하영 몫 실행 증적이다. A4 E2E·A2 원복 판정은 재환 원본과 #47 보고를 따른다. 해시 일치는 무결성 확인이며 AC PASS의 단독 근거가 아니다.

## 민감정보
- **자격증명 0건:** 편입 전 압축(내부 `msa42-deploy-69e28c49.tgz` 포함)을 풀어 비밀번호·토큰·개인키·`postgres://` 접속 문자열·dockerconfigjson 값을 검사했다. 일치는 `secretKeyRef`의 **key 이름**(`DATABASE_URL`), receipt의 `KEYS=DATABASE_URL`·`DATABASE_URL_PRESENT=True`, 배포 README의 `$PW`·`base64 -d` 명령 예시, 오프라인 스키마 생성 주석(`postgresql://offline@invalid/offline`)뿐이다.
- **식별자 포함:** namespace·객체 UID, 내부 host·IP. 원본 바이트 보존 규칙에 따라 그대로 둔다.
