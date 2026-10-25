# #46 A3 후속 실제 검증 — 2026-10-26

기준: 2026-10-26T04:16:19.631913+09:00. 실행/판정: 이권욱(Codex 보조). 독립 사람 Runtime 증적 리뷰는 대기 중이다.

| 항목 | 실제 결과 | 근거/한계 |
|---|---|---|
| A3 자동 배포 | ACK6·두 앱 Ready·finish/완료기록·펜스 해제 | [RUN40220786672](https://github.com/321Team/infra-cicd/actions/runs/40220786672), 원본 serialized NOT_VERIFIED는 편집하지 않음 |
| imageID | Pod6 전부 승인된 두 digest와 정확 일치 | 각 Pod→ReplicaSet→Deployment UID 확인, 각 앱3 Ready·restart0 |
| Health | 외부 HTTPS /readyz200 및 내부 엔진 /livez·/readyz200 | TLS 우회0, 외부 readyz는 실제 DB ping 계약 |
| 엔진 Rule | 정상 대조군·R01/R02/R04/R07 5응답 통과 | 내부 엔진 실제 HTTP, context는 명시한 시험 fixture, DB 쓰기0 |
| API/DB 연계 Rule | API201 10건 모두 기대값 일치 | R01 인출4·R07 이체4·R02/R04 각1. 고유 시험 account prefix `p46-a3-20261026-0355`. 실제 API commit 응답·이력 기반 응답 관측이며 직접 SQL 행조회는 미실행 |
| 고의 Unit 실패 | 기존 앱 Unit16 PASS 후 고정 unittest1 FAIL, CID REMOVED | [RUN40224325708](https://github.com/321Team/infra-cicd/actions/runs/40224325708), GitHub FAILURE·PUSH/DEPLOY NOT_EXECUTED |
| P2 실패 원본 reader | actual PrivateGitHubTLS→ActionsRunSource.inspect에서 ACTIONS_RUN_NOT_SUCCESSFUL | 실제 실패 RUN/attempt/job/step을 test negative pin으로 선택, 운영 SITE·grant 변경0·새 SA 발급/claim/배포0 |
| ROSA 전후 | 두 Deployment UID·generation·RV·spec·managedFields 및 Pod6 UID/imageID/containerID/restart/Ready 동일 | 2026-10-26T03:58:06.024571+09:00 → 2026-10-26T04:10:33.983102+09:00, 외부 readyz200 유지 |
| 실패 차단 AC | 부분 관측/독립 인수 대기 | negative Workflow에는 Deploy job이 없어 skipped job을 주장하지 않음. linked native dispatch chain 전체 실행 증거는 아님 |
| 버전 rollback | 미실행·차단 | 승인된 상이한 이전 P2 digest 없음. current와 같은 previous를 재적용하거나 최초배포 앱0을 버전 rollback PASS로 바꾸지 않음 |

## 원본·계보와 한계

- image source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`의 main/rules/context 파일4개를 실제 Git blob에서 수신해 기존 검토 source와 hash 일치를 확인했다. render source `69e28c494a120c388afe18d901043d05333d7c7c`의 DELIVERY-CONTRACT-rosa.md §9는 최초 P2 previous 없음 및 다음 검증본을 previous 후보로 삼는 절차를 명시한다.
- 단일 승인 image profile 338b8a28… / 8b257adb…만 확인했다. 새 릴리스·상이 이미지·rollback 승인/성공을 합성하지 않았다. 현재와 다른 승인 profile/source/scan/registry/복구 render가 없으므로 현 요청의 버전 복구는 실행 불가다.
- failed reader 검사는 기존 실제 A3 Binding key `5a5940c2…`에 대한 음성 입력 선택이다. 새로운 정상 producer 계보·GO·앱 쓰기를 생성하지 않았다. 원 native Job의 `DELIVERY_GATE=NOT_VERIFIED`는 보존한다.
- 원본의 사후 수집기 자체 검토는 CODEX_ASSISTED이며 외부AI 의견을 사람 독립 리뷰로 표시하지 않는다. 기존 코드/기준을 완화하거나 현장 권한·TLS를 변경하지 않았다.

## 회수 인계

- 앱 각3은 계속 실행 중이다. 소비종료 **10/26 08:30**, 최종 정리·복구·원본 반출·보고 **12:00** 유지.
- 신규 관리호스트 `final-validation-20261026-0355*`, `post-b1-validation-20261026-0410*`, Runner 전용 `cicd-unit-negative-40224325708-1` checkout와 `/home/server01_cicd-runner/FDS_CICD_UnitNegative.l6l2lwoq`를 원본 반출 후 자기 P2 회수 목록에 추가한다. 공용 HOME/SSH/기존 공급/다른 회차 삭제0.
- Unit fixture CID `3e56793c…`는 그 실행에서 제거 확인. 새 source 자격 생성0; 기존 PAT21758739는 GitHub UI 만료10/27과 구분해 오늘12시 전 수동 폐기 대상이다.
- API 시험10건 transaction_id는 FINAL_STATUS.json에 별도 기록했다. 실제 DB 데이터의 삭제는 수행하지 않았고 기존 사용자 거래를 건드리지 않았다.

## 외부 AI 병행

Claude Code `claude-opus-5-5/high`, Grok CLI `grok-4.7/high`(actual grok-4.7-build), Antigravity CLI `gemini-4-argon-high/high` 실제 응답을 수신했다. 실제 effort 별도 metadata는 세 도구 모두 미제공. AGY 첫 호출150초 빈응답은 실패로 보존하고 두번째43초 응답을 사용했다. 외부에는 비밀/운영 raw를 제공하지 않고 시험 설계 명세만 전달했다. 채택/기각은 EXTERNAL_DISPOSITION.json 참조.

해시 일치는 무결성이며 AC/독립 리뷰/최종 인수 완료를 뜻하지 않는다. #46은 In Progress를 유지한다.
