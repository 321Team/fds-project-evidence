# AC-04 적용 전(before) 도달성 관측 — 2026-10-04 KST

파일은 모두 터미널 출력을 옮긴 것이며 서버 해시 대조는 없다(소량 텍스트).

## 1. TCP 443 도달성 (`timeout 5 bash -c '</dev/tcp/10.1.93.54/443'`)

| 파일 | 출발지 | 시각 | 결과 |
|---|---|---|---|
| `runner-before-20261004T185723.txt` | cicd-runner01 `10.250.10.20` (허용 BASELINE) | 18:57:23 | `OPEN` |
| `ansible01-before-20261004T185905.txt` | ansible01 `10.250.10.10` (MGMT negative) | 18:59:05 | `BLOCKED_OR_UNREACHABLE` |

해석 주의: ansible01의 `BLOCKED`는 **harbor01 호스트 방화벽 결과가 아니다.** 적용 전인데 이미 막혔다. 2026-09-30 수집본(`received-20260930T040033Z`)의 mgmt-gw01 `mgmt-to-physical`(target=DROP)이 관리망에서 harbor01:443을 Runner에만 허용하는 상류 경로 통제로 보이며, 원인을 확정하지는 않았다. 따라서 ansible01은 harbor01 호스트 방화벽의 적용 전후 비교 대상으로 쓰지 않는다.

## 2. same-L2 비승인 출처의 실제 도달 (harbor01 proxy.log)

`harbor01-proxylog-before-20261004T190013.txt`: 2026-10-04 19:00:13 KST harbor01에서 `.26/.29/.30`의 최근 기록 6줄. 18:26~18:57에 `.30`(18:26:55, 18:41:55, 18:56:55)과 `.26`(18:27:24, 18:42:24, 18:57:24)이 HTTP **200**으로 응답을 받았다(15분 주기 `GET /api/v2.0/jobservice/queues`, Referer는 Harbor 웹 화면). 적용 전에 same-L2 비승인 출처 `.26/.30`이 Harbor 443에 도달했다는 증거이며, 적용 후 같은 주소의 신규 기록이 멈추는지가 비교 기준이다. 줄은 `cut -c1-220`으로 잘려 있다.
