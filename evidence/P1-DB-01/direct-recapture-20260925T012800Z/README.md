# P1-DB-01 — 직접 재수집 (2026-09-25)

[fds-project-evidence PR #31](https://github.com/321Team/fds-project-evidence/pull/31)에서 지적된 "P1-DB-01 AC 근거가 저장소 밖 claude.ai 아티팩트뿐이고 원본 미수신" 상태를 해소하기 위한 자료다. PR #31이 요청한 원본 4종 중 P1-DB-01 관련 항목을 담당 Lead 본인(이재환, supreme33-kr)이 직접 재수집했다.

## 수집 정보

| 항목 | 값 |
|---|---|
| 대상 | k8s-control01 (kubectl), db01(10.1.93.55) |
| 실행자 | 이재환(supreme33-kr) 본인, control01/db01에 직접 SSH 접속하여 실행 |
| 수집 시각 | 2026-09-25 (KST, 대화 세션 진행 중 실시간 수집) |
| 수집 방식 | 조회 명령만 실행(설정 변경 없음). `pg_hba.conf`/`postgresql.conf` grep, `firewall-cmd --list-all`, `kubectl get networkpolicy`, `kubectl exec`로 거부 재현 |

## 파일 목록

- `pg_hba.txt` — db01 `pg_hba.conf` 허용 규칙 (fds_app 계정, 4개 IP, scram-sha-256/hostssl)
- `postgresql_listen_addresses.txt` — db01 `postgresql.conf`의 `listen_addresses`
- `firewalld.txt` — db01 firewalld 상태 (5432/tcp 포트만 개방, source 미제한 — 실질 통제는 pg_hba/NetworkPolicy)
- `networkpolicy.txt` — `fds-app` 네임스페이스 NetworkPolicy 목록 및 `fds-engine-allow` 전체 YAML
- `rejection-repro.txt` — fds-engine Pod에서 db01:5432로의 미승인 연결 시도 재현 결과(타임아웃)

## 참고 — 예전 기록과의 차이

이전 세션 기록(메모리)에는 차단 지점이 `allow-transaction-api-to-db`라는 정책이 fds-engine을 selector에서 제외하는 방식이라고 되어 있었으나, 이번 재조회 결과 그 이름의 정책은 존재하지 않는다(NotFound). 현재는 `fds-engine-allow`(egress: kube-system DNS만 허용, db01 egress 규칙 없음) + `default-deny-all` 조합으로 동일한 차단 효과를 낸다. `fds`→`fds-app` 네임스페이스 정리 과정에서 구조가 바뀐 것으로 추정된다(결과는 이전과 동일 — fds-engine의 db01 접근은 차단됨).

## 이번에 하지 않은 것

- 설정 변경, Secret 조회/노출, 신규 시험 설계. 전부 조회/재현 명령만 실행.
- 원본 파일 자체(command 출력)를 그대로 텍스트로 저장했으며 편집하지 않았다.

AI 사용: CLAUDE_ASSISTED (담당자 본인이 직접 명령을 실행했고, Claude는 명령 목록 제공·결과 정리·파일화만 수행)
