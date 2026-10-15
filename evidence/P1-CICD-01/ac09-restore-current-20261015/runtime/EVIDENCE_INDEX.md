# AC09 실제 원본 인덱스

기준: 2026-10-15 16:06:17 KST 단독 실행 종료. [실행 결과](RUNTIME_RESULT.md), [창 반환](WINDOW_RETURN.json), [시각 판정](TIMING_ASSESSMENT.json). 추가 Run·Token·POST·수동 PATCH 없음. 원본에는 공개 저장소에 올리지 않은 정상 관측 응답이 포함되므로 기존 승인된 비공개 보관 기준을 유지한다.

| 묶음 | 원본/판정 경로 |
|---|---|
| 승인과 입력 | `AUTHORIZATION_BINDINGS.json`, `R1/approval.json`, `R2/approval.json`, 회차별 deploy JSON, `STAGED.json` |
| 정확 4 Run·4 Job·로그 ZIP | `github-final/RUN_SUMMARY.json` 및 각 Run 폴더 |
| R1/R2 원 claim·checkpoint | `r1-journal-final/r1/stdout.json`, `r2-journal-final/r2/stdout.json` (원 mtime/ctime/inode/bytes/SHA 포함) |
| 첫 PATCH 구간 | `P_FIRST_ORIGINAL.json`, `R2_FIRST_PATCH_INTERVAL.json`, 첫 journal 원본 폴더 |
| 실제 전후 6대 시계 | `clocks-before-r1`, `clocks-after-finish`; 각각 6호스트·18명령 |
| 최소 업무 2회 | `r1-post-one/stdout.json`, `r2-post-one/stdout.json`, `r1/r2-before-mon`, `r1/r2-after-mon` 원 HTTP/metrics 응답 |
| 직접 포트 및 기존 경로 관측 | `r1/r2-before-edge-api`, `r1/r2-before-api`, 각 observer inventory의 Pod UID/container/PID/netns 결속 |
| 추가 Edge GET 4개 | 상위 `round4/edge-pre`, `round4/edge-during`; 원 helper 불변 |
| 현행 복귀/최종 상태 | `R2_CURRENT_PODS.json`, `RECOVERY_HTTP_CONFIRMED.json`, `r2-final-state`, `return-current-state` |
| 토큰 수량·만료 원본 | `operations/broker-execute-38693979785`, `operations/broker-execute-38694721511`; 토큰 값은 기록하지 않음 |
| 임시 공급 제거 | `EXACT_CLEANUP_RECEIPT.json`, `cleanup-inventory-*`, `operations/cleanup-exact-*`; 제거 전 파일별 SHA와 inode/mtime 보존 |
| 증적 보존 잔존물 | 원 서버 claim/checkpoint·Workflow 결과·native source 디렉터리 8개, 별도 삭제 없음. `return-ansible.json`, `return-control01`, `return-runner`에서 공개 소스 7개씩 canonical bundle SHA 일치 재확인 |
| 로컬 준비 예외 | `R1/actual-scope-over-local-metadata.original.json`와 `AUTHORIZATION_BINDINGS.json`; 원격 승인/입력 불변·발급 전 복구 |

`EVIDENCE_MANIFEST.json`은 이 폴더의 실제 파일과 외부 동결 기준/추가 Edge 원본을 파일별 SHA-256으로 연결한다. 원본·파생 결과·실행 보조 코드를 구분하며 SHA 일치 자체를 AC 통과로 판정하지 않는다. 매니페스트·자체 영수증만 자기 참조 방지를 위해 제외한다. 원 파일을 보존한 상태에서 결과/대장을 추후 추가하면 새 버전 인덱스로 별도 관리한다.

중앙이 #11 최종 umbrella 기록 및 다음 실행창을 담당한다. 이 세션은 중복 최종 댓글이나 타 세션 실행 메시지를 전송하지 않았다. DB 동일 ID 행 미수집·엄격 시각 상한 미입증을 유지하며, 후속 독립 리뷰에서 판정한다.
