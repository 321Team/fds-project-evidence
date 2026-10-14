# AC05 실제 두 실패 회차와 배포 이미지 유지 — 2026-10-14

CODEX_ASSISTED · CICD Lead 이권욱. **두 실제 실패 유형과 회차별 Deployment/Pod 이미지 유지 관측을 확보했다. 증적 편입 독립 리뷰·AC05 범위 수용은 대기**다. 두 GitHub Run은 의도대로 FAILURE로 보존하며 성공 Pipeline·전체 Delivery로 표시하지 않는다.

## 실제 결과

| 회차 / Run / Job (Attempt1) | 실제 프로그램 실행(KST) | 관측한 실패 | 전후 배포 상태 |
|---|---|---|---|
| [vulnerability / 38553120620](https://github.com/321Team/infra-cicd/actions/runs/38553120620), Job115815618445 | 19:57:04~19:57:15 | fresh DB·transaction-api 실제 rc10, HIGH61/CRITICAL3, BLOCK, 상위rc1/GitHub FAILURE | Deployment2·Pod6 `OBSERVED_UNCHANGED` |
| [scanner-error / 38553393207](https://github.com/321Team/infra-cicd/actions/runs/38553393207), Job115816526113 | 19:59:29~19:59:30 | 새 빈 DB cache·실제 Trivy rc1, DB 누락 원문369B, SCANNER_EXECUTION_ERROR, 상위rc1/GitHub FAILURE | Deployment2·Pod6 `OBSERVED_UNCHANGED` |

각 `cases/<case>/VERIFIED.json`, `raw/result.json`, `raw/scan/result.json`, `github-run.json`, `github-jobs.json`, `actions.log`를 연결했다. 원본의 초 이하 시각은 JSON을 따른다. 프로그램과 GitHub Job의 시작·종료는 다른 경계다.

두 회차 모두 `EXPECTED_FAILURE_OBSERVED`, **Push/Deploy NOT_EXECUTED**, Test/Build NOT_EXECUTED_FIXED_HISTORICAL_IMAGES다. transaction-api 첫 Scan에서 중단돼 **fds-engine은 NOT_SCANNED**다. 이 Workflow에는 downstream Push/Deploy Job이 없으므로 실제 `skipped` Job 증적이라고 주장하지 않는다. Attempt2는 조건에서 skip될 수 있으며 이번에는 재실행하지 않았다.

## 기준·승인·비중첩

- AC05: “취약점 Gate 실패와 스캐너 실행 오류를 각각 실패 처리하며 배포 이미지가 유지된다.” [정본 사본](references/P1-CICD-01.md). 이전 [evidence PR227](https://github.com/321Team/fds-project-evidence/pull/227)의 과거 rc10/rc1 원본은 유효하지만 당시 전후 관측 누락은 그대로 보존한다. 이번은 별도 새 두 회차다.
- [CICD PR81](https://github.com/321Team/infra-cicd/pull/81)의 HEAD `884c3d99ba865d0e08f58951dbd750cb4e8589c6`에 [이하영 독립 APPROVED](https://github.com/321Team/infra-cicd/pull/81#pullrequestreview-5514019754). merge `65ae4fd3b274efc04c3cb686b41cc99fb07383b8`를 실제 두 Run 모두 사용했다. reviewed HEAD와 대상 코드 diff0. PR CI38522275424/main CI38529245862 SUCCESS, 각692건·smoke 동일성 PASS. CI의 MOCK을 실제 스캔 증적으로 쓰지 않는다.
- 사용자 “착수” 및 두 새 회차/비중첩 질문에 “권장 순으로 조정하고 각 세션에 인계”를 반영했다. 최신 순서는 **H4 종료·회수 → PR83 CI·host 회수 → AC05**다. 코드 리뷰를 Runtime 승인으로 확대하지 않으며 기존 소진 회차를 재사용하지 않았다. 정본 Lead 실행 권한과 사용자 의사를 연결한 기록은 `coordination/EXECUTION_AUTHORITY.json`이다.
- H4 재회차 결과/수집 완료는 기존 담당 세션의 `H4_EVIDENCE_VERIFICATION.json`과 PR83 인계로 확인했다. H4 전체 원본을 이번 PR에서 재심사한 것은 아니다. PR83의 19:53 `WINDOW_RELEASE.json`·CI/회수 결과 사본 및 fresh API/Runner 읽기를 확인하고 시작했다. 기존 수집기 준비 중 순서 정정 이력과 실제 dispatch를 구분한다.
- 20:00:56 KST 최종 API active/queued0·Runner idle, 직전 서버 읽기 Worker0/Trivy0, 고정 입력3해시 일치. 원본 회수 후 공유 창 해제를 양쪽 세션에 전달했다. `WINDOW_RELEASE.json`. 이후 이 세션은 로컬/GitHub 편입 작업만 수행한다.

## 입력·관측·원본

실행 계정은 `cicd-runner01`의 정상 `server01_cicd-runner` UID1000이다. 별도 sudo/새 credential 공급·이미지 load/run·서비스/보안 통제 변경은 없었다. 과거 Source `ec69b67067decf35abbfed0a6a99f3073132787b`의 실제 앱 OCI2개를 해시로 고정해 새 private 경로로 복사했다. 현재 앱 Source의 Build를 재실행한 시험은 아니다.

- transaction-api archive93,404,160B / `218c57b0613dc37e9628745d3ae580886543902714bbb9ab6249b5ac90d1266f`.
- fds-engine archive74,496,512B / `a8895e245ea2a2f30aa106524bf858020fccc65a12fc543d26f3c09a87f04d1c`.
- root 소유0755 Trivy0.74.0 / `d89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791`.
- vulnerability의 새 DB download rc0·metadata 순서/NextUpdate·DB/report hash 검증. 과거57/3을 강제하지 않았고 이번 DB에서는61/3이었다. 이는 **과거 고정 이미지**의 현재 DB 스캔 결과다.
- scanner-error는 별도 새 빈 캐시에서 실제 `--skip-db-update cannot be specified on the first run`을 확인했다. stderr SHA256 `0a84a92039f60bcf86eb033600a1fa7597e0f37bdea3da3b549bc96fada18131`, rc1, report/DB 미생성. 다른 오류·timeout·예상 밖 rc0은 통과 조건이 아니다.

관측은 `k8s-control01`에서 기존 `svc_ansible`/`sudo -n`으로 고정 fds-app GET4개(Deployment/Pod/Service/EndpointSlice)만 수행했다. 수집기 해시는 검토된 PR81/merge 바이트와 같다. 실제 호출 argv·source/stdout/stderr SHA256·계정·시각·rc를 회차별 before/after 폴더에 보존했다. stdout은 필드 선별 JSON이며 raw API 전체 payload를 Git에 편입한 것은 아니다.

승인된 comparator가 확인한 동일성 범위는 **Deployment2개 UID/generation/spec hash/digest/replicas/Ready와 Pod6개 UID/owner/node/imageID/containerID/Ready/restartCount**다. 각 앱 Ready3, 회차 전후 관측은 시작/종료에서 각각5분 이내다. 수집된 Service/EndpointSlice의 동일성까지 comparator가 입증한다고 확대하지 않는다. `resourceVersion` 변화는 비교에서 제외된다. 실행 전부터 있던 일부 Pod restartCount1도 그대로 유지됐으며 0으로 바꾸어 기록하지 않았다.

원본 텍스트21개(11+10, claim2개 포함)를 바이트 그대로 수신했다. root Manifest 전체56항목(30+26)은 **서버의 실제 잔존 파일을 재해시**했고 nested Manifest·result/report/DB 연결도 일치했다. `cases/*/original-collection/stdout.json`은 base64 수신 원문, `raw/`는 동일 바이트 디코딩본, `original-index.json`은 조회 메타데이터/허용 필드 report 요약이다.

**대용량 OCI·DB·이미지 layout·원본 report는 hash-only**이며 Git에 전체 원본이 있다는 뜻은 아니다. Runner private 폴더 `FDS_CICD_ScanNegative.v9c5md84`와 `FDS_CICD_ScanNegative.5yuif6qp`, 두 claim을 보존했다. 기존 입력·cache·claim 삭제나 Podman prune은 하지 않았다. 보고서 요약은 CVE/패키지/심각도 허용 필드만 추린 파생 자료다. 자격증명·개인키·실제 token 값은 편입하지 않는다.

## 검증 재현과 한계

저장소 루트에서 Python3 표준 라이브러리만으로 실행한다. 서버/네트워크 접근·파일 수정 없이 수신 사본을 검증한다.

```text
python -B evidence/P1-CICD-01/ac05-runtime-20261014/verify.py
python -B tools/check-evidence-layout.py --base origin/main
```

정상 출력은 원본21개·root Manifest56항목 참조·각 회차 expected failure·Deployment2/Pod6 유지 대조 통과다. hash-only 항목의 **로컬 검증은 수집 당시 서버 해시 기록을 대조**하며 서버의 현재 바이트를 다시 읽는 것은 아니다. `SHA256SUMS`는 편입 사본의 현재 무결성 목록이고 서버 원본 Manifest와 구분한다.

Runner readiness/원본 읽기 도구와 SSH transport는 **PURE_READ_PRECHECK / REVIEW=NOT PERFORMED (Pre-check)**다. 승인된 app 수집기에도 재사용 transport 영수증의 일반 `review` 필드가 이 값을 갖지만, app 소스 자체는 검토된 merge의 byte/hash와 별도 대조했다(`references/CODE_BINDING.json`). Runtime harness와 스캐너 변경은 PR81의 독립 코드 검토 대상이다. 이 PR의 편입 독립 리뷰는 별도다.

최초 로컬 dispatch 사전검사에서는 수신 직후 서버 시각이 Windows보다 약1초 앞서 freshness 하한에 걸렸다. **dispatch-intent/API POST 전에 종료**했고, 수 초 뒤 동일 조건 검사 통과 후 case당 실제 POST1회만 수행했다. 서버 시각·검증 한계를 수정하거나 Runtime을 재시도하지 않았다.

AC05의 두 실패/이미지 유지에 대응하는 증거는 확보했다. 다만 고정 과거 앱 이미지·공유 어댑터 시험이라는 적용 범위를 독립 증적 리뷰와 Lead 인수에서 확인해야 한다. AC04/AC07/08/09·최종 Delivery/E2E·Phase1 전체 완료를 자동으로 선언하지 않고 **기존 AC 체크·Status In Progress/OPEN을 유지**한다.
