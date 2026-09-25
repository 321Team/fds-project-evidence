# P1-CICD-01 — 기존 collect 로그·시각 보완 수신

수신 검증: **2026-09-24 04:59:08 KST** / 이권욱 작업의 Codex 보조 검증.
대상: Run35683010080 / Attempt1. [이전 수신 기록](../received-20260924/README.md)의 누락 항목을 새 기록으로 보완한다.
책임: [CICD #11](https://github.com/321Team/infra-cicd/issues/11), [baseline #16](https://github.com/321Team/fds-project-baseline/issues/16).

**보완 수신 대조 PASS / 원 앱 BLOCK / Runtime AC1/10 / Delivery NOT_VERIFIED.**
이전 원문·수신 검토 기록18개를 보존한다. 이번 수신은 앱 재실행·스캔 재수행·독립 증적 승인이나 전체 Delivery 인수가 아니다.

## 수신·연결 결과

| 항목 | 확인 결과 |
|---|---|
| 제출 archive | `collect-record.tar.gz`, 1,204bytes, SHA256 `58ed389299582dc6d69d5d19c94d08c82df730c27c5a693b54408d0cca61b758` |
| 외부·내부 무결성 | 제출 sidecar 일치. 일반 파일5개, 중복·링크·경로 이탈 없음. 내부 SHA256SUMS **4/4**, 기록의 원본3파일 size/hash **3/3** 일치 |
| 수집기·신원 기록 | `cicd-runner01 / server01_cicd-runner / UID1000`, `COLLECTED`, 누락 목록0. 신원은 제출 기록이며 새 원격 인증 점검이 아님 |
| 수집기 Source | [infra-cicd PR34](https://github.com/321Team/infra-cicd/pull/34), merge `4258d0879b186296fc4a4f5a7f06a4818d11bef0`; 코드 SHA256 `87868f5baab72288ccfc4de3f1a42341e3d29f219b230d8b29f754897813a265`와 일치 |
| 원 수집 회차 | `CICD_Evidence35683010080_1.qtYnYi`, AUTO_SINGLE_MATCH. collect.log의 archive 경로·hash와 보완 record 연결 일치 |
| 기존 app-evidence | SHA256 `11578ae33211f569df91830a2b26314c01ffcaea70a67dc7165f9e3dad4b1c79`, 이전 수신 검토의 archive 값과 일치. 이번 첨부에는 해당 archive 바이트가 없음 |
| 원 collect 시각 | **2026-09-23 23:59:24~23:59:30 KST**, 기록 간격6초 |
| 보완 기록 생성 시각 | **2026-09-24 04:55:11.104906 KST**. 원 앱 실행·원 collect·수신 검증 시각과 구분 |
| 서버 collect stdout | EVIDENCE_CHECK=PASS / RAW_PAYLOAD_CHECK=LOCAL_BYTES / BINDING=COMPLETE / SOURCE_BINDING=MATCH / RECORDED_APP_WORKFLOW=BLOCK |
| 과거 collect 종료코드·화면 | NOT_RECORDED / NOT_INCLUDED 유지. 새 보완 수집기 종료코드도 별도 화면으로 제공되지 않음 |

보완 기록의 원본3파일에 기존 수집기의 순수 `validate_record()` 규칙을 적용했다. 수집기 `collect()`나 `main()`, 앱 및 서버 명령은 호출하지 않았다.
시각은 원 앱 종료 → 원 collect 시작/종료 → 최초 수신 검증 → 이번 보완 생성 → 이번 수신 검증 순서로 일치한다.

## 해소 범위와 남은 한계

1. **해소:** 기존 collect.log·started-at.txt·finished-at.txt 미수신, 정확한 collect 시각 미확인, 서버 로그의 출력 archive hash 미확보.
2. 서버 stdout의 7개 결과 중 RAW_PAYLOAD_CHECK를 제외한 **6개 값이 기존 수신 verify 결과와 동일**하다. 서버는 LOCAL_BYTES, 수신 측은 NOT_INCLUDED_SERVER_RECORD_ONLY이며 서로 다른 검사 범위를 뜻한다.
3. 서버가 원본 바이트 검사 PASS로 기록한 로그를 확보한 것이다. 원 앱 로그·OCI·report·DB 바이트를 이번에 수신해 독립 재해시한 것은 아니다. 수신 측 RAW_PAYLOAD_CHECK를 LOCAL_BYTES로 올리지 않는다.
4. 파일 무결성·일관성 검증은 서버 실행 진위의 독립 증명이나 소급 승인과 구분한다. 과거 collect의 명시적 rc·종료 화면은 미수신 그대로다. 새 명령으로 과거 rc를 재생성하지 않는다.
5. 수집기 Source 분류는 **REVIEW=NOT PERFORMED (Pre-check)**다. 증적 PR의 독립 검토 의무는 [EVIDENCE_POLICY](../../../../governance/EVIDENCE_POLICY.md)에 따라 별도로 유지한다.
6. 원 app-evidence와 이번 collect-record archive의 **독립 검토자 접근 인계는 미확인**이다. 기존 첨부 원본을 그대로 보존하며 재압축·Git 바이너리 편입·Release Asset 업로드·공유 권한 변경을 하지 않았다.
7. transaction-api HIGH57/CRITICAL3 BLOCK, fds-engine NOT_SCANNED, Push/Deploy NOT_EXECUTED 및 Runtime AC1/10을 유지한다. 기존 기록의 부분 증거를 확장한 것이며 새 Scan 결과는 없다.

## 파일 구성·정정 방식

- `submitted/`: 제출 archive의5파일을 원문 바이트 그대로 보존. 그 안의 SHA256SUMS는 서버 보완 묶음의 목록이다.
- `submitted-archive.sha256`: 첨부 sidecar 원문 바이트.
- `RECEIVER_REVIEW.json`: 이번 수신 대조 결과·원본3파일 판정·시간 구분·제한.
- 이 README와 루트 `SHA256SUMS`: 이번 편입 기록이며 과거 서버 생성물로 표시하지 않는다.
- 제출 file ID: archive `file_00000000ede0820bb665493b02ac02db`, sidecar `file_00000000cc68820b9a6f7b3407269a65`. 식별자는 팀 접근 완료의 근거가 아니다.

STATIC/수신 검증 완료, 새 MOCK/앱 RUNTIME 미실행. CI는 실제 check-run 조회로 별도 기록하고 0건을 PASS로 표시하지 않는다. 독립 REVIEW·MERGE·Release는 PENDING이다.
정정이 필요하면 원문을 보존하고 후속 기록으로 보완한다. 서버 변경이 없어 서버 원복은 필요 없다. 원 collect 및 앱을 이 누락 보완 목적으로 다시 실행할 필요는 없다.
