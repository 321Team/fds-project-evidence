# fds-msa#9 후보 artifact 원본 보관 기록 (2026-09-30)

[fds-msa#9](https://github.com/321Team/fds-msa/pull/9) 작업 브랜치 `app/distroless-py313-20260926`에서 2026-09-26에 생성된 GitHub Actions artifact 172개를, GitHub에서 삭제하기 전에 팀 공유 디렉터리로 옮기고 해시를 대조한 기록이다. 상위 Record ID는 DEC-P1-IMG-01([baseline #110](https://github.com/321Team/fds-project-baseline/issues/110), Related PR `321Team/fds-msa#9`)이다.

## 배경

- 321Team 조직의 GitHub Actions·Packages 무료 저장 한도는 0.5GB다. 2026-09-30 조회 시점에 조직 전체 artifact는 368개 8,798,150,397 bytes였고, 그중 fds-msa가 199개 8,791,923,177 bytes였다(artifact 목록 API의 `size_in_bytes` 합계, 만료 전 artifact만).
- 한도 초과로 [infra-ansible Run 36522640149](https://github.com/321Team/infra-ansible/actions/runs/36522640149)가 artifact 업로드 단계에서 `Artifact storage quota has been hit. Unable to upload any new artifacts.`로 실패했다.
- 이번 대상 172개가 7,509,394,490 bytes로 대부분을 차지한다. GitHub 보존 기간이 끝나는 시각은 2026-10-03(UTC)이다.

## 결정

| 항목 | 내용 |
|---|---|
| 보관·삭제 확인 | 이권욱(fds-msa#9 작성자, P1-CICD-01 Lead), 2026-09-30 **구두 확인**. 이재환이 전달받았다. 이 기록 외에 서면 원본은 없다. 리뷰 승인으로 서면 확인을 대신한다 |
| 수행 | 이재환(DEC-P1-IMG-01 Lead). 다운로드·대조·복사는 Claude Code 세션에서 실행했다 |
| 방식 | 선례 [RAW_STORAGE_DECISION_20260924](https://github.com/321Team/fds-project-evidence/blob/9df407cf7fbdc455a9dd5bdeff17303c2c28a4e7/evidence/P1-CICD-01/app-remediation-followup-20260924/github-hosted-run-35921580081-1/RAW_STORAGE_DECISION_20260924.md)·[RAW_STORAGE_PLACEMENT_20260924](https://github.com/321Team/fds-project-evidence/blob/9df407cf7fbdc455a9dd5bdeff17303c2c28a4e7/evidence/P1-CICD-01/app-remediation-followup-20260924/github-hosted-run-35921580081-1/RAW_STORAGE_PLACEMENT_20260924.md)과 같은 정식 보관 위치를 쓴다. EVIDENCE_POLICY의 "1MB를 넘으면 별도 보관소에 두고 URI·SHA-256만 연결"에 따라 원본 바이트는 Git에 넣지 않는다 |

## 보관 위치

`\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\01차 프로젝트\02 프로젝트 결과물\fds-msa-pr9-app-distroless-py313-20260926\`

| 파일 | 내용 |
|---|---|
| `<artifact 이름>.zip` × 172 | GitHub API `GET /repos/321Team/fds-msa/actions/artifacts/{id}/zip`로 받은 바이트 그대로(재압축 없음) |
| `<artifact 이름>.zip.sha256` × 172 | sidecar, 형식 `<sha256>  <파일명>` |
| `SHA256SUMS` | 172개 zip의 SHA-256. 이 폴더의 [RAW_ZIP_SHA256.txt](RAW_ZIP_SHA256.txt)와 같은 내용 |
| `ARTIFACTS.tsv` | artifact ID·이름·크기·GitHub digest·Run ID·head SHA·생성·만료 시각. 이 폴더의 [ARTIFACTS.tsv](ARTIFACTS.tsv)와 같은 내용 |

## 대상 범위

- 포함: fds-msa artifact 중 `workflow_run.head_branch = app/distroless-py313-20260926`이고 2026-09-26(UTC)에 생성된 172개. 생성 11:19:10Z~18:18:21Z, 합계 7,509,394,490 bytes. 목록은 [ARTIFACTS.tsv](ARTIFACTS.tsv)에 있다.
- 제외: 같은 브랜치에서 2026-09-27에 생성된 18개(298MB), main 브랜치 `apko-offline-supply`와 2026-09-28 artifact, infra-ansible·fds-project-baseline artifact. 이번 보관·삭제 대상이 아니다.

### 인용된 실행과의 대응

아래 실행은 fds-msa#9 본문·코멘트·리뷰 또는 baseline #110(`audit/issue-body-repair-20260928/bodies/issue-110.md`, `governance/ticket-sync-map.json`)에서 인용된다. 모두 이번 보관 범위에 들어 있다.

| Run ID | artifact ID | artifact 이름 |
|---|---|---|
| 36244672648 | 10906982795 | `candidate-images-2a82a1bdf20f740f953b89395770da71b32e478f-1` |
| 36244672651 | 10907201013 | `py313-lock-candidate-2a82a1bdf20f740f953b89395770da71b32e478f-1` |
| 36254936425 | 10910034850 | `runtime-base-probe-distroless-base-debian13-9d21c0a9a104e018c17ed06ebdbe6bdb38615232-1` |
| 36254936425 | 10910104308 | `runtime-base-probe-distroless-cc-debian13-9d21c0a9a104e018c17ed06ebdbe6bdb38615232-1` |
| 36254936425 | 10910505843 | `runtime-base-probe-python-313-alpine-9d21c0a9a104e018c17ed06ebdbe6bdb38615232-1` |
| 36257652463 | 10911098862 | `wolfi-py313-candidate-9ffa43332553eac2d8e732347b79225c5aee0039-1` |
| 36258123200 | 10911630807 | `wolfi-py313-candidate-6a92b63554c870884d5fe4e8c21984282a7112b2-1` |
| 36258996521 | 10910844205 | `apko-wolfi-py313-782c8ea25503b1934754931a41965f862c46fe5a-1` |
| 36259714053 | 10911608373 | `apko-wolfi-py313-d10cbc4d9eadb27f95891dd765705b31636e1788-1` |
| 36259793213 | 10911937542 | `apko-wolfi-py313-04dcc8f4a88286f568f661ead47a245501bf1bfe-1` |
| 36261693099 | 10912401890 | `apko-wolfi-py313-b78d90914856feb4ce4bcf8a500a789a0a821ca9-1` |
| 36261976104 | 10912322356 | `py313-lock-candidate-88b494c58d057303672cc1502021ab4655a4e916-1` |
| 36261976189 | 10912672801 | `candidate-attestation-capability-88b494c58d057303672cc1502021ab4655a4e916-1` |
| 36261976339 | 10912162747 | `apko-wolfi-py313-88b494c58d057303672cc1502021ab4655a4e916-1` |

fds-msa#9에서 인용한 2026-09-27 실행(36298642676·36298642693·36298642920)의 artifact는 이번 범위 밖이며 GitHub에 그대로 있다.

## 대조 결과

2026-09-30 11:50~12:29 KST, 이재환 PC(Windows, Git Bash `sha256sum`)에서 수행했다.

| 단계 | 방법 | 결과 |
|---|---|---|
| 1. 다운로드 | GitHub API artifact zip 다운로드, 4개씩 병렬 | 172개, 7,509,394,490 bytes |
| 2. 로컬 대조 | 파일마다 크기가 API `size_in_bytes`와 같은지, SHA-256이 API `digest`와 같은지 확인 | **172/172 일치** |
| 3. 공유 위치 복사 | 로컬 파일을 공유 폴더로 복사(덮어쓰기 없음) | zip 172·sidecar 172·`SHA256SUMS`·`ARTIFACTS.tsv`, zip 합계 7,509,394,490 bytes |
| 4. 공유 위치 대조 | 공유 폴더에서 `sha256sum -c SHA256SUMS` | **172/172 OK, 실패 0** |

- GitHub `digest`와 SHA-256이 같으므로, 보관한 zip은 GitHub가 저장한 artifact 바이트와 같다.
- 공유 위치 `SHA256SUMS` SHA-256 `134fb8738efd28496d726549253510e5ed0cfd0252fcabef7ea44a07d407a6a8`(이 폴더 [RAW_ZIP_SHA256.txt](RAW_ZIP_SHA256.txt)와 바이트 동일).
- 공유 위치 `ARTIFACTS.tsv` SHA-256 `84c88ad4a46c3c71b7b3243922a5fe4d1ce3965215e071c5ee2628a563c8081c`(이 폴더 [ARTIFACTS.tsv](ARTIFACTS.tsv)와 바이트 동일).
- 로컬 다운로드 초기에 순차 다운로드와 병렬 다운로드가 잠시 겹쳐 실행됐다. 그래서 다운로드 중 기록한 결과 대신, 다운로드가 끝난 뒤 2단계에서 172개 전체를 다시 대조한 결과를 기준으로 삼는다.

## 한계

- 이 기록은 원본 보관 위치만 다룬다. artifact 내용물(이미지·lock·보고서)은 검토하지 않았고, DEC-P1-IMG-01·P1-CICD-01·P1-APP-01의 판정과 상태를 바꾸지 않는다.
- 두 대조 모두 수행자(이재환 세션)의 결과다. 공유 위치 사본의 독립 대조는 하지 않았다(NOT VERIFIED). 리뷰어는 공유 위치에서 `sha256sum -c SHA256SUMS` 또는 `Get-FileHash`로 확인할 수 있다.
- 구두 확인의 서면 원본은 없다.

## 다음 조치

1. 이 PR의 리뷰·병합이 끝나면 이재환이 GitHub의 artifact 172개를 삭제한다. 삭제 결과(삭제 ID 목록, 조회 결과)는 같은 Record ID 아래 새 폴더에 기록한다.
2. fds-msa 워크플로우가 이미지 tar를 artifact로 올리는 방식(실행마다 약 50~200MB)의 개선은 별도 PR로 다룬다.
