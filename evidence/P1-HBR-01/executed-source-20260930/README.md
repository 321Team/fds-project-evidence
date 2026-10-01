# P1-HBR-01 — 2026-09-30 Runtime 검증에 실제 실행된 스크립트 원본

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 이 폴더는 같은 PR의 [`received-20260930T040033Z`](../received-20260930T040033Z/README.md)(로그 원본)를 만든 **스크립트의 실행 당시 원본**이다. 독립 리뷰(CHANGES_REQUESTED, exact HEAD `c946f831…`)의 BLOCKER 1(실행 source provenance)에 대응한다. 판정이 아니라 원본 보존이다.

## 파일

| 파일 | 원본 위치 | SHA-256 |
|---|---|---|
| `worker-scripts.tgz` | k8s-worker01(10.1.93.105) `~/verify`에서 ansible01로 `tar czf -` 스트림 수집 | `0ed648c8d67da0428315290e9227a83d4919b079d3c897de5c51640dc2f36e50` (sidecar `.sha256` 동봉) |
| `runner-push-test.sh` | cicd-runner01 `~/verify` | `f8a26cdca188c2e289899b4c98e7f44750d7f1f6585cc3e0283e4e8d87026d12` |
| `server-vs-repo-20ce46b.code-diff.txt` | 위 서버 파일과 저장소를 대조한 결과 | 아래 참고 |

`worker-scripts.tgz`는 재압축하지 않았다. 내용물: `worker-pull-pod-start-test.sh`, `digest-traceability-check.sh`, `pod-restricted-psa-overrides.json`, `lib/load-review-run-env.sh`, `lib/pod-review-binding.sh`, `lib/pod-review-lifecycle.sh`. `runner-push-test.sh`는 수집 경로에서 base64로 옮겨 원본 해시와 일치함을 확인했다.

## 실행 대상 서버와 동일성

3대 워커에서 같은 파일 목록의 `sha256sum`을 각각 실행해 **worker01(.105)/worker02(.107)/worker03(.108) 결과가 서로 동일**함을 확인했다.

| 파일 | SHA-256 (세 대 동일) |
|---|---|
| `worker-pull-pod-start-test.sh` | `3e8cea37c6f334ff9e867026d097dc73392c783d09ac852eb520fc1b40ac0173` |
| `digest-traceability-check.sh` | `a9c513572c779d3a7fb3d476a0de3ef0576cd6ebd17a6bb4bcc7141779846cd6` |
| `pod-restricted-psa-overrides.json` | `d863c259416caeaf2b1962d77da09d7c8af365a20dd8c689de305082a7bd1686` |
| `lib/load-review-run-env.sh` | `aa7f76c8f3b1d35100175566a8edb5bb3f086bb3fd9be43099afa6a6aa9685e5` |
| `lib/pod-review-binding.sh` | `bdbe3cf1e8a5852d9c620acea5af22f50e40663d008688d16e1e2180df90a621` |
| `lib/pod-review-lifecycle.sh` | `900fb82b91fe7889311bc968b5c1a9bfb71fc65f2ad282b73a35c20e9039b60c` |
| `review-run.env` (내용 미보존, 해시만) | `c9fddfb5fcef7366d4791b627fa55cf3020ed81dc6fe104455ed5a41ae7147b2` |

## 한계: 실행 시각과 수집 시각

위 해시는 **2026-09-30 오후(KST)에 서버에서 재계산한 값**이다. 오전 실행 시점에 해시를 남기지 않았으므로, 그 사이 파일이 바뀌지 않았다는 것은 (a) 세 대가 서로 동일하고 (b) 저장소 대비 차이가 아래 설명과 정확히 일치한다는 정황으로만 뒷받침되며 **암호학적으로 고정되지 않는다.** 실행 시점의 file hash 기록은 없다.

## 저장소 `infra-harbor-trivy` 20ce46b와의 관계

비교 기준: `infra-harbor-trivy` `scripts/verify/` @ `20ce46b50d8ec4f5f4208d1382bc7bf3ecf5478d`(이 경로의 마지막 커밋, 비교 시점 main `89cfd0299fad…`와 내용 동일). 서버 파일의 해시는 저장소의 어떤 커밋 버전과도 바이트 단위로 일치하지 않는다. 줄 끝(CRLF) 차이는 아니다. **주석·빈 줄을 제거한 뒤** 비교한 결과는 [`server-vs-repo-20ce46b.code-diff.txt`](server-vs-repo-20ce46b.code-diff.txt)에 있고 요약은 다음과 같다.

| 파일 | 결과 |
|---|---|
| `lib/load-review-run-env.sh`, `lib/pod-review-binding.sh`, `lib/pod-review-lifecycle.sh` | 로직 동일. 서버 실행본에는 주석이 없다 |
| `pod-restricted-psa-overrides.json` | 바이트 동일 |
| `digest-traceability-check.sh` | 로직 동일. **에러/출력 메시지 문구만 짧게 변경**(예: `OK: Harbor manifest Digest: …`) |
| `worker-pull-pod-start-test.sh` | 로직 변경 2건: ① push 직전 `worker-push-denytest-<REVIEW_RUN_ID>` 고유 태그로 재태깅 후 그 태그 push, ② 거부 판정 정규식에 `unauthorized to access repository.*action: push` 추가 |

이전 README(`received-20260930T040033Z`)는 이 변경을 "로컬 수정 2건"으로만 적었다. 정확히는 **로직 수정 2건 + 주석 제거 + 메시지 문구 정리**다. 이 수정본은 `infra-harbor-trivy` 저장소에서 리뷰를 받지 않았다.

## `runner-push-test.sh`에서 확인한 한계 (판정 아님)

- 스크립트 제목은 Push/Pull이지만 실제 시험은 push(와 로그인 Positive/Negative)만 수행한다. Pull Positive 시험은 이 스크립트에 없다(Pull은 워커 스크립트가 다룬다).
- `PUSHED_DIGEST`는 `podman push` 출력의 **마지막 `sha256:` 값**이다. 그 출력에는 config blob 줄(`Copying config sha256:…`)이 있고, 오전 로그의 `bf8527eb…`는 그 config digest와 같은 값이다. 따라서 이 값을 Harbor에 저장된 **manifest digest로 읽으면 안 된다.**
- Negative(잘못된 credential) 판정은 로그인이 실패하고 출력에 timeout/TLS/certificate 등 전송 오류 문구가 없으면 PASS로 처리한다. `unauthorized`/`401` 같은 인증 거부 문구를 요구하지는 않는다.
- 이 스크립트는 저장소 밖 별도 파일이며 리뷰를 받지 않았다.

## 이 원본으로 주장하지 않는 것

- 저장소 main의 코드가 실행됐다는 주장 — 실행된 것은 위 서버 파일이다.
- 스크립트의 정식 리뷰 완료 — 정식 AC 판정에는 코드 PR 리뷰 후 같은 SHA로 재실행이 필요하다.
- 실행 시각의 파일 해시 — 위 "한계" 참고.
