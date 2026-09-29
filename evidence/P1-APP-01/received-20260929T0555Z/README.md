# P1-APP-01 — Workload별 Request/Limit 부하 시험 (2026-09-29 14:53~15:01 KST)

APP Lead(이재환)가 정본 클러스터의 transaction-api·fds-engine에 3단계 부하를 주고 Pod별 CPU·메모리·CPU 스로틀링과 클라이언트 응답을 관측했다. 합격 산식은 시험 전에 edge01 서버 파일로 기록했다. 명령은 담당자가 k8s-control01(`server02`), edge01(`server08`)에서 직접 실행했다.

**운영 변경:** 없음(Deployment·Resource·replica 변경 없음). 시험 거래 6,750건(`SIM_load_202609291455_<n>`, 10,000원)이 운영 `fdsdb`에 남아 있다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-app-load-20260929/` (`q.py`, `env-before.txt`, `metrics.log`, `env-after.txt`) | `load-control01.tar.xz` 1,988 B, SHA-256 `d9d54d90…d87f7685` | 서버 `sha256sum`과 수신 archive 일치. 개별 파일 4개는 archive 내부와 바이트 동일 |
| `edge01/` | `~/p1-app-load-202609291455/` (`criteria.txt`·`criteria.sha256`, `gen.py`, `stages.log`, `summary.txt`, `requests.log` 6,750줄·`requests.sha256`) | `load-edge01-full.tar.xz` 26,420 B, SHA-256 `f7cc07c9…00bf7ba4f` / `load-edge01.tgz`(requests.log 제외본) SHA-256 `fbb72570…5c76f4c1` | 두 archive 모두 서버 `sha256sum`과 일치. 개별 파일 7개는 전체본 archive 내부와 바이트 동일, 제외본의 6개 파일도 동일. `requests.log` SHA-256 `b608b19e…230a0877cb`는 서버에서 기록한 `requests.sha256`과 일치 |

- 서버의 파일명은 `load-control01.txz`, `load-edge01-full.txz`다. 증적 도구가 `.tar.xz` 확장자를 archive로 인식하므로 **바이트는 그대로 두고 이름만** `.tar.xz`로 바꿨다(sidecar·`ARCHIVE_CONTENTS`는 바꾼 이름 기준).
- control01은 처음에 gzip 묶음(서버 SHA-256 `92455624…`)으로 받았으나 base64를 옮겨 적는 과정에서 반복 구간이 어긋나 복원에 실패했다. 서버에서 같은 폴더를 xz로 다시 묶어 받은 것이 위 `load-control01.tar.xz`다. 실패한 묶음은 편입하지 않았다.

## 시험 설계 (`edge01/criteria.txt`, 시험 전 기록 — SHA-256 `3fd227e2…`)

- 단계: S1 5 rps·90초 → S2 20 rps·90초 → S3 50 rps·90초. edge01 → Worker `:30080`(`.105/.107/.108` 순환), 요청마다 새 계정, 입금 60%·출금 20%·이체 20%, 금액 10,000원(`edge01/gen.py`)
- 관측: control01에서 Prometheus 15초 간격 Pod별 `rate(container_cpu_usage_seconds_total[1m])`, `container_memory_working_set_bytes`, CFS throttling 비율(`control01/q.py`, `metrics.log`) / edge01에서 단계별 처리량·상태코드·지연
- 시험 전 값: 두 서비스 모두 requests 250m/256Mi, limits 500m/512Mi(`control01/env-before.txt`)
- 산식: CPU request = S2 최대 ×1.5(50m 올림, 최소 100m) / CPU limit = S3 최대 ×2(100m 올림), throttling 25% 이상이면 부족 / 메모리 request = 전 구간 최대 ×1.2(64Mi 올림), limit = request ×2
- 판정: 현재 값 ≥ 산식, throttling < 25%, 오류 0, 재시작·OOM 0이면 현재 값 유지 확정. p95는 정본 기준이 없어 기록만 한다.

## 결과

**클라이언트 (`edge01/stages.log`, `summary.txt`, `requests.log`)**

| 단계 | 시각(KST) | 요청 | 처리량 | 상태 | p50 / p95 / p99 / max (ms) |
|---|---|---|---|---|---|
| S1 | 14:55:06~14:56:36 | 450 | 5.0 rps | 201×450 | 24.3 / 28.2 / 34.6 / 50.3 |
| S2 | 14:56:36~14:58:06 | 1,800 | 20.0 rps | 201×1,800 | 23.3 / 26.7 / 29.6 / 60.9 |
| S3 | 14:58:06~14:59:36 | 4,500 | 50.0 rps | 201×4,500 | 19.0 / 24.9 / 29.3 / 47.3 |

Worker별 요청은 단계마다 정확히 3등분됐다(S3 1,500×3).

**자원 (`control01/metrics.log`)** — CPU는 1분 평균이라 1분 창이 해당 단계 안에 완전히 들어간 측정값의 최대를 썼다.

| 워크로드 | S1 CPU | S2 CPU | S3 CPU | 메모리 최대 | 스로틀링 |
|---|---|---|---|---|---|
| transaction-api (Pod 3) | 24.0m | 89.5m | **174.4m** | **121.5MiB** | 0 |
| fds-engine (Pod 3) | 3.3m | 7.2m | 16.2m | 69.7MiB | 0 |

**Pod (`env-before.txt` → `env-after.txt`):** restartCount 전후 동일(fds-engine 0/2/0, transaction-api 0/0/1). `LAST=Unknown`은 시험 전부터 있던 재시작 기록이다.

## 산식 적용

| 워크로드 | CPU request | CPU limit | 메모리 request | 메모리 limit | 판정 |
|---|---|---|---|---|---|
| transaction-api | 89.5×1.5 → 150m ≤ 250m | 174.4×2 → 400m ≤ 500m | 121.5×1.2 → 192Mi ≤ 256Mi | 384Mi ≤ 512Mi | 유지 |
| fds-engine | 최소 100m ≤ 250m | 100m ≤ 500m | 128Mi ≤ 256Mi | 256Mi ≤ 512Mi | 유지 |

오류 0, 스로틀링 0, 재시작·OOM 0이므로 기준에 따라 **현재 값(250m/500m, 256Mi/512Mi) 유지로 확정**한다.

## 한계와 후속

- 50 rps까지만 시험했다. 그 이상 처리량과 한계점은 확인하지 않았다.
- fds-engine은 50 rps에서도 CPU 16.2m·메모리 69.7MiB로 여유가 크다. 산식상 100m/128Mi로 줄여도 되지만 기준 판정은 "유지"이며, 조정은 별도 제안 사항이다.
- 경로는 edge01 → Worker NodePort 직접이다(edge01 nginx :80 이관 전).
- 10/5 이미지 전환 후 자원 특성이 달라질 수 있다.
- 시험 거래 6,750건이 운영 DB에 남아 있다(`SIM_load_` 접두사).

AI 사용: CLAUDE_ASSISTED (명령·부하 생성기·판정 산식 준비, 수신 대조·재계산·문서화, 서버 명령 실행은 담당자 본인)
