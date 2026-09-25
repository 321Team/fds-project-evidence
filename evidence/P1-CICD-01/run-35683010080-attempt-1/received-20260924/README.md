# P1-CICD-01 — Run 35683010080/1 수신 증적 검증

수신 검증: **2026-09-24 00:20:20 KST** / 이권욱 작업의 Codex 보조 검증.
책임: [CICD #11](https://github.com/321Team/infra-cicd/issues/11), [baseline #16](https://github.com/321Team/fds-project-baseline/issues/16).

**EVIDENCE_CHECK=PASS / 원 실행 APP_WORKFLOW=BLOCK / Runtime AC 1/10 / DELIVERY_GATE=NOT_VERIFIED.**
수신 무결성과 연결 검사 결과를 등록하는 Draft 편입 자료다. 독립 증적 검토·병합·전체 인수 완료가 아니다.

## 대조 기준과 결과

| 항목 | 확인 결과 |
|---|---|
| 실제 실행 | [GitHub Run 35683010080/Attempt 1](https://github.com/321Team/infra-cicd/actions/runs/35683010080/attempts/1), Job 106603847854, cicd-runner01 |
| 원 실행 시각 | 2026-09-22 12:24:08~12:25:29 KST. 증적 수집 시각과 구분 |
| Workflow SHA | `7e939d7f77c38c13fd331b38f6649580bf0d05bd` |
| Source | `321Team/fds-msa@ec69b67067decf35abbfed0a6a99f3073132787b` |
| config 원본 SHA256 | `ea375a00811923cfb415e6c851ceed55227b5978835953eb2227b03552ab5728`, Git blob `0438f87045ff1a685385b2d2172289eafbc23138` |
| 수신 archive | 7,367 bytes, SHA256 `11578ae33211f569df91830a2b26314c01ffcaea70a67dc7165f9e3dad4b1c79`; 첨부 sidecar 일치 |
| 내부 구성 | 영수증 JSON 6개 + manifest 1개, payload 해시·크기 기록 56개. 원본 payload는 미포함 |
| 수신 검증기 | 기존 `app_evidence.py verify` exit 0; 도구 hash `644362b79e89362dd6343cd8c973951d38523f39f8625c260e29ffc199e4308f`, 고정 모듈 7개 hash 일치 |
| 결합 결과 | BINDING=COMPLETE, SOURCE_BINDING=MATCH, Run/Source/config/Handoff/Build/Scan/DB 연결 일치 |
| 추가 config 대조 | source 승인 선언·Unit/Contract 범위·requirements 4개·lock 4개 hash가 실행 당시 GitHub config와 일치 |
| 기존 요약 연결 | report hash `a9a0c6eff7961d95af7fb3a5f51093568e0ce50ab03c86859733341b0260769c`, 565,430 bytes; Scan 영수증·manifest·기존 요약 일치 |
| 취약점 | HIGH 57 + CRITICAL 3 탐지 기록, 고유 CVE 24개. 취약점 해소 아님 |
| DB | 영수증의 원 Scan 시각에 유효. 오늘 새 Scan의 DB 유효성 보장 아님 |

GitHub 원본 Job 출력의 `APP_WORKFLOW=BLOCK / ERROR_CODE=NONE / exit 10`과 수신 영수증이 일치한다. Actions 전체 conclusion은 failure이며, Scan은 `HIGH_CRITICAL_FINDINGS`로 차단됐다. 도구 실행 오류로 인한 FAIL과 구분한다.

## 시험·이미지 범위

아래 실행 여부는 제출 영수증의 명령 종료 코드와 GitHub Run을 대조한 범위다. raw pytest 로그는 미포함이므로 시험 건수·assertion 세부 재검토를 주장하지 않는다.

| 서비스 | Unit / Contract | Build | Scan |
|---|---|---|---|
| transaction-api | Unit NOT_APPLICABLE(앱 Lead의 기존 사유·승인), Contract rc 0 | build/save rc 0 | BLOCK: HIGH 57 / CRITICAL 3 |
| fds-engine | Unit rc 0 / Contract rc 0 | build/save rc 0 | NOT_SCANNED |

- transaction-api OCI manifest: `sha256:d97ff91bd7704147b1097a4c74245721811057f501a45cb29b619993521b57ed`. Build와 Scan의 archive/manifest/config/layer 식별값이 일치한다.
- fds-engine OCI manifest: `sha256:1eeaba0e0c6022cf6b65ea1f9740d8e1fe9e7b74c41aef14355f515e71afe916`. Build 증적만 있으며 Scan 통과로 표시하지 않는다.
- 위 값은 로컬 OCI manifest 식별값이다. Harbor registry manifest Digest 또는 Deployment/Pod 실행 Digest로 표시하지 않는다.
- Private Source fetch rc 0 및 Source 결합을 확인했다. 현재 Token 권한·만료 상태까지 재검사한 것은 아니다.
- Push/Deploy는 NOT_EXECUTED. 기존 Deployment 이미지 유지·실제 스캐너 오류 시 배포 차단 시험은 별도 잔여다.

## 원본과 수신 검증 파일

- `submitted/`: 수신 tar의 허용 JSON 7개를 바이트 그대로 보존. 서버 원본에 사후 판정·승인 문구를 넣지 않았다.
- `submitted-archive.sha256`: 업로드 `app-evidence.tar.gz(1).sha256`의 원문 바이트. 내부 파일명은 서버 이름 `app-evidence.tar.gz`; 업로드 archive 이름은 `app-evidence.tar(1).gz`다. 이름 차이는 전송 식별자이며 해시 불일치가 아니다.
- `cicd-findings-35683010080-1.json`: 이전 수신 원문. SHA256 `bd8a38006307e9a716826e8fa04be4d5be825548863266081c38d523b8f12f48` 일치.
- `expected.json`: 사전에 확정하고 실제 Run/config로 재확인한 외부 기준. 수신 영수증을 복사해 기준을 변경하지 않았다.
- `config-at-run.json`: 위 Workflow SHA의 GitHub 원본 바이트. 실제 운영 config를 변경하는 파일이 아닌 검토 사본이다.
- `github-metadata.json`: 조회한 Run 메타데이터 및 기존 앱 승인 댓글의 검토용 사본. 원본 URL을 함께 기록했다.
- `github-run-excerpt.log`: 실제 Job 로그의 경로·판정·종료 코드에 관한 행만 발췌. 전체 로그가 아니다.
- `receiver-verify.stdout.txt`, `.rc`: 이번 수신 측 실행 결과. 서버 collect 로그가 아니다.
- `RECEIVER_REVIEW.json`, `SHA256SUMS`: 이번 수신 검토 및 편입 파일 무결성 목록.

archive 원본은 업로드 자료 `libfile_447da44053b881919cdab259b8cdc3ef`, sidecar는 `libfile_3f207ff50dbc8191a09c094befa474df`로 보존돼 있다. [EVIDENCE_POLICY](../../../../governance/EVIDENCE_POLICY.md)의 패키지 보관 원칙에 따라 재압축·Git blob 편입·Release Asset 업로드를 하지 않았다. 독립 검토자의 원 archive 접근 인계는 별도 확인해야 한다. 위 ID는 파일 식별자이며 팀 공유 접근 완료를 뜻하지 않는다.

## 검증 한계와 인수 조건

1. `RAW_PAYLOAD_CHECK=NOT_INCLUDED_SERVER_RECORD_ONLY`. 원본 명령 로그·Source archive·OCI·Trivy report·DB 바이트는 서버에 남아 있으며 수신 측에서 재검사하지 못했다. report 원본 자체의 hash를 독립 재계산한 것으로 기록하지 않는다.
2. 이번 첨부는 archive와 sidecar다. 서버 종료 화면·collect stdout/rc·started/finished-at는 미수신이며, 별도 채널의 서버 출력 hash 대조와 정확한 collect 시각 확인은 미완료다. 원래 Run 시각으로 수집 시각을 대체하지 않는다. 서버 collect를 재실행할 필요 없이 기존 작업 폴더의 출력으로 보완할 수 있다.
3. 도구의 `SOURCE_APPROVAL=NOT_INDEPENDENTLY_VERIFIED` 출력은 그대로 보존했다. 별도 GitHub 조회로 앱 Lead 이재환의 [9/18 승인](https://github.com/321Team/infra-cicd/issues/11#issuecomment-5725640696)과 [저장소 정정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-5757298518)을 대조했다. 이것은 새 코드 리뷰나 이번 증적 PR의 독립 승인으로 간주하지 않는다.
4. 자동 token/private-key 패턴 검색과 JSON 내용 확인에서 게시 대상 비밀값을 발견하지 않았다. 이 범위의 점검을 원 서버 전체의 Secret 잔류 검사로 확대하지 않는다.
5. AC-03은 Test/Build까지만 부분 증거가 있고 두 Scan·Push·Digest 갱신·Health/E2E가 남는다. AC-05는 취약점 BLOCK 기록을 확보했으나 스캐너 오류 경로·배포 이미지 유지 검증이 남는다. AC-06은 Source→Run→로컬 이미지→Scan까지만 연결되며 Harbor→Deployment/Pod가 남는다. 기존 Runtime AC 1/10은 변경하지 않는다.

독립 검토자는 수신 원본/해시·실제 실행·판정 범위·민감정보·위 미수신 항목을 확인한다. 모든 증적 PR의 독립 리뷰 요구는 유지되며 본인/AI 검증을 독립 승인으로 기록하지 않는다.

## 후속과 복구

- 앱 Lead: FastAPI/Starlette 호환 조합·requirements·lock 4개·Dockerfile·시험·최종 승인 SHA 인계.
- CICD/공급 담당 + 앱 협의: 패치 base 후보·미패치 항목 처리안·새 OCI/wheel 공급 근거를 준비. 변경 입력은 별도 config PR 독립 리뷰 후 사용.
- 새 Run에서 두 이미지 Test→Build→Scan과 새로운 DB/영수증을 수집한다. 이번의 예상값을 새 Run에 재사용하지 않는다.
- Push/Deploy 연결 및 AC별 남은 실제 시험은 별도 작업이다. 취약점 일괄 ignore·HIGH 제외는 수행하지 않는다.
- 이번 수신 검증은 서버 명령·환경 변경·앱 재실행을 수행하지 않았다. 정정이 필요하면 원본을 보존하고 새 검토 기록으로 수정한다.
