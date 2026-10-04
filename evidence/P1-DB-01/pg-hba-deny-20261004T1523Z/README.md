# P1-DB-01 — 허용 목록 밖 출발지의 db01 5432 접속 거부 증적 (2026-10-05 00:23~00:25 KST)

[#11 SEC 조건부 위험수용 5980722471](https://github.com/321Team/fds-project-baseline/issues/11#issuecomment-5980722471)의 조건 1("control01에서 5432 접속을 시도해 pg_hba 거부를 캡처")에 대한 수집이다. 수집자는 DB Lead 이재환(supreme33-kr)이다. 해석은 이 README에만 적는다.

**결론:**
- **control01 `.102`**: db01 5432에 **TCP 연결 단계에서 timeout**이 났다. pg_hba까지 도달하지 않았으므로 조건 1이 요구한 "pg_hba 거부" 증적이 되지 않는다.
- **PC `.29`**: 같은 시도에서 TCP 연결은 됐고, PLAIN·SSL 두 경우 모두 **pg_hba 단계에서 거부**됐다(SQLSTATE `28000`). db01 서버 로그에도 같은 시각의 거부 2줄이 남았다.

## 수집 정보

| 출발지 | 시각(KST) | 실행 | 파일 성격 |
|---|---|---|---|
| control01 `10.1.93.102`(계정 `server02`) | 00:23:28 | 사용자가 Chrome 원격 데스크톱으로 실행. 시험 코드는 `pc/probe.py`와 같은 코드를 heredoc으로 붙여넣음 | `control01/0*.txt`는 화면 출력에서 복원한 파일이다. 서버가 출력한 SHA-256(`control01/server-SHA256SUMS`)과 3개 모두 일치한다 |
| PC `10.1.93.29`(개발 PC, db01 VM의 물리 호스트) | 00:24:35 | Claude가 이 PC에서 직접 실행(Windows Python) | `pc/*` 실행 출력 원본(CRLF). `01-route.txt`는 UDP connect로 얻은 출발지 주소다 |
| db01 `10.1.93.55`(계정 `server08`) | 00:23:39, 00:24:35 이후(두 번째 조회 시각은 기록하지 않음) | 사용자가 실행, 조회만 | `db01/transcribed-db01-20261005.txt`는 붙여넣은 출력의 **전사본**이다. 서버 SHA가 없다 |

**시험 방법:** PostgreSQL StartupMessage(`user=fds_app`, `database=fdsdb`)만 보낸다. 비밀번호와 자격증명은 보내지 않는다. 서버 응답이 인증 요청(`R`)이면 pg_hba 허용으로 판정하고 그대로 연결을 닫도록 했다. 같은 출발지에서 PLAIN 한 번, SSLRequest 뒤 TLS로 한 번 시도했다. TLS는 이 시험에서 서버 인증서를 검증하지 않는다(접속 거부만 관찰하므로).

## 결과

| 출발지 | TCP | PLAIN | SSL | db01 로그 |
|---|---|---|---|---|
| control01 `.102` | **timeout(5초)** | `TimeoutError` | `TimeoutError` | `.102` 기록 없음(00:23:39 조회) |
| PC `.29` | 연결됨 | `ErrorResponse S=치명적오류 C=28000` "…암호화 안함 연결에 대한 설정이 pg_hba.conf 파일에 없습니다" | SSLRequest 응답 `S`, TLSv1.3 뒤 `ErrorResponse C=28000` "…SSL 암호화 연결에 대한 설정이 pg_hba.conf 파일에 없습니다" | `00:24:35.219 [56055]`·`00:24:35.309 [56056]` 치명적오류 2줄, 문구 일치 |

`28000`은 `invalid_authorization_specification`이다. 서버 메시지 언어(한국어)와 무관하게 이 SQLSTATE로 판정한다.

## db01 현재 정책 (00:23:39 KST, 전사본)

- pg_hba의 원격 허용은 `hostssl fdsdb fds_app` + `scram-sha-256`, 출발지 `10.1.93.105/107/108/50` 4개뿐이다. 그 밖의 원격 줄은 없다.
- firewalld `public` zone은 `ports: 5432/tcp`를 출발지 제한 없이 열어 두었다. rich rule은 SSH(22)만 있다. [#11 5980438508](https://github.com/321Team/fds-project-baseline/issues/11#issuecomment-5980438508)에 적은 "5432 출발지 제한 미적용" 상태와 같다.

## 해석과 한계

- PC `.29`는 pg_hba 허용 목록 밖 출발지다. 이 결과는 "허용 목록 밖 출발지가 5432에 TCP로 도달해도 인증 단계에서 거부된다"는 수용 위험의 전제를 클라이언트 응답과 서버 로그 양쪽으로 보여 준다.
- control01 `.102`의 timeout은 db01 firewalld(5432 무제한 개방)가 원인이 아니라, 경로 앞단에서 패킷이 버려진 것으로 보인다. 6노드는 firewalld 대신 Calico GlobalNetworkPolicy/HostEndpoint를 쓰므로 control01 egress 정책이 원인일 가능성이 높지만, **정책 조회는 하지 않았다(원인 NOT VERIFIED)**. 이 결과를 db01 쪽 접근통제의 증거로 쓰지 않는다.
- PC `.29`는 db01 VM의 물리 호스트이고 같은 `10.1.93.0/24`에 있다. 다른 망(관리망 `10.250.10.0/24` 등) 출발지는 시험하지 않았다.
- 이 수집은 Phase 1 잔여 위험(인증 계층에만 의존)을 확인한 것이다. 출발지 제한(infra-db#6) 적용 증적이 아니며, P1-DB-01 AC "미승인 Source 접속이 거부된다"의 호스트 계층 근거도 아니다.
- fds-engine 직접 접근 차단은 이 수집 범위가 아니다(기존 `direct-recapture-20260925T0447Z` 참조).

## 파일

| 경로 | 내용 |
|---|---|
| `control01/00-time.txt`, `01-route.txt`, `02-probe.txt` | 시각·호스트명, `ip -4 route get 10.1.93.55`(src `.102`), 시험 출력 |
| `control01/server-SHA256SUMS` | control01이 출력한 3개 파일의 SHA-256 |
| `pc/probe.py` | 실행한 시험 코드 전문 |
| `pc/01-route.txt`, `pc/02-probe.txt` | PC 출발지 주소, 시험 출력 |
| `db01/transcribed-db01-20261005.txt` | pg_hba 유효 줄, firewalld 상태, 로그 grep 2회 (전사본) |
| `SHA256SUMS` | 이 폴더 파일의 SHA-256 |

AI 사용: CLAUDE_ASSISTED (PC 시험 실행, 파일 정리, README 작성)
