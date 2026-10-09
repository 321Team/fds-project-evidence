# P1-DB-01 — W4 Edge access log 집계 수신

CODEX_ASSISTED · 이권욱. **2026-10-09 07:45:11 KST** 사용자가 기존 `server08@edge01` 콘솔에서 sudo 인증 후 수집기를 실행했고, 07:45:43 이후 기존 `svc_ansible` SSH 경로로 집계 원본을 회수했다. 새 키/ACL/sudo 정책을 부여하지 않았다. 앞선 접근 거부 기록을 성공으로 덮어쓰지 않고 별도 수집으로 연결한다.

**수집 완료, HTTP 5xx 전체 판정은 `NOT_MEASURED` 유지.** 조회 파일에서 W4 기록이 없다는 사실만 확인했으며 무중단 또는 5xx 0건으로 확대하지 않는다.

## 결과

| 항목 | 값 |
|---|---|
| 대상 구간 | 2026-10-08 20:26:49~20:27:52 KST, 양 끝 포함 |
| 대상 | `/var/log/nginx/*access*`, 발견·조회 9개 |
| 실제 읽은 파일 바이트 | 10,078 bytes, 압축 해제 후 128,503 bytes |
| 파싱 기록 | 1,217개, 미해석 0개 |
| W4 해당 기록 | 0개 |
| 파일 상태 | 9/9 SCANNED, 읽기 전후 동일, byte/time cap 도달·오류 없음 |
| 현재 access.log | 0바이트 |
| access.log-20261009 | 6,697 bytes, 63개 기록. 첫 시각10/8 03:28:01, 마지막10/9 00:28:39 KST. W4 해당 기록 없음 |
| 나머지 rotated gzip 7개 | 8/28~9/29 기록. 파일별 기간은 analysis.json |

`SCANNED`는 고정된 parser가 해당 파일을 끝까지 처리했다는 뜻이다. 실제·역사적 Nginx log_format, access_log 제외 조건, 다른 로그 경로, 모든 업무 요청의 경유·기록 여부는 미확인이다. 그러므로 결과0은 **수집한 파일에 기록된 해당 구간 요청0건**이며, 전체 요청0건·전체5xx0건을 뜻하지 않는다. 과거 기록이 없는 원인을 삭제/미발생/설정 탓 중 하나로 단정하지 않는다.

## 추적성과 재현

- 콘솔에 사용자가 보고한 집계 SHA256과 수신 bytes SHA256이 모두 `f5c970f3c770997aa4acb0643eb0d29ecd3c4df267f7887cb04a1e6d23eff003`으로 일치한다.
- 실행 수집기 SHA256 `cd2205c11461f4c12258ecae62d64051c6f458e41cdd50e1bac1920131f8b750`은 로컬 소스·배치 검증·수신 JSON과 일치한다. `receipt/collector.py`는 **회수기**이며, 실제 집계기는 `edge-w4-access-collector.py`다. 두 파일의 역할·해시를 혼동하지 않는다.
- `operator-report.txt`는 사용자 터미널 전사본이고 서버 원본 터미널 로그가 아니다. 실제 JSON·수신기 stdout/해시/시각/rc는 `receipt/`에 원본 bytes로 보존한다. 실행 원 프로세스 exit code 자체는 전사본에 없으며, 완료표시·결과파일 및 회수 rc0로 수집 완료를 확인했다.
- 원 access log 본문은 Edge에 유지했다. 받은 자료는 호스트가 만든 집계 projection이며 원 access log 사본이 아니다. 파일별 원본 읽기 SHA256은 포함하되, 본문·IP·계정·URL query·referer·User-Agent는 반출하지 않았다.
- `analyze_edge_w4.py receipt/stdout.json` 재실행은 analysis.json과 바이트 일치. `test_edge_w4_access.py`: 로컬 fixture 7건 PASS(시각 경계/UTC/본문 미출력/gzip/미해석/긴 행/용량·시간 한도). 이는 독립 리뷰나 모든 실제 로그 형식의 적합성 증명이 아니다.
- 수집기는 root/edge01/00~09시 gate, 일반 파일 nofollow/noatime, 최대32파일/파일16MiB/총원본64MiB/해제128MiB/60초 상한을 적용했다. 새 민감 데이터 없이 전용 폴더에 mode600 집계 파일1개만 생성했다. 서비스 명령·설정 수정·트래픽 생성·Harbor 작업은 없다.

## 기존 증적과 최종 잔여

[원 실행 #172](https://github.com/321Team/fds-project-evidence/pull/172), [추가 수집 #181](https://github.com/321Team/fds-project-evidence/pull/181)의 Worker CRI0바이트 및 과거 Prometheus 오류카운터0/관측 공백 결과와 함께 판단한다. 세 종류 수집을 수행했으나 W4 전체 HTTP 응답을 복원하지 못했다. **수집 절차 완료와 과거 가용성 인수는 구분한다.**

다른 보존 로그/요청 기록이 있다면 담당자가 출처·대상 구간·coverage를 추가 제시할 수 있다. 없으면 W4 미측정 한계를 유지하고 인수한다. 새 시험으로 과거 미측정을 PASS로 바꾸지 않으며, 이 결과로 DB 위험수용 종료·N1 판정·AC를 바꾸지 않는다. 독립 리뷰는 작업창 종료 후 이재환님께 회수한다. 기존 봉인 파일은 수정하지 않았다.
