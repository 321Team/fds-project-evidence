# PR7 GitHub 호스팅 후보 Build/Scan 결과 — 2026-09-24 KST

**Source CI59 PASS / 두 Build PASS / API HIGH44·CRITICAL0 BLOCK / engine NOT_SCANNED.**

- [앱 PR7](https://github.com/321Team/fds-msa/pull/7), Source `bbe349c8815ed2ade3de87a1b312221c34f4361b`.
- [Run35921580081/1](https://github.com/321Team/fds-msa/actions/runs/35921580081): 전체 failure. 이는 API Scan exit10 차단 결과이며, validate Job107386565765는 success다. candidate-images Job107386743984의 후속 독립 hash 검사 및 원본 upload step은 success다.
- 격리 실행 시작/종료: 2026-09-23 21:18~21:20 UTC, 09-24 06:18~06:20 KST. 구체적 시각은 원문 로그/result 참조.
- 책임: CICD 이권욱 사용자 후속 “착수” 및 중앙 REVIEW_AUTHORITY_POLICY §4의 병합 전 후보 CI·격리 시험. 앱 Lead 이재환·Support 이하영 역할 유지. 작성자 검증이며 독립 승인 아님.
- 기존44efdc6 대비4파일 delta, 누적18파일, 원격80blob/mode 일치. 19개 도구 판정/lock 시험 + API14 + engine26 =59 PASS. 실제 DB/E2E 시험 아님.
- 기존 base digest·runtime lock에서 Docker Buildx linux/amd64 두 이미지를 실제로 빌드했다. 설치 RUN은 network=none. 운영 Podman/공급 수신 검증과 다르다.
- API scan: HIGH44·CRITICAL0, 고유CVE8. report hash `621f420c0f70cca9d8c3919e39c38abe69472bd5c735303b1ebdeddeea0b2ef1`은 실행 결과에 기록된 값이다. 첫 BLOCK에 따라 engine 스캔과 Push/Deploy는 수행하지 않았다.

## DB 무결성 확인 범위

새 DB SHA256 `dd1fd09d5d7ff9cfe0ad84e827f052bb43fee1d7655a6399aa26306448991464`, metadata `6af7ed5a7cc43e6ead1b0febce043e6606e43ab2b8ee04e3df8b521d9e3259e2`. UpdatedAt2026-09-23T20:20:57.734988316Z, DownloadedAt21:19:26.501791Z. Python streaming/시스템 sha256sum 및 scan 전후, driver 종료 후 별도 step의 내부42파일·DB2파일 재검사는 Runner에서 PASS했다. 이전 Codex DB 오류의 원인은 여전히 UNKNOWN이다. 다른 DB 회차 결과로 과거 기록을 덮어쓰거나 수치를 단순 차감해 해소 CVE 수로 계산하지 않는다.

## 원본 접근과 수신 제한

- [GitHub 원본 artifact10777267517](https://github.com/321Team/fds-msa/actions/runs/35921580081/artifacts/10777267517): 278,490,138bytes, ZIP SHA256 `22c0952ccafa9dc5d65506f821e5c125179d9bd4b7bcbfcd193dda36d5415eb8` (GitHub API/Job 기록).
- 포함: 두 Docker image archives·실제 DB·metadata·report·result·명령/로그·SHA256SUMS 등43파일이라는 upload 기록. 이 검토 묶음에는 원본 ZIP의 payload가 들어있지 않다.
- Workflow retention 요청은14일이나 저장소 상한7일로 실제 적용됐다. 원본 expires_at2026-09-30T21:18:11Z (=10-01 06:18:11 KST). 저장소 정책 변경 없음.
- 원본 ZIP의 Codex 수신 시 HTTP403, 정식 materialize 전송 시 HTTP502 두 차례 발생. **RAW_ARCHIVE=NOT_RECEIVED / RECEIVER_HASH_VERIFICATION=NOT_PERFORMED.** 원본 전체 바이트·Trivy report 본문을 수신 검증했다고 주장하지 않는다.
- source-ci.log/image-ci.log는 GitHub Job 원문. result-extracted-from-job-log.json은 로그 안 JSON을 추출한 파생본이며 artifact의 result.json 원본 수신본으로 표시하지 않는다.
- package/type/CVE별 후속 분류는 원본 report를 읽은 뒤 확정해야 한다. 고유CVE8/카운트와 report identity 검사는 Runner 결과로 확인됐다.

## 다음 조치

1. 최신 앱 HEAD 독립 코드 리뷰와 앱 Lead 최종 Source/시험 범위 인계. PR은 Draft·미병합 유지.
2. 원본 artifact를 만료 전에 내려받아 외부 ZIP hash 및 내부 SHA256SUMS, DB_SHA256SUMS를 수신 측에서 검증한다. 성공 시 실제 report의 패키지별 원인/수정 버전을 분류해 base·의존성 조치를 선택한다. HIGH/CRITICAL 예외는 자동 채택하지 않는다.
3. 승인된 패치 후보가 준비되면 새 DB/Run으로 재검증. 현재 BLOCK을 유지하며 같은 실패 후보를 이유 없이 반복 실행하지 않는다.
4. on-prem Podman·최종 Source/공급 경로·CICD config 인계/독립 리뷰·실제 Delivery는 별도 잔여다.

**APP BLOCK / Runtime AC1/10 / Delivery NOT_VERIFIED 유지.** 서버·Runner·권한·운영 config 변경, Push/Deploy·병합·정본 발행은 없음. 기존 운영 Run35683010080/1과 증적 PR22, 이전 Codex 오류 원문은 그대로 보존한다.
