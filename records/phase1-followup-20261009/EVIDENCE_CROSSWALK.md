# Phase 1 후속 증적 대응표 — 2026-10-08/09

CODEX_ASSISTED · 이권욱. 기준 main `dfb2521a8de77686c6566e8752899772f61eb8a1`, GitHub 병합 상태 재조회 10/8 23:29 KST. 봉인된 원본·기존 판단은 수정하지 않고 후속 편입 상태를 별도 연결한다. 이 표는 새로운 AC 인수나 위험 수용·종결 결정이 아니다.

| 과거 미수집/대기 표기 | 후속 근거와 현재 수집 단계 | 그대로 남기는 경계 |
|---|---|---|
| APP 전체 원문20개 미수신 | [#138](https://github.com/321Team/fds-project-evidence/pull/138)으로6개 보충·병합. [이번 회차](../../evidence/P1-APP-01/topology-spread-originals-20261009T000019/README.md)로 잔여14개 수신·과거 manifest 해시14/14 일치 | 편입 리뷰는 별도. engine MON60.9647초 절차 이탈은 소급 해소하지 않음 |
| K8S control02 외5대 적용본 미수집 | [이번 회차](../../evidence/P1-K8S-01/v4-readonly-comparison-20261009T000026/README.md)로5대 수집·비교45개 중28개 일치·17개 불일치 | 수집 완료와 소스 정합성을 구분. 도구 교체·정책 적용·AC 인수 미수행 |
| K8S Edge/CP02·03 추가 관측 대기 | [#144](https://github.com/321Team/fds-project-evidence/pull/144) 병합 | 승인1회 대비 중복 실행과 timeout 귀속 한계. 해당 AC의 최종 처분과 별도 |
| SEC backup 격리 복원 미실행 | [#152](https://github.com/321Team/fds-project-evidence/pull/152) 병합 | 격리 복원 범위를 넘어 실제 클러스터 전체 복구·예방 회전 성공으로 확대하지 않음 |
| IF03/IF13A·hostNetwork 관측 공백 | [#155](https://github.com/321Team/fds-project-evidence/pull/155), [#157](https://github.com/321Team/fds-project-evidence/pull/157) 병합 | 수행한 출발지·행·시각의 범위. 미관측 조합·기존 위험 수용과 별도 |
| Discord 수신 원문 미확보 | [#157](https://github.com/321Team/fds-project-evidence/pull/157)의 receipt 보충 있음 | Firing 화면08:57, Resolved 약1분 뒤라는 담당자 정정. 메시지 링크·개별 정확한 시각과9093 비허용Source 시험은 별도 |
| worker02 DNS 검증 대기 | [#167](https://github.com/321Team/fds-project-evidence/pull/167) 병합 | verify 한 대 성공. apply/rollback·전역 Ansible 엔진 전환 성공 아님 |
| Client→Edge 후속 관측 대기 | [#169](https://github.com/321Team/fds-project-evidence/pull/169) 병합 | 해당 경로의 관측. 최종 APP Source 전체 회귀·CICD 전달 성공과 별도 |
| DB .50 제거/credential 회전 실행 대기 | [#172](https://github.com/321Team/fds-project-evidence/pull/172) 병합 | control01 N1 귀속 불명확, W4 5xx NOT_MEASURED, 복구 미실행. 위험 수용 종료는 Lead 판단 |
| 격리 Probe 재시험 대기 | [#173](https://github.com/321Team/fds-project-evidence/pull/173) 병합 | 격리 exec T0~T3·UID 삭제·봉인. 실제 APP HTTP Probe나 #19 전체 완료 아님 |
| CICD 성공 회차 증적·구축 PR 리뷰 대기 | [#147](https://github.com/321Team/fds-project-evidence/pull/147) 및 infra-cicd#65/#66/#67 병합 | 새 Push/Deploy는 미실행. [정합화 PR69](https://github.com/321Team/infra-cicd/pull/69) 리뷰 대기 |
| DR 격리 복원·E2E 미실행 | [#67](https://github.com/321Team/fds-project-evidence/pull/67) 원본 있음 | 9/3 dump 인계 미확인. [Runbook PR11](https://github.com/321Team/infra-db/pull/11) 초안 작성·Lead 검토 대기 |

## 실행 경계

[단독 작업창 기록](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6062332401): 2026-10-09 00:00~09:00 KST, 사용자 확인. 첫 회차는 APP 기존 원본과 K8S 적용본의 읽기 전용 수집이다. 하위 폴더의 receipt가 실제 수신 결과이며 이 대응표의 계획 문구는 실행 증거가 아니다.

Harbor 자동기동은 타 세션에 남긴다. 실습·고장 주입·Push/Deploy·운영 엔진 전환에 필요한 해당 승인/정책/복구 조건은 창 확보만으로 면제하지 않는다. 철회된 #30 예외 제안이나 과거 만료 GO는 사용하지 않는다.
