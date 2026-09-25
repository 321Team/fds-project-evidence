# P1-E2E-01 — 체크된 AC의 근거 수신 검토 (2026-09-24)

판정: **원본 증적 없음. 참고 사본 연결만 기록한다.** [baseline #20](https://github.com/321Team/fds-project-baseline/issues/20)은 Status가 To Do인데 AC 3개가 체크돼 있다. 각 AC의 근거가 무엇인지 기록한다. AC 판정·Status는 바꾸지 않는다(Lead 이재환 판단).

| AC (체크됨) | Issue에 적힌 근거 | 이 저장소의 대응 |
|---|---|---|
| 정상 거래 E2E가 성공한다 | **없음** | 없음 |
| R01/R02/R04/R07 기대결과가 일치한다 | **없음** | 없음. 같은 아티팩트에 `S7a-E2E / TC-APP-CANON` 카드가 있지만 Issue가 인용하지 않아 연결하지 않았다 |
| 비인가 DB/Management 접근이 차단된다 — DB | 외부 아티팩트 `S1/TC-NET-DB` 카드 | 참고 사본: [`evidence/P1-DB-01/received-20260924T075714Z/CARD_EXTRACT_S1_TC-NET-DB.txt`](../../P1-DB-01/received-20260924T075714Z/CARD_EXTRACT_S1_TC-NET-DB.txt)(SHA-256 `37f471d63999c9563f29db8390c7c18d24e920f52095447305a2bed550597c53`). 대조 결과와 미수신 원본은 그 폴더의 `RECEIPT_REVIEW.md` |
| 같은 AC — Management(SSH) | db01 firewalld rich-rule 서술, K8s 6노드는 "Gate2 A1 9/22 PASS" | db01 firewalld 출력은 미수신. K8s 노드 방화벽 상태는 [`evidence/P1-K8S-01/gate2-final-20260922/`](../../P1-K8S-01/gate2-final-20260922/)에 있으나 이 AC와의 대응은 이번에 검토하지 않았다 |

## 미수신 원본 (Lead 이재환 제출 요청 대상)

1. 정상 거래 E2E 요청·응답과 DB 조회 결과
2. R01/R02/R04/R07 시험 입력·기대값·실제값
3. db01 `firewall-cmd --zone=public --list-all` 출력(비밀값 제외)
4. P1-DB-01 폴더의 미수신 원본 4건

## 이번에 하지 않은 것

- 서버·클러스터 조회, AC 체크·Status 변경, baseline #20 본문 수정
