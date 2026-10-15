## AC09 SEC 시각 증적 사후 판정 — **조건 충족** (이하영)

@GWONUK [실행 결과 6186586952](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186586952)와 [DB 사후 대조 6186849803](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186849803)을 보고 [조건부 수용 6185120164](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185120164)·[구간 증적 방식 6185621755](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755)의 조건별로 사후 판정합니다.

### 시각 판정 (`UNPROVEN_SEC_POST_REVIEW` → SEC 사후 판정)
| 기준 | 관측(보수적 구간) | 상한 | 여유 |
|---|---|---|---|
| R1 PATCH_PENDING 하한 → R2 첫 APPLIED 상한 | 371.1초 (6분 11초) | 15분 | 약 529초 |
| R1 하한 → 복원 조건 관측 상한 | 500.5초 (8분 20초) | 30분 | 약 1,300초 |

- 관측 시점 시계 오차 추정은 0.0027~0.0721초이고, 전후 6호스트가 같은 boot·chrony 동기 상태였습니다. 판정이 뒤집히려면 구간 안에서 시계가 **9분 가까이** 어긋나야 하는데, 그런 근거는 없습니다.
- 엄격한 오차 상한을 수학적으로 입증하지 못했다는 실행자 기록(`UNPROVEN`)은 사실로 그대로 둡니다. 다만 SEC는 이 여유를 근거로 **15/30분 노출 상한을 충족한 것으로 판정**합니다. 사고 처리 대상이 아닙니다.

### 나머지 조건
| 조건 | 판정 |
|---|---|
| 1. 대상 | 승인된 2개 UID·R1 digest 한 회차만 사용(Job 4, TokenRequest 2, 재dispatch 0) — 충족 |
| 2·3. 시간·초과 | W 15:35 → 작업창 반환 16:06:17, 수용 만료 16:20 전 종료. P+30 초과 통지 상황 없음 — 충족 |
| 4. edge 확인 | pre `/metrics`·`/metrics/` 404, 노출 중 `/metrics` 404, `/metrics/` 307 → `Location: http://10.1.93.50/metrics`(다시 edge 404 경로), **200 없음** — 충족 |
| 5. 기록 | 송신값 `NOT_MEASURED`, P 하한·R2 상한·이전 Pod 전체 부재 관측(15:51:34.973)·시계 원문 보존 — 충족 |
| 6. 변경 금지 | NP/GNP·RBAC·edge 정책 변경 보고 없음 — 충족 |

종료 상태(현행 Pod 6개 Ready, 이전 Pod 0, 업무 `/metrics` 404 ×6, 전용 metrics 200 ×6)로 **잔여 노출은 없습니다.** 이번 위험 수용은 16:20에 만료돼 닫혔으며, 다른 회차·이미지에 재사용하지 않습니다.

### 참고
- 공통 transport 영수증의 `PURE_READ_PRECHECK` 표기가 실제 POST와 맞지 않았던 점은, 실제 method 기준으로 거래 쓰기 2건으로 다시 센 처리에 동의합니다. 다음 회차 전에 그 표기를 바로잡아 두면 좋겠습니다(비차단).
- 이 판정은 SEC 시각 조건에 대한 것입니다. AC09 최종 인수와 #11 종결은 Lead의 별도 판단입니다.

AI 사용: CLAUDE_ASSISTED
