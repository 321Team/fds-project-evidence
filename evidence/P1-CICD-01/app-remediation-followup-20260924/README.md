# P1-CICD-01 앱 후보 CI·base 진단 원본 — 2026-09-24

**최종 판정: CI=PASS / BASE_SCAN_ACCEPTANCE=BLOCKED_EVIDENCE_INTEGRITY.**

- 책임: [CICD #11](https://github.com/321Team/infra-cicd/issues/11), [앱 PR7](https://github.com/321Team/fds-msa/pull/7).
- 앱 최신 HEAD: `44efdc6a84af0ff63e574786093b71d4b8fdd105`. 기존 후보 f5ba3bf에서 Workflow·lock checker/시험·인계 문서4개 delta. 앱 코드/lock/Dockerfile/공급 바이트 동일.
- 실제 [Source CI35919225150/1, Job107378589806](https://github.com/321Team/fds-msa/actions/runs/35919225150): 명시적 HEAD checkout, hash lock 다운로드·오프라인 설치·pip check2/2, lock 검사8+API14+engine26=48PASS. 실제 이미지 Build/Scan CI가 아니다.
- 수행 위치: Codex Linux x86_64 작업 공간, 로컬 root 프로세스. cicd-runner01/운영 서버 실행이나 새 운영 권한 사용이 아니다.

## 관측·무결성 문제·판정

고정 Trivy0.74.0 프로젝트 binary SHA 일치 후 공개 공식 DB와 base OCI를 로컬로 조회·스캔했다.
최초 및 새 DB 재확인 보고 원문에는 trixie HIGH44/CRITICAL0, bookworm HIGH55/CRITICAL5가 기록됐다.
그러나 DB 사후 해시가 결과 기록과 달라 공식 비교 검증으로 수용하지 않는다. ASSESSMENT.json을 최종 판정으로 읽는다.

| 원문 | 상태·한계 |
|---|---|
| base-scan/result.json | 최초 BLOCK 원문. DB의 현재 바이트는 최초 기록 hash와 불일치 |
| bookworm-scan-summary.log | 최초 DB 재사용 전 hash 불일치로 중단한 traceback. 이 회차 bookworm Scan은 미실행 |
| paired-rescan/result.json | 새 DB로 두 base를 재확인한 원문. COMPARISON_COMPLETE는 실행기 내부 기록이며 사후 무결성 수용이 아니다 |
| checksum-replay/ | 두 번째 DB의 사본과 원본이 시스템 sha256sum/Python streaming에서 c15fd665…로 일치. 해당 사본의 trixie 재사용은 bbolt Page.FastCheck SIGSEGV, exit2로 중단. 이후 bookworm 미실행 |
| ASSESSMENT.json | 사후 해시 불일치·원인 UNKNOWN·추가 검사 중단·최종 수용 보류 |

기록 DB hash779370a7…와 사후8cf4c7e1…/c15fd665…의 차이를 보존한다. 기존 결과 원문의 해시나 완료 문구를 사후 수정하지 않았다. 보고서 config digest·diff ID/report hash 대조만으로 전체 무결성이나 취약점 해소를 확정하지 않는다.

**권고:** 앱 의존성·CI 코드 리뷰를 진행하되 base 교체/예외/운영 승격은 보류한다. 안정된 DB 바이트를 확인할 수 있는 승인된 격리 환경에서 실제 base/app Build·Scan을 재검증한다. Codex에서 발생한 현상을 기존 Runner의 장애로 일반화하지 않는다.

## 보존 범위

- Git 편입 대상은 위 텍스트 원문·선택한 registry JSON·판정·실행 driver 사본·SHA256SUMS다. source-ci.log는 GitHub Job에서 수신한 원문이다.
- drivers/는 실제 사용한 로컬 진단 코드의 원본이며 독립 리뷰/운영 적용 승인이 없다. 아카이브 배치 그대로 실행하는 Runbook이 아니다. 여기의 상대 작업 경로는 당시 로컬 경로다.
- DB 본체·Trivy binary·OCI는 Git에 편입하지 않는다. binary/OCI는 고정 공개 출처 및 hash로 추적한다. 진단에 사용한 DB 사본은 사용자 전달 후속 ZIP에 별도 보존하며 승인된 공급 DB로 사용하지 않는다.
- 내부 SHA256SUMS는 텍스트 편입 파일을 다시 계산한 목록이다. 새로운 byte 대조를 과거 DB 무결성 복구 또는 Runtime AC로 표시하지 않는다.
- 원문 시각은 UTC/로그 KST를 구분한다. 원 앱 Run35683010080/1·기존 증적 PR22와 이번 Codex 후보 검사를 혼합하지 않는다.

증적 Draft / 독립 심사·병합 대기. APP BLOCK·Runtime AC1/10·Delivery NOT_VERIFIED 유지. 서버·Runner·운영 config·권한·Push/Deploy·정본 발행 변경 없음.
