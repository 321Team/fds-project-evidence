# P1-HBR-01 — HBR Lead Runtime 증적 편입 (2026-09-30 ~ 2026-10-02)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 수집·실행: 이하영(HBR Lead). 원본 전사·정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다(추가 증적은 새 회차 폴더).

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. 이 편입은 AC PASS 선언이 아니다. 아래 "AC 대응"의 범위만 해당한다.

## 파일 목록

| 파일 | 내용 | 대응 AC | 수집 시각 / 수행 | 출처 |
|---|---|---|---|---|
| `harbor-tls-restore-post-20260930T172323.txt` (+`.sha256`) | TLS 복구 후 재검증(Leaf 발급자, SAN, Verify 0, health, Trivy, 컨테이너 healthy) | AC-01 | 2026-09-30 17:23:23 KST / 이권욱 | harbor01 |
| `runner-podman-trust-20261001T170012.txt` (+`.sha256`) | Runner Podman CA trust: 배치한 `ca.crt` SHA256 `20ddfa5e…053f` 일치, 틀린 계정 로그인이 TLS 통과 후 인증 거부(rc=125) | AC-02 선행 | 2026-10-01 17:00:12 KST / 이하영 | cicd-runner01 |
| `base-digest-precheck-20261002T153016.txt` | 승인 후보였던 `alpine@sha256:c053b592…4214` pull: `manifest unknown`, rc=125 | AC-02 선행 | 2026-10-02 15:30:16 KST / 이하영 | cicd-runner01 |
| `base-digest-precheck-c64c-20261002T153119.txt` | `alpine@sha256:c64c687c…3b5e` pull: rc=0(config `bf8527eb…`). #13 승인 코멘트 5946864064로 c053 superseded / c64c approved | AC-02 선행 | 2026-10-02 15:31:19 KST / 이하영 | cicd-runner01 |
| `base-digest-precheck.sha256` | 위 두 파일의 sidecar | - | - | - |
| `if09-formal-run-20261002T161052/` | **IF-09 Runner 정식 시험(공식 Run)** 결과 폴더 6개 파일: `run.log`, `summary.txt`, `review-run.env`(+`.sha256`), `runner-push-test.sh`, `SHA256SUMS` | AC-02 | 2026-10-02 16:10~16:11 KST / 이하영 | cicd-runner01 `~/hbr-review-run-hbr-20261002-161052-d57ab5dc` |
| `harbor-robot-accounts-list-20261001.png` | Robot 계정 목록, 만료 시각, 권한 범위 | AC-06(중간 상태) | 파일 시각 2026-10-01 15:26 KST / 이하영 | Harbor UI |
| `harbor-robot-worker-edit-basic-20261001.png` | `robot$worker` 기본 정보(만료 30일, 10/16 17:02). 저장하지 않고 닫음 | AC-06(중간 상태) | 2026-10-01 15:29 KST | Harbor UI |
| `harbor-robot-worker-edit-project-perm-20261001.png` | `robot$worker` 권한(`fds` 한정 1권한, `library` 0) | AC-06(중간 상태) | 2026-10-01 15:33 KST | Harbor UI |
| `harbor-robot-screenshots.sha256` | 위 3개 화면 캡처의 sidecar | - | - | - |

## AC-02 정식 시험 요약 (공식 Run)

- Run ID `hbr-20261002-161052-d57ab5dc`, TEST_TAG `ifup-20261002T071118Z`, Harbor manifest `sha256:7a3b263c938493c827d8295e64f23d9386ffcbea75516ea03a6b65196636bfc6`
- 결과: login 성공, `10.1.93.54/fds/test:ifup-20261002T071118Z` push 성공, 같은 credential로 exact digest pull 일치, 잘못된 credential 거부 확인, child rc=0, `EVIDENCE_SEAL=OK`
- 실행 도구: infra-harbor-trivy main PR #8(`74fc4b49…`)·PR #9(`b4e9eef`) 병합본. wrapper SHA256 `9ffc541874455fe981a762729000de94d575b01cc4b9091eb08c59fd9db7c88a`, 본체 `runner-push-test.sh` SHA256 `1305e9affe70132bcc570a646369834dd1ce237570a4c7537bbead6da6b6fe1e`. 독립 리뷰 supreme33-kr(PR #9 APPROVED), Linux Gate 23/23 PASS(이권욱, PR #9 코멘트).
- Lead 선언: 이 Run을 공식 AC-02 PASS 및 AC-03 handoff 기준으로 선언했다([#13 코멘트 5947371286](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947371286)).
- 같은 날 이권욱이 별도로 수행한 보조 Run(`hbr-20261002-163705-7a5537d2`)은 supplemental revalidation이며 이 폴더에 포함하지 않는다([#13 코멘트 5947598139](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947598139), [5947968672](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947968672)).

## 수신·전사 검증

- Runner·harbor01 원본은 터미널 출력을 PC로 옮겨(base64 또는 텍스트 재작성) 저장했고, 각 파일의 해시를 **원본 서버에서 계산한 해시와 대조**해 바이트 동일을 확인했다. 첫 TLS 전사본은 끝부분 해시가 어긋나 교체 후 일치를 확인했다. `if09-formal-run-…`의 5개 파일은 Runner가 봉인한 `SHA256SUMS`와 일치하고, `runner-push-test.sh`는 저장소 main 사본이며 해시 `1305e9af…`로 일치한다.
- 비밀정보 검색: `password|secret|token|robot$` 검색 결과 없음(로그인은 `Login Succeeded!`만 기록). Runner Podman trust 파일은 오류 문구의 "password" 단어(값 아님)만 해당.
- 화면 캡처 시각은 파일 메타데이터이다.

## 한계와 주의

- **추적성 주의:** `run.log`의 `SOURCE=infra-harbor-trivy main 6edf816 (tree 25b8195fe1c1)`는 wrapper에 남은 과거 하드코딩 문자열이며 실제 실행 commit이 아니다. 실제 실행 source는 병합 커밋 `b4e9eef`이다. 이 Run은 `summary.txt`·`run.log`의 `WRAPPER_SHA256`과 `SCRIPT_SHA256`으로 결속해 사용하고 SOURCE 문자열만으로 commit을 특정하지 않는다.
- 폴더 안 `SHA256SUMS`는 자체 봉인 대상이 아니다(AC-02 폴더 안의 것은 Runner 원본).
- 이 편입은 AC-03(Worker×3), AC-04(Source IP/Firewall), AC-05(4/4), AC-06(Robot 재발급·회전)의 PASS를 뜻하지 않는다. AC-06 화면 캡처는 재발급 이전(2026-10-01) 상태다.
- 전사·편입 자체는 작성자와 AI의 자체 검수이며 독립 리뷰 완료가 아니다.
