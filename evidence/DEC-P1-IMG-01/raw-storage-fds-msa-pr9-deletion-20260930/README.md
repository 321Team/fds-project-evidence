# fds-msa#9 후보 artifact 172개 GitHub 삭제 기록 (2026-09-30)

[raw-storage-fds-msa-pr9-20260926](../raw-storage-fds-msa-pr9-20260926/README.md)(fds-project-evidence#76, merge `8f0550c6391206741636dbf244ede8306a2db493`)의 "다음 조치 1"을 수행한 기록이다. 공유 디렉터리 보관과 해시 대조가 끝난 artifact 172개를 GitHub에서 삭제했다.

## 근거

- 보관 기록 [fds-project-evidence#76](https://github.com/321Team/fds-project-evidence/pull/76): 이권욱 APPROVED(exact HEAD `b7f729ba8e18241942b6fd9dbb3137bd31cdcbf6`, 2026-09-30T03:43:14Z). 리뷰 본문에 "이 승인은 보관 기록 편입 및 후속 GitHub artifact 삭제 진행에 대한 서면 확인"이라고 적혀 있다.
- 삭제 대상: 병합된 [ARTIFACTS.tsv](../raw-storage-fds-msa-pr9-20260926/ARTIFACTS.tsv)의 artifact ID 172개. 다른 artifact는 삭제하지 않았다.

## 수행

| 항목 | 내용 |
|---|---|
| 수행자 | 이재환(supreme33-kr). 본인 PC의 Git Bash에서 직접 실행했다 |
| 시각 | 2026-09-30T03:47:56Z~03:49:45Z (12:47~12:49 KST) |
| 명령 | 병합된 `ARTIFACTS.tsv`의 ID마다 `gh api -X DELETE repos/321Team/fds-msa/actions/artifacts/<id>`, 결과를 `tee`로 기록 |
| 결과 로그 | [DELETE_LOG.txt](DELETE_LOG.txt): 172줄, `DELETED` 172, `FAILED` 0. 로그의 ID 집합은 대상 172개와 같다 |

## 삭제 후 확인

2026-09-30T03:52~03:54Z, Claude Code 세션에서 read-only로 조회했다.

| 확인 | 방법 | 결과 |
|---|---|---|
| 개별 조회 | 172개 ID마다 `GET /repos/321Team/fds-msa/actions/artifacts/<id>` | **172/172 HTTP 404** ([POST_DELETE_CHECK.tsv](POST_DELETE_CHECK.tsv)) |
| 목록 조회 | fds-msa·infra-ansible·fds-project-baseline의 만료 전 artifact 목록 | 185개 1,288,751,760 bytes. 대상 ID와 겹치는 것 0개 ([REMAINING_ARTIFACTS.tsv](REMAINING_ARTIFACTS.tsv)) |

공유 디렉터리의 보관본은 이번 작업에서 바꾸지 않았다.

## 남은 저장 용량

삭제 뒤에도 만료 전 artifact는 1,288,751,760 bytes로 무료 저장 한도 0.5GB보다 크다. 대부분 fds-msa에 있다.

| 남은 것 | 용량 | 만료(UTC) | 비고 |
|---|---|---|---|
| `candidate-images-bbe349c8…-1`(Run 35921580081) | 278,490,138 bytes | 2026-09-30T21:18:11Z | P1-CICD-01 RAW_STORAGE_PLACEMENT_20260924로 공유 디렉터리에 보관돼 있음 |
| 브랜치 `app/distroless-py313-20260926`의 2026-09-27 artifact 18개 | 약 298MB | 2026-10-04 | #76 범위 밖. fds-msa#9에서 일부 인용 |
| `apko-offline-supply` 6개(main·`ci/apko-offline-supply-20260927`·`app/distroless-py313-builder-tzdata-20260928`) | 약 659MB | 2026-10-04~10-05 | main Run 36415939069는 artifact에만 의존하는 증적 |

- GitHub 사용량은 6~12시간마다 다시 계산되고, 월 포함 사용량은 2026-10-01에 초기화된다. 권욱 코멘트의 infra-ansible quota 재시험은 초기화와 재계산 이후에 수행한다.
- 재시험에서도 quota 오류가 나면, 위 남은 artifact의 추가 보관·삭제를 별도로 결정한다. 이 기록은 그 결정을 포함하지 않는다.

## 한계

- 이 기록은 GitHub artifact 삭제만 다룬다. DEC-P1-IMG-01·P1-CICD-01·P1-APP-01의 판정과 상태를 바꾸지 않는다.
- 조직 청구 화면의 저장 사용량은 조회하지 않았다(NOT VERIFIED). 위 수치는 artifact 목록 API의 `size_in_bytes` 합계다.
