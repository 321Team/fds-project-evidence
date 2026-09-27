# P1-SEC-01 — B2 edge01(승인 source) 30080 Positive 최종 확인 (2026-09-27)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). GWONUK Review Owner 판정의 B2 잔여 요구사항("edge01(10.1.93.50) → local endpoint가 있는 Worker:30080 = OPEN/PASS") 대응. 관련: [B1/B2 evidence PR#54](https://github.com/321Team/fds-project-evidence/pull/54), [이슈 코멘트](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5855138268).

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-b2-edge01-positive-20260927T104621Z.tar.gz` |
| SHA-256 | 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 | edge01, `server08`, 2026-09-27T10:46:21Z (read-only 접속 시험, 변경 없음) |
| 전달 경로 | edge01 → 사용자가 zip으로 압축해 세션에 업로드 → 세션에서 압축 해제 후 SHA-256 재확인 |
| 수집·제공 | 이하영(P1-SEC-01 Lead). 수집·편입 정리는 Claude Code 보조 |

## 수신 검증

- tar.gz 내부 `SHA256SUMS`(1개 파일 대상) 재계산 일치
- 비밀정보 검색: 해당 없음(연결 시험 결과 텍스트만 포함)

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 내용 |
|---|---|
| `b2-edge01-30080-positive.txt` | edge01(승인 source, `10.1.93.50`)에서 워커 3대(`10.1.93.105/107/108`, 각각 `transaction-api` Pod 1개씩 Ready) `:30080` 접속 시험. 3건 전부 `CONNECTED` |

## 배경

[B1/B2 evidence PR#54](https://github.com/321Team/fds-project-evidence/pull/54)의 승인 source 복구(`transaction-api`→ClusterIP, `transaction-api-nodeport`→NodePort 30080-only) 이후, 실제 승인된 접근 경로(edge01)에서 기능 회귀가 없는지 확인이 남아있었다. 이 수집은 그 마지막 Positive 증거다. metrics(9091/32085) 미노출은 [PR#54](https://github.com/321Team/fds-project-evidence/pull/54)의 `b2-svc-after.yaml`로 이미 최종 spec 확인됨(GWONUK 판정: "32085는 현재 Service 레벨에서 listener 자체가 없어졌음을 최종 spec으로 확인").

## 한계

- AC 최종 충족 판정은 이 편입만으로 하지 않는다. 판정은 Review Owner/Lead가 baseline #19에서 별도로 함.

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
