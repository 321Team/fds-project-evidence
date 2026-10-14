# AC05 과거 실패 원본 회수와 잔여 증적 — 2026-10-14

CODEX_ASSISTED · 이권욱. 판정은 **PARTIAL**이다. 실제 취약점 차단과 스캐너 실행 오류의 원본을 회수했지만, 각 실패 당시 배포 이미지가 유지됐다는 관측 원본은 이번 조사에서 확보하지 못했다. 이번 작업은 기존 파일의 읽기·복사·해시 대조이며 **신규 Runtime·재스캔·Push·Deploy는 수행하지 않았다.**

## 기준과 조사 범위

- 기준 시점: 2026-10-14 13:58 KST. 파일별 서버 수집 시작·종료는 `runs/<run>/COLLECTION_METADATA.json`, SSH 호출·수신 시각은 `collection/receipt.json`에 보존했다. 서로 다른 호스트의 시계를 섞어 소요 시간을 계산하지 않는다.
- AC 정본: [baseline `768e5da` P1-CICD-01](https://github.com/321Team/fds-project-baseline/blob/768e5da817c1b96ae847a9efe11e729f3d73c789/tickets/live/descriptions/P1-CICD-01.md). AC05는 **“취약점 Gate 실패와 스캐너 실행 오류를 각각 실패 처리하며 배포 이미지가 유지된다.”**이다. [조회 당시 사본](references/P1-CICD-01.live-at-audit.md)을 포함했다.
- Evidence 조사 기준: main `89f9d4cbd3ff77aa6fc70cfe3de34a71ffb09758`. P1-CICD-01의 추적 JSON 중 8 MiB 이하 938개를 파싱해 최상위 `IMAGE_SCAN=BLOCK/FAIL` 원본을 검색했다. 기존 BLOCK receipt 1건을 찾았다. [검색 범위와 경로](TRACKED_RECEIPT_SEARCH.json). 다른 비공개 채널·미추적 압축파일까지 전수 확인했다는 뜻은 아니다.
- CICD 현재 코드 비교 기준: main `b183fddb9c65e7119bf008214c34bef3ca4066d2`. 기존 Unit-negative 승인 이후 추가분은 Phase 2 문서·도구이며 P1 스캐너 변경은 없다. [현재 스캐너 사본](references/scanner-at-current-main.py), [오류 회차 스캐너 사본](references/scanner-at-error-run.py)을 구분했다.
- 기존 [PR222](https://github.com/321Team/fds-project-evidence/pull/222)는 10:36:49 KST 병합 완료다(merge `cfee8cad50ffc8efc63dc797e9ba84932a583a1d`). Unit-negative 증적 편입이며 AC04 최종 인수나 이번 AC05 승인을 뜻하지 않는다. [조회 원본](references/pr222.json).

## 회수 결과

모든 회차는 Attempt 1이다. 아래 시각은 원본 receipt의 UTC를 KST로 변환한 값이며, 현재의 재실행 결과가 아니다.

| 과거 Run / 실제 실행 시각(KST) | 확인한 결과 | 적용 범위와 한계 |
|---|---|---|
| [35047422631](https://github.com/321Team/infra-cicd/actions/runs/35047422631), 9/16 11:17:47~11:17:55 | 파일시스템 fixture HIGH 15 / CRITICAL 6, rc10. 빈 DB 실오류 rc1, toolcheck PASS | 앱 이미지 파이프라인이 아닌 Trivy 도구 시험. 배포 전후 이미지 없음 |
| [35050018964](https://github.com/321Team/infra-cicd/actions/runs/35050018964), 9/16 11:58:40~11:58:44 | 동일 유형의 rc10·빈 DB rc1, toolcheck PASS | 앞 회차와 별도 실행이나 AC05 앱 인수 두 건으로 세지 않음 |
| [35588577241](https://github.com/321Team/infra-cicd/actions/runs/35588577241), 9/21 19:24:40~19:25:37 | `APP_WORKFLOW=FAIL`, `SCANNER_EXECUTION_ERROR`, 실제 scanner rc1, GitHub FAILURE | Test/Build 후 transaction-api Scan 실패. Push/Deploy `NOT_EXECUTED`. 배포 전후 이미지 없음 |
| [35683010080](https://github.com/321Team/infra-cicd/actions/runs/35683010080), 9/22 12:24:08~12:25:29 | `APP_WORKFLOW=BLOCK`, `HIGH_CRITICAL_FINDINGS`, HIGH 57 / CRITICAL 3, 실제 scanner rc10, GitHub FAILURE | transaction-api에서 차단. fds-engine `NOT_SCANNED`. Push/Deploy `NOT_EXECUTED`. 배포 전후 이미지 없음 |

원본 텍스트·receipt **148개**(11 + 11 + 63 + 63)를 바이트 그대로 복사했다. 각 원본 Manifest에 포함된 **35개 항목**(11 + 11 + 6 + 7)은 수신 파일 또는 서버에서 직접 계산한 해시와 일치했다. 기존 Run35683010080 편입 Manifest의 **payload 56개 전체**도 이번 서버 읽기에서 대조했고, 기존 제출 JSON 6개는 Git에 편입된 바이트와 동일했다. 상세 결과는 [AUDIT_RESULT.json](AUDIT_RESULT.json)과 회차별 `MANIFEST_VERIFICATION.json`이다.

대용량 OCI/source archive·Trivy DB·원본 report는 복사하지 않고 서버의 잔존 원본을 읽어 SHA-256을 계산했다. `COLLECTION_METADATA.json`의 `hash_only`와 별도 [scan archive 보완](collection-history/scan-archive-supplement/stdout.json)에 경로·크기·해시가 있다. **원본 전체를 Git에 보관했다는 뜻이 아니다.** 로컬 재검증은 복사한 148개를 다시 해시 계산하고, hash-only 항목은 수집 기록과 기존 receipt를 대조한다. 서버의 현재 바이트를 다시 읽는 것은 별도 수집이다.

Run35683010080 원본 report의 서버 재계산 해시는 `a9a0c6eff7961d95af7fb3a5f51093568e0ce50ab03c86859733341b0260769c`이다. `REPORT_ALLOWLIST_SUMMARY.json`은 그 파일에서 CVE·패키지·심각도 필드만 추린 **파생 자료**이며 receipt의 57/3과 일치한다. 이미지 설정·환경·원본 report는 편입하지 않았다. 이 수치는 과거 DB 기준으로, 현재 앱의 취약점 판정이 아니다.

## 해결한 공백과 남은 공백

1. **해결:** GitHub Actions의 과거 로그 다운로드는 네 회차 모두 현재 HTTP 410이지만, Runner에 남은 실제 파일을 직접 회수해 오류/차단 receipt와 로그 연결을 보완했다. 빈 `github/run.log`는 다운로드 실패 결과이며 성공 로그로 해석하지 않는다. metadata/jobs 및 다운로드 종료 코드·오류도 보존했다.
2. **해결:** Run35683010080의 과거 아카이브 접근 공백은 이미 [ARCHIVE_ADDED_20260924.md](../run-35683010080-attempt-1/received-20260924/ARCHIVE_ADDED_20260924.md)에서 보완됐다. [PR22](https://github.com/321Team/fds-project-evidence/pull/22)도 병합된 상태다. 옛 README의 대기 문구를 현재 차단사항으로 재사용하지 않는다. 이번에는 아카이브 내부 목록에만 있던 payload의 서버 해시까지 대조했다.
3. **잔여:** 취약점 실패와 스캐너 오류 **각각의 당시 Deployment/Pod 전후 이미지 관측은 `NOT_COLLECTED`**다. Push/Deploy 미호출은 앱 이미지 유지 실측과 구분한다. Unit-negative의 관측이나 현재 Kubernetes 조회를 과거 실패의 전후 증거로 대신하지 않는다.
4. **잔여:** 과거 앱 스캐너 어댑터는 stdout/stderr를 `DEVNULL`로 보냈으므로 fatal stderr는 **`NOT_RETAINED_BY_ADAPTER`**다. 당시 코드가 OCI archive를 직접 `--input`으로 넘겼고 이후 layout 입력으로 수정된 사실은 확인되지만, 보존되지 않은 stderr의 실제 문구나 원인을 이번 회수만으로 재구성하지 않는다. rc1과 실패 전파는 원본으로 확인했다.
5. **범위 유지:** 두 앱 이미지 중 transaction-api에서 중단됐다. fds-engine 결과를 PASS로 채우지 않는다. 두 앱 실행에서는 Build/save가 이미 수행됐으므로 “이미지 생성 없음”으로 기록하지 않는다. 과거 collect 종료 코드 미기록도 새 수집의 rc0으로 소급 보완하지 않는다.

따라서 AC05를 체크하거나 P1-CICD-01을 Done으로 변경하지 않는다. 후속은 [NEXT_CASES.md](NEXT_CASES.md)의 두 실패 유형 시험 준비이며, 코드·입력 검토와 새 실행 범위 확정 전에는 실행하지 않는다.

## 수집 방법과 검증 재현

- 실행 대상/계정: `cicd-runner01` / `server01_cicd-runner` UID1000. Windows → `fds-ansible01` → Runner의 기존 SSH 경로. `sudo`, 새 토큰, 서비스·설정 변경 없이 고정된 4개 기존 결과 디렉터리만 읽었다.
- 각 `collection/collector.py`가 실제 실행 소스다. `receipt.json`에 소스 SHA-256, 명령 인자, 실행·수신 시각, rc, stdout/stderr 해시를 보존했다. 분류는 `PURE_READ_PRECHECK`, **`REVIEW=NOT PERFORMED (Pre-check)`**다. 이번 증적 편입 독립 리뷰는 별도 대기다.
- 파일 유형·소유자·symlink·크기·읽기 전후 inode/mtime/size를 검사한 뒤 복사 또는 해시 계산했다. 최초 앱 회차 수집은 1 GiB 상한 때문에 중단했다. 실제 DB 크기(약 1.41/1.43 GB)를 읽기 전용으로 확인한 뒤 상한을 2 GiB로 제한해 재수집했다. 첫 실패 소스·오류·rc도 `collection-history/`에 보존했으며 서버 파일/권한은 변경하지 않았다.
- 수신 base64와 전체 SSH stdout은 승인된 작업 PC의 `deliverables/p1-cicd-ac05-audit-20261014/`에 보존했다. Git에는 디코딩한 원본과 필요한 메타데이터를 편입한다. 전체 stdout은 Git에 없으므로 그 transport 해시를 Git 사본만으로 재현할 수는 없다.

저장소 루트에서 Python 3 표준 라이브러리만으로 실행한다. 운영 서버·네트워크 접근과 파일 쓰기는 없다.

```text
python -B evidence/P1-CICD-01/ac05-history-20261014/verify.py
python -B tools/check-evidence-layout.py --base origin/main
```

정상 기준은 복사 원본 148개, 기존 payload 참조 56개 및 receipt 연결의 대조 성공이다. 불일치 시 검증은 nonzero로 종료하며 원본을 고치거나 누락 값을 생성하지 않는다. 조회·파일 무결성 PASS는 신규 Runtime 성공, 독립 리뷰, AC 최종 인수로 확대하지 않는다.
