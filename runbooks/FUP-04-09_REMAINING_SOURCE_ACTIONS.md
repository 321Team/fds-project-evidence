# FUP-04~09 잔여 원본·참조 후속 실행표

> **증적 현황 안내(2026-09-25 갱신):** [Evidence 후속 현황](../registry/EVIDENCE_FOLLOWUP_20260924.md)의 맨 위 절에 main `4d2db33` 기준 병합·잔여 상태를 정리했다. 그 이후 변경은 PR 이력과 해당 문서를 따른다. 아래 과거 검토·병합 대기 표기는 각 작성 시점의 이력이다.

이번에 [기존 증적 매핑](../records/followup-mapping-20260909/EXISTING_EVIDENCE_MAP.md)을 등록하고 독립 검토를 요청한다. 기존 증적의 미매핑 부분을 연결하는 작업이며 아래 미수신 자료의 수령 완료를 뜻하지 않는다.

| 항목 | 확인 주체 | 착수한 일 | 다음 입력 / 완료 기준 |
|---|---|---|---|
| Index 10 | 이권욱 | 기존 종결 문서 고정 링크 연결 | 재제출 불필요. 이번 연결 정정 검토 |
| Index 03~06 | 이권욱 / 이재환 | 8/28 원본 5개·Manifest·수신 맵 대조 및 공통 참조 연결 | 이재환은 새 매핑의 범위·일시·5개 Hash·한계만 독립 검토 |
| Index 01/02 | 이권욱 / 자료 보유자 | 최초 Windows/VMware 자료 탐색 대상 지정 | server01~08 PostBuild 로그와 실제 Virtual Network Editor 캡처 또는 정확한 기존 보관 위치 |
| Index 03~08 최초 원본 | 이권욱 / 자료 보유자 | 8/26 최초 원본과 8/28 보완 근거를 분리 | 당시 Linux/관리 VM/gateway Verify 원문·Manifest·보관 위치. 이미 연결한 8/28 원본의 재제출은 불필요 |
| Index 09 | 이권욱 | IP 예외 결정 문서 연결 | 필요 시 당시 응답 장비 조사 원문 연결. 기존 IP 결정을 다시 적용하지 않음 |
| FUP-05 | 이권욱 | 기존 Done와 과거 승인자 미확인을 분리 | 당시 검토자·승인자·일시·범위가 보이는 회신 또는 고정 참조 |
| FUP-06/07 | 이권욱 | 정본 APPROVED 표기 발췌 연결 | 사람별 승인 회신·승인 시각, 검토자의 WBS 바이너리 실제 열람 확인. 이전 후보 편입 재승인 불필요 |
| FUP-09 Permanent | 이하영 | 수신·독립 승인·병합 근거를 인수 판단 입력으로 준비 | 확인한 Commit·검토일시/시간대·인정 범위·남은 조건의 본인 회신 |
| FUP-09 IP 중복검사 | 이권욱 / 자료 보유자 | 기존 8/31 게시 시각을 탐색 단서로 연결 | 2026-08-31T08:04:05Z 게시 원문·내보내기 또는 당시 저장 파일. 새 arping을 과거 증거로 쓰지 않음 |

## 기존 보관 위치 탐색 후보

- ansible01의 당시 키트 최상위 아래 `evidence-source-preservation/<timestamp>/summary.tsv` 및 노드별 txt. `fds-source-preservation-batch.sh`가 정의한 출력 위치다.
- Linux의 `/var/tmp/fds-build-evidence`, Windows의 당시 키트 Evidence 폴더. `FDS_VM_Setup_Guideline_v3.1.1.md`에 안내된 위치다.
- 문서상 공통 제출 위치 `docs/evidence/D-NET-01/`. 현재 실제 디렉터리 존재나 파일 수신은 확인되지 않았다.

위 위치는 스크립트·가이드의 탐색 후보이며 실제 저장 확인 결과가 아니다. 자료 보유자가 기존 파일/목록/경로를 제공하면 대상·작성/수집일·기존 Hash·승인 참조를 확인해 별도 수신 기록을 만든다. 비밀키·토큰·암호는 제출 대상이 아니다.

## 인수 판단 입력

대상: [PR #6 검토 HEAD 0450108c](https://github.com/321Team/fds-project-evidence/tree/0450108cecfe961557bb2b1a427a9bae5d93d722), [병합본 493c09e7](https://github.com/321Team/fds-project-evidence/commit/493c09e728b643d620debe29738f1b47b3cafa8a), [수신 검토](../evidence/P1-LB-01/stage-a/supplement-20260909T072022Z/README.md).

이하영의 실제 회신에는 본인이 확인한 Commit, 검토일시·시간대, 현재 시각 Permanent 자료의 인정 범위, 남은 조건을 기재한다. 새 인수 회신은 아직 수신하지 않았다. 자료 준비는 인수 서명이 아니다.

일정은 원본 보유 위치·담당자의 회신을 확인한 후 정한다. 미확인 기한이나 승인자를 새로 만들지 않는다. 직접 메시지 발송·서버 조회·apply·rollback·Bootstrap 실행은 이번 작업에서 수행하지 않았다.
