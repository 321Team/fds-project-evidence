# P1-CICD-01 — affbc69 후보 오프라인 공급물

CODEX_ASSISTED · 이권욱 · 2026-10-09 KST. **격리 CI 공급 생성·로컬 수신 검증 완료 / APP Source 승인 PENDING / 현장 전송·Test/Build/Scan·Push·Deploy 미실행.**

기존 [APP27](https://github.com/321Team/fds-msa/pull/27)의 후보 TCP/Scan [증적178](https://github.com/321Team/fds-project-evidence/pull/178)은 공급 archives가 없는 검사 결과다. 이번에는 기존 공급 workflow로 같은 후보 Source의 실제 공급 bytes를 새로 생성했다. [CICD70](https://github.com/321Team/infra-cicd/pull/70) 인계 준비를 보완한다.

## 고정 식별과 보관

| 항목 | 값 |
|---|---|
| APP source | affbc69beef9967f7977d09a6fec14f7fb6c0e94 (리뷰 대기) |
| 공급 tool/workflow | main 8eac4c982076e3c219840a13686b15c46879981f |
| Run/Attempt | [37859961937 / 1](https://github.com/321Team/fds-msa/actions/runs/37859961937), SUCCESS |
| 공급 artifact | [11585741989](https://github.com/321Team/fds-msa/actions/runs/37859961937/artifacts/11585741989), 109,786,915 bytes |
| 원 ZIP SHA256 | 2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd |
| SUPPLY_MANIFEST SHA256 | 6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4 |
| 진단 artifact | 11585507417, 22,125 bytes; receipt.json에 원 ZIP hash |
| API 표기 만료 | 2026-10-16 08:32:03 KST (두 artifact 동일) |
| 로컬 수신 완료 | 2026-10-09 08:34:12 KST |

공급 ZIP은 Git에 넣지 않고 원래 bytes 그대로 실행자 비공개 로컬 `phase1-work-20261009/private/app-supply-37859961937/supply.zip`에 보존했다. 원격 공유 업로드·Release 발행은 없다. artifact는 위 만료 이후 받을 수 없으므로 담당자 인계/장기 보관 위치 결정이 남아 있다. 로컬 사본 존재를 다른 담당자의 수신 완료로 표시하지 않는다. 재압축하지 않은 ZIP의 수신 크기·SHA256이 GitHub API metadata와 일치한다.

## 실제 검증 범위

- GitHub hosted Ubuntu에서 잠긴 builder/runtime 베이스를 각2회 빌드해 byte 대조, runtime UID/GID10001:999 smoke, runtime/test wheels4종 수집, SUPPLY_MANIFEST 및 SHA256SUMS를 생성했다. 앱 이미지 재빌드·새 취약점 Scan 회차는 아니다.
- 로컬: ZIP CRC·중복/경로/link·파일집합, 내부 manifest **125/125** 일치(ZIP 전체126파일, SHA256SUMS 포함), Source Git blob **12/12** 일치(requirements8·apko입력4).
- 베이스2종의 Docker-load archive manifest/index/config/platform·압축 계층 digest·비압축 diff_ids와 SUPPLY_MANIFEST identities를 대조했다. 이 digest들은 Harbor remote manifest나 Pod imageID가 아니다.
- wheels 합계106개는 **프로필별 중복을 포함한 파일 수**: engine runtime20/test28, API runtime27/test31. 각 wheel bytes/hash·내부 Name/Version·inventory·lock·roots를 대조했다. 로컬 pip install·의존성 재해결·이미지 load는 하지 않았다.
- drift 진단 원본9파일/해시와 원 ZIP을 대조했다. workflow의 실제 build 단계는 `DRIFT_NOT_BLOCKING`, age41시간/기존3일 한도 이내다. 도구 단위시험의 모의 age 출력과 실제 build 출력은 구분한다. upstream과 다르다는 사실은 남기고 lock·날짜를 갱신하지 않았다. 실제 사용 시 freshness는 다시 판단한다.
- `run.log`는 gh로 회수한 실제 회차 로그이며 공급 생성 실패를 숨기거나 다시 실행한 회차가 없다. `VALIDATION.json`의 SHA·범위, `ARCHIVE_CONTENT_INDEX.json`의 원 ZIP 내부 항목을 함께 추적한다. 원 ZIP 자체는 이 Git manifest 범위 밖이다.

## 재검증·승인 경계

원 ZIP을 확보한 뒤 `python3 verify_supply_affbc69.py supply.zip RECHECK.json`을 실행한다(Python3.11+ 및 gh의 정확한 Source 읽기 권한 필요). 이 검증기는 기존 adc90410 artifact 검사기를 이번 source/tool/artifact 값으로 고정한 로컬 검사기이며 독립 리뷰 전이다. GitHub main 공급 도구와 이 검사기의 승인을 혼동하지 않는다. source,tool SHA가 이번에는 서로 다르며 각 역할을 따로 검증했다.

Workflow step 이름의 `approved application source`는 실제 APP 승인 증거가 아니다. APP27은 리뷰 대기이고 `delivery_authorization=false`를 유지했다. Source/Unit 범위 확정 전 `materialize_app_build_scan_v3.py`를 실행하거나 APPROVED 설정·승인자/참조를 만들지 않았다. 활성 config는 기존 Source를 유지한다.

다음 순서: APP Lead의 최종Source/51개 시험 매핑/API Unit 처분 확정 → 이 공급 bytes와 supply tool 승인 연결 → 정상 Runner 전달 및 consumer config 준비/독립 리뷰 → fresh 선행조건·회차 GO 확인 후 현장 실행. 후보 HEAD·lock/requirements/tool이 바뀌면 이번 공급과 영향 범위를 다시 대조한다. 별도 공급원본·과거승인·artifact ID를 복사해 새 승인을 만들지 않는다. 리뷰는 작업창 종료 후 이재환님께 요청한다.

## 추가 consumer 호환성 검증

[consumer-check](consumer-check/README.md)에08:44 정상 Linux 계정에서 실제 consumer stage/verify/source 검증과 잘못된 입력3건 거부 결과를 추가했다.08:45 전용 임시270파일을 검증 후 정리했다. 이는 전체 APP config나 실제 Runner 실행 검증이 아니다. 최초 공급 수신 원본은 변경하지 않았다.

## Runner 읽기 전용 보완

[runner-readonly](runner-readonly/README.md)에08:51~52 정상계정·도구·공간·기존공급 manifest·main입력 관측을 추가했다. Trivy 최초조회 한도초과는 원본에 남기고 해당파일만 후속 hash대조했다. 실행Gate/등록/DB신선도/새공급전달은 미확인 상태를 유지한다.
