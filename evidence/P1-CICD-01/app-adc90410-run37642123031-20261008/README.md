# adc90410 앱 Test / Build / Scan 실제 회차

CODEX_ASSISTED. 2026-10-08 KST. Run37642123031/attempt1, Job112863570663. Workflow main `4e9324cd8acf0ba67b35f950b4c952db8064540e`, source `adc90410f99cb7af5b40bc8ff92c45272e9f8bee`.

## 결과

- GitHub Actions SUCCESS(00:05:22 생성, 00:06:57 최종 갱신). 실제 앱 기록 00:05:32.237~00:06:46.628.
- APP_WORKFLOW / BUILD_SCAN / 두 이미지 IMAGE_SCAN PASS. engine Unit16, transaction-api Contract14, engine Contract10 통과. API Unit은 승인된 NOT_APPLICABLE이며 PASS를 만들어 넣지 않았다.
- 두 이미지 HIGH0/CRITICAL0, 새 DB 다운로드00:06:39. 이전 Scan 결과를 재사용하지 않았다. DB UpdatedAt/NextUpdate는 원 metadata에 보존.
- image archive/config/manifest identity, Source/Workflow/config/Run/Attempt는 SUMMARY.json과 수집 archive에서 추적한다. Push/Deploy/Harbor manifest/Pod imageID/전체 Delivery 인수는 미수행이다.

## 원본과 수집 검증

Runner 기존 정상 계정 UID1000, 공급125파일 해시/권한, 공간, 중복 프로세스·lock 및 fresh Harbor TLS 확인 후 사용자가 허용한 시험 종료 후 창에서 한 회차 실행했다. start-record.md는 실행 전 계획이고 actual receipt/GitHub 시각은 별도다. 다음 SEC Probe는10/8 14시, Backup HOLD 기록을 확인했다. 앞선 HBR 자동기동 FAIL과 수동 복구를 구분했다.

원본 경로 `/home/server01_cicd-runner/FDS_CICD_AppWorkflow._6zedcc5`의 raw 로그·source·OCI·DB·Trivy report는 서버에 보존한다. 검토된 실행 checkout의 `tools/delivery/app_evidence.py collect`가 해당 원본 바이트와 receipt 연결을 검증했다: EVIDENCE_CHECK=PASS, BINDING=COMPLETE, RAW_PAYLOAD_CHECK=LOCAL_BYTES.

원 수집 archive `/home/server01_cicd-runner/app-evidence-37642123031-8ymlnocd/collection/app-evidence.tar.gz`, SHA256 `d0762a96741f69ac0fab14f116bdd84b95330d5eb9fe65889ad96853df47b6b4`. 재압축 없이 수신·sidecar 대조했고 내부 receipt6개+manifest1개다. 이 archive에는 승인된 수집기 whitelist JSON과 원본 hash/size 목록만 있으며 raw logs/images/DB/reports 자체는 없다.

수신 측 ansible01에서 같은 source의 verifier로 EVIDENCE_CHECK=PASS/BINDING=COMPLETE/SOURCE_BINDING=MATCH를 확인했다. RAW_PAYLOAD_CHECK=NOT_INCLUDED_SERVER_RECORD_ONLY: 수신 단계가 생략된 raw 원본을 직접 다시 읽었다는 뜻은 아니다. SOURCE_APPROVAL=NOT_INDEPENDENTLY_VERIFIED는 도구의 범위이고 실제 APP 승인 및 PR64 독립 승인은 연결 이슈에서 별도 확인한다.

첫 수신 verify는 relative archive/expected 경로를 써 절대경로 Gate에서 rc1이었다. 원본·도구 변경 없이 절대경로로 수정한 호출이 rc0이었다. 첫 실패 stdout/stderr/receipt를 보존했고 성공 호출은 도구 transcript 관측으로 `receiver-verify-absolute-observation.json`에 명시했다. 이를 native stdout 파일로 가장하지 않는다.

## 종료·잔여

- 00:11 앱 실행 프로세스 없음, workflow lock 미점유, 기본 Podman 컨테이너[] 확인.
- 00:12 이번 Run 전용 VFS store의 컨테이너[] 확인. 장기 Runner ID2 online/idle 재확인.
- 원본/이미지 store는 증적·후속 Push를 위해 의도적으로 보존했다. workspace/store 전체 삭제·prune나 공급 토큰 발급을 하지 않았다. Run별 종료와 보존 정책을 구분한다.
- 수집/점검 wrapper는 로컬 운용 명령 기록이며 새 Runtime source 승인으로 주장하지 않는다. 실제 증적 검증기는 기존 reviewed main의 코드다.
- PR 독립 증적 리뷰/편입 병합과 AC 인수는 별도 단계다. 본 문서의 PASS는 지정 Source의 해당 Test/Build/Scan 회차에 한정한다.

재검증: Python3.11+ Linux에서 위 main의 app_evidence.py verify에 archive·expected.json의 **절대경로**와 위 archive SHA를 지정한다. 실패하면 원본을 보존하고 입력/연결 오류를 확인하며 재시험으로 덮지 않는다. `SHA256SUMS`는 자신을 제외한 이 폴더 파일을, 최상위 REGISTRY_SHA256SUMS는 이 manifest를 결속한다.
