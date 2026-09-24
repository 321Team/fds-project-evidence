# P1-DB-01 — 외부 아티팩트 근거 수신 검토 (2026-09-24)

판정: **참고 사본으로만 편입. 원본 증적이 아니다.** 이 폴더는 [baseline #11](https://github.com/321Team/fds-project-baseline/issues/11) AC "미승인 Source 접속이 거부된다"의 2026-09-23 근거로 연결된 아티팩트를 받아 보존하고, 확인할 수 있는 범위만 대조한 기록이다. AC 판정·Status·Done 여부는 바꾸지 않는다(Lead 이재환 판단).

## 수신 정보

| 항목 | 값 |
|---|---|
| 출처 | `https://claude.ai/artifact/UCatzSQWiTdLxHXzeABRhe` (baseline #11 AC 본문의 "FDS 인프라 검증 시연 아티팩트" 링크) |
| 수신 방식 | Claude Code Artifact read 도구가 저장한 raw HTML. 게시 페이지와 바이트 단위로 동일한지는 확인하지 않았다 |
| 수신 시각 | 2026-09-24T07:55:55Z (저장 파일 시각), 폴더 생성 07:57:14Z |
| 작성자·작성 시각 | **미확인.** 도구는 이 아티팩트를 "조직 밖에서 작성된 공개 아티팩트"로 표시했다. 페이지 제목 "FDS 인프라 검증 시연", 본문 기준일 2026-09-22 |
| 원본 파일 | `artifact/UCatzSQWiTdLxHXzeABRhe.html` — 101,774 bytes, SHA-256 `2d16863a590b1236b7fc37d926c1af73b1d1fd6b4366616f2372a70d13dec015` |
| 발췌 | `CARD_EXTRACT_S1_TC-NET-DB.txt` — 위 HTML의 `S1 / TC-NET-DB` 카드 정의를 글자 그대로 잘라낸 파생 파일(검토 편의용) |

## 아티팩트 성격

- 페이지가 스스로 "기록 재생 — LIVE 아님"이라고 표시한다. 카드는 `evidence_mode: ARCHIVED_RUNTIME`, `verdict: PASS`이다.
- 명령 출력 원문이 없다. `postgresql.conf`의 `listen_addresses`, firewalld public zone, `pg_hba.conf`, `kubectl get networkpolicy -n fds-app` 결과는 **서술만** 있고 실행 로그·시각·실행 계정·해시가 없다.
- 따라서 이 파일은 [EVIDENCE_POLICY](../../../governance/EVIDENCE_POLICY.md)의 원본 증적(실제 시험·로그)에 해당하지 않는다. Hash 일치는 수신 바이트의 무결성만 뜻한다.

## 확인 가능한 범위의 대조

| 아티팩트 서술 | 대조 결과 |
|---|---|
| `fds-msa/kubernetes/base/networkpolicy.yaml`의 `allow-transaction-api-to-db`가 `app: transaction-api`만 선택하고 fds-engine은 db01 egress가 없다 | **정적 확인(부분 일치).** 해당 파일은 현재 `321Team/fds-msa`에서 [`references/upstream/kubernetes/base/networkpolicy.yaml`](https://github.com/321Team/fds-msa/blob/a8c2fc458543e754bd9a17f367e88be317a476b3/references/upstream/kubernetes/base/networkpolicy.yaml)(SHA-256 `bedda0cf85c6d348af523f9a767f630e59fdb18fc99eb1640434fa996fc5ccc3`)에 있다. `default-deny-all`(Ingress+Egress)과 `allow-transaction-api-to-db`(transaction-api → `10.1.93.55/32:5432`)가 있고, fds-engine을 선택해 db01로 나가는 규칙은 없다. 다만 이 파일은 이관 전 앱 저장소의 **참고 사본**이며 namespace는 `fds`다 |
| 실제 클러스터 `fds-app` namespace의 `fds-engine-allow`·`default-deny-all`을 라이브 조회했고 로컬 manifest와 100% 일치 | **확인 불가.** `fds-app` namespace의 `fds-engine-allow` NetworkPolicy는 fds-msa·infra-kubernetes·infra-cicd·infra-ansible main 어디에도 없다(2026-09-24 검색). 조회 출력도 수신되지 않았다 |
| db01 `listen_addresses='*'`, firewalld 5432/tcp 전체 허용, `pg_hba`가 worker01·02·03·edge01로 제한 | **확인 불가.** 서버 설정 원문 미수신 |
| 거부가 Calico REJECT(RST)로 `ConnectionRefusedError`로 나타남 | 기존 [P1-DB-01 증적 R2](https://github.com/321Team/fds-project-evidence/blob/90093f88167055f81e8789d2a848f44ead0ee9ce/docs/evidence/P1-DB-01/evidence-20260907.md#r2--clientfds-engine-직접-db-접근-차단)의 `ConnectionRefusedError` 관측과 같다. 원인(REJECT) 해석을 뒷받침하는 Calico/정책 원문은 미수신 |

## 미수신 원본 (Lead 이재환 제출 요청 대상)

1. `kubectl get networkpolicy -n fds-app -o yaml` 출력(실행 시각·context·계정 포함)과 SHA-256
2. 실제 배포에 사용한 NetworkPolicy manifest의 저장소 경로와 Commit (현재 버전관리 위치 미확인)
3. db01의 `postgresql.conf` `listen_addresses`, `pg_hba.conf` 해당 줄, `firewall-cmd --zone=public --list-all` 출력(비밀값 제외)
4. fds-engine Pod에서 db01:5432 연결 거부 재현 로그(정본 클러스터 기준)

## 보안 참고

이 아티팩트는 공개 링크이며 내부 주소(`10.1.93.x`, `10.250.10.x`)와 DB 접근 통제 구조를 담고 있다. 자격정보 문자열은 발견하지 못했다. 공개 범위 조정 여부는 작성자와 이권욱이 판단한다.

## 이번에 하지 않은 것

- 서버·클러스터 재조회, AC 체크 변경, baseline #11 본문 수정
- 아티팩트 작성자 확인
