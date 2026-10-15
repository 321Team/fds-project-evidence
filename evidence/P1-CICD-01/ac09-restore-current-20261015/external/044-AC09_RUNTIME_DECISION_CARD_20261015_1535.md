# AC09 단회 실행·현행 복구 결정 카드

**검토용 후보 / 사용자 최종 허용 전 / Runtime 미실행.** 2026-10-15 KST. 이 카드의 승인은 아래 한 회차의 실행·별도 유한 복구와 해당 결정/결과의 infra-cicd #11 기록만을 대상으로 한다. AC09 최종 인수·티켓 종결은 실제 결과 검토 후 별도 판정한다.

## 시간과 단일 담당

| 항목 | 후보 범위 (KST) |
|---|---|
| 정상 작업창 W~W+45 | **10월15일 15:35~16:20** |
| 최초 구버전 PATCH P | **15:45까지**. 도달하지 못하면 새 R1 시작 중단 |
| R1 승인 만료 | 16:00; 기존 시작 예산·Token 유효기간 검사는 유지 |
| R2 승인 만료 | 16:15; 실제 첫 현행 PATCH는 **P+15분 이내** |
| 노출 회수 | **P+30분 이내**, P 최댓값 기준16:15까지 |
| 별도 현행 복구 허용 | **15:35~16:35**, 아래 정확 두 대상의 현행 복원만 |

실제 실행 단일 담당은 기존 **[로컬] Phase 1 CI/CD 배포·복구 검증 — AC09** 채팅이다. 중앙은 창·결과·통지와 공통 기록을 조정한다. 실패 시 실제 수동 복구 수행자는 이미 수락한 **이권욱**, 확인한 **server02@k8s-control01 VM 콘솔**이다. 로그인·당일 가용성·DB 자료를 다시 요구하지 않는다.

위는 후보이며 아직 예약이 아니다. 사용자 허용과 fresh 조건이 시작 시각에 갖춰지지 않으면 이 창으로 강행하거나 자동 연장하지 않는다. 준비·공급·false 검증도 허용된 정상 창에 포함한다.

## 허용할 정상 범위

- namespace `fds-app`의 아래 두 Deployment만 현행→이전(R1)→현행(R2)으로 검증한다. replicas·환경·네트워크/권한·DB schema는 변경하지 않는다.
- 기존 native Runner #2에서 R1/R2 execute=false 각1회, execute=true 각1회: **최대4job, 각 Attempt1**, 신규 Runner등록0. 응답 불명 시 dispatch/실행을 반복하지 않는다.
- 기존 broker의 **TokenRequest 최대2회·TTL각900초**, 실제 expiry·시작 잔여예산 검사. 자동 추가 발급 없음.
- 업무 표본은 각 회차 입금 POST1건, **합계최대2건**. timeout/응답 유실 시 재POST하지 않고 동일ID 결과를 기존 읽기 경로로 판정한다.
- edge `.50:80`의 `/metrics`·`/metrics/`를 R1 전과 노출 중 각각1회: **총최대4GET**, 원문 보존·redirect 미추적·재시도 없음.
- 기존 정상 계정의 필요한 파일 공급·한정 조회·실행 증적·자기 임시자원 회수 포함. 실제 R1 직전/종료 직후 관련 시계 원문과 원 서버 journal metadata를 수집한다.
- 정상 image PATCH 최대4회. R1의 명확 실패 때는 이미 반영된 대상의 현행 보상 최대2회(`allow_rollback=true`). R2는 `allow_rollback=false`로 구버전 역복귀를 하지 않는다.

| 대상 | 정확 UID | 이전 digest → 현행 digest |
|---|---|---|
| transaction-api | `8a2af808-ec33-41f2-80b5-addde4e28910` | `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` → `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0` |
| fds-engine | `bf825dec-465b-4603-8b71-f768d195531c` | `5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` → `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d` |

registry는 `10.1.93.54/fds/<service>@sha256:<digest>`이다. 실행 직전 대상·UID·전체 non-image spec·현재 image가 준비 기준과 다르면 중단한다.

## 새로 결속할 별도 현행 복구 범위

정상 회차의 토큰·창 만료 또는 mixed/unknown/보상 실패 시, 위 관리콘솔의 기존 인증으로 **old→current image필드만 대상별최대1회·총2PATCH**를 16:35까지 허용하는 안이다. 이 별도 범위는 아직 승인되지 않았다.

자동 writer의 종료·마지막 요청 결과 판명·새 GET·정확 UID/RV/generation/non-image spec·동일 승인 바이트·잔여시간을 모두 확인한 뒤만 실행한다. 이미 현행인 대상에는 PATCH하지 않는다. 결과 UNKNOWN이면 자동 재시도하지 않고 claim·원문을 보존한다. helper는 남은 구버전2대상876초/1대상568초 예산 미달이면 새 PATCH를 거부한다. 이 예산은 복구 성공 보장이 아니다.

새 Token·권한 확대·rollout undo/restart/force·Pod삭제·호스트 종료·다른 대상·구버전 재적용은 포함하지 않는다. 16:35 만료·승인 철회·대상 불일치 시 추가 PATCH를 중단하고 실제 상태를 인계한다.

## 보안·중단·종료 기준

- 이하영 [조건부 수용](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185120164) 및 [시각 구간 방식 수용](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755)을 적용한다. 정확 PATCH 시각은 미계측이면 NOT_MEASURED, Pod 종료 원값이 없으면 관측 구간으로 기록한다.
- 시계 오차는 시작을 앞당기고 완료를 늦춰 적용한다. 오차·연속성·Run/원본 결속 부족은 **시한 미입증 / SEC 사후 검토**로 기록하며 자동 사고나 PASS로 바꾸지 않는다.
- **실제 P+30 미회수는 즉시 SEC 통지·현행 복원 우선. 16:20 이후 잔여 노출은 수용 밖 사고 기록·SEC 재판단.** 별도16:35 복구 허용은 위험수용 연장이 아니다.
- edge pre 오류는 R1 중단, during 오류는 추가 업무시험/POST 중단·현행 복원 우선. 무리하게 시험 수량을 채우지 않는다. 미수행 검증은 미완료로 남긴다.
- 종료는 현행 양 Deployment Ready3·이전 Pod 부재·업무 metrics404·전용metrics200/target6·실행/원본 결속·허용 임시자원 회수 및 Job/writer 종료를 확인한 뒤 판단한다. Ready3/3만으로 AC09 전체 성공을 선언하지 않는다.
- 기존 Ansible/Harbor 실제 점유가 없음을 창 진입 직전 확인한다. 다른 창은 AC09의 실제 반환 후 배정한다. Phase2 CloudShell Plan 승인은 온프레미스 Runtime 변경 허용으로 전용하지 않는다.

## 검토된 고정 코드·자료

| 항목 | 버전 / SHA256 |
|---|---|
| production source | `fddc76e1c261cd938f06211b7ed035fdcb32e606` |
| R1 plan | `6e622c0bf539830c77cc841beb6852b0db65a9652822754d30141e587ca71d2d` |
| R2 plan | `3b928b2c74600d81066f4577a0b3095df027351434137249a67ef5e328720183` |
| native bundle | `16366261081cf95639480cfb9256255541bc1099fde717225e4ad8f6e322ae8b` |
| console helper | `b01fd209dc089db3ed8da9eca590294d8b36523b119e76af962396d62e11d7f4` |
| edge collector | `0a5e52a99f25cc84b1e48fb815d45035503d16c8e63356d21a9b2a303da38cba` |
| edge launcher | `fbfca05e908262ee5b5bb50a3e43747516d446f996c4c9f7b16b61cd1cda9dd6` |

[상세 실행·복구 명령](../p1-cicd-ac09-preparation-20261015/round5/FINAL_OPERATOR_CARD.md), [수용된 시각 증적 실행 절차](../p1-cicd-ac09-preparation-20261015/round5/TIMING_CONTRACT.md), [수정본 기술 검토](../../reviews/phase1-ac09-helpers-review-20261015/REVIEW_R2.md), [SEC 시각 보완](../../reviews/phase1-sec-20261015/AC09_SEC_TIMING_ADDENDUM.md), [DB 최종 정적 판정](../phase1-ac09-app-evidence-20261015/round3/AC09_DB_DECISION_UPDATE.md). 상세 실행 카드 SHA256 `cda3353af5f5894f6c9a01b1094f79d534f4f71cf2d48ee2773492c4a2986786`, 시각 절차 SHA256 `9e46cd279e618a7d4cafaf989adc0670c3fd3cbd54b46dde5f1663fc964bbf92`를 결속한다. 범위·시간·승인 상태는 이 결정 카드와 실제 최종 승인 기록을 함께 적용한다.

최종 질문 전 확인: 15:20:37 관리 읽기에서 같은 두 UID/현행 digest·각Ready3와 실제3Worker의 Pod6개를 확인했다. 기존 Runner #2 online/idle·Worker process0. 15:23:36 GitHub 상태별 queued/in_progress/waiting/requested/pending 조회는 각각0건이다. [조회 영수증](AC09_ACTIVE_RUNS_PREPARATION.json). 이는 그 시점 준비 관측이며 창 진입 직전 확인을 대신하지 않는다. 시계 읽기6대·원본 journal 수집 경로를 준비했고, 실제 회차 원본은 미수집이다.

15:27 최종 결속: 새 읽기 도구 STATIC9파일·journal 결속 MOCK7 통과(원격 시험0), helper3·plan2·native bundle 불변. 초기 checkout 비교 실패는 CRLF 차이였다. 중앙이 준비 source37/37의 raw bytes를 고정 commit Git blob 및 기존 manifest와 직접 대조해 정확 일치를 확인했다. [원본 결속 확인](AC09_SOURCE_BINDING_RECHECK.json). 실행 파일을 고쳐 일치시키거나 기존 검증 범위를 축소하지 않았다.

실제 승인 JSON/Run/record는 사용자 최종 회신과 이 카드 해시를 결속한 뒤 생성한다. template/이 초안은 실행 승인으로 사용하지 않는다. 코드·대상·범위의 실질 변경은 이 승인을 자동 확장하지 않는다. 실행 결정·실제 결과를 infra-cicd #11에 기록하되 인증정보·private 원본은 공개하지 않는다.
