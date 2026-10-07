#!/usr/bin/env bash
# P1-SEC-01 IF-12B: CP02/CP03 -> Worker 3대 :10250 접속 관측 (읽기 전용 TCP + TLS 핸드셰이크 관측, 설정 변경 없음)
# REV=v1.1-20261007
#
#   k8s-control02 또는 k8s-control03 콘솔(root)에서: bash if12b-cp-to-worker-10250-v1.sh
#
# 범위는 코드에 고정(환경변수 무시): 대상 10.1.93.105/.107/.108, 포트 10250, TCP 제한 5초, TLS 제한 8초, 행당 1회, 재시도 없음.
# TCP 와 TLS 는 별도 명령·별도 원본으로 보존한다. TCP 성공은 TCP 연결만 뜻한다.
# TLS 는 핸드셰이크 결과(Protocol version 줄)만 관측하며 인증서 비교·kubelet 인증·API 호출은 하지 않는다.
# 판정하지 않는다: 출력은 행별 관측 요약일 뿐이며 AC·IF-12B 판정은 Review Owner 몫이다.
# 종료 코드: 0=6행 기록 완료(결과와 무관), 2=STOP(접속 전 중단), 12=기록·봉인 실패
set -uo pipefail
REV="v1.1-20261007"
WORKERS=(10.1.93.105 10.1.93.107 10.1.93.108)
PORT=10250
TCP_TMO=5
TLS_TMO=8

stop() { echo "STOP: $*" >&2; exit 2; }
HN="$(hostname -s 2>/dev/null)"
case "$HN" in k8s-control02|k8s-control03) ;; *) stop "hostname=$HN 은 예상(k8s-control02|k8s-control03)과 다름";; esac
for c in timeout openssl ip sha256sum tar date mktemp; do command -v "$c" >/dev/null 2>&1 || stop "$c 명령 없음"; done
SELF_ERR="$(timeout 2 bash -c 'exec 3<>"/dev/tcp/127.0.0.1/1"' 2>&1)"
case "$SELF_ERR" in *"No such file or directory"*) stop "이 bash 는 /dev/tcp 를 지원하지 않음";; esac

umask 077
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$(mktemp -d "p1-sec01-if12b-$HN-$TS.XXXXXX")" || stop "배타적 출력 폴더를 만들 수 없음"
FAIL=0
w() { printf '%s\n' "$2" >> "$1" 2>/dev/null || { echo "쓰기 실패: $1" >&2; FAIL=1; }; }

w "$OUT/00-environment.txt" "rev=$REV host=$HN started_utc=$TS workers=${WORKERS[*]} port=$PORT"
w "$OUT/00-environment.txt" "script_sha256=$(sha256sum "$0" 2>/dev/null | cut -c1-64)"
w "$OUT/00-environment.txt" "openssl=$(openssl version 2>&1)"

SUMMARY="$OUT/99-summary-provisional.txt"
w "$SUMMARY" "PROVISIONAL=true SEAL_STATUS=PENDING  (관측 요약이며 판정이 아님)"
for W in "${WORKERS[@]}"; do
  D="$OUT/$W"; mkdir "$D" || { FAIL=1; continue; }
  # 실제로 실행하는 고정 명령 문자열을 행별로 보존한다(TCP 와 TLS 는 별개 명령).
  w "$D/cmd.txt" "route: ip -4 route get $W"
  w "$D/cmd.txt" "tcp  : timeout $TCP_TMO bash -c 'exec 3<>\"/dev/tcp/$W/$PORT\"'"
  w "$D/cmd.txt" "tls  : timeout $TLS_TMO openssl s_client -connect $W:$PORT -brief < /dev/null"
  ip -4 route get "$W" > "$D/route.stdout" 2> "$D/route.stderr"; w "$D/route.rc" "$?"
  S1="$(date -u +%FT%TZ)"
  timeout "$TCP_TMO" bash -c 'exec 3<>"/dev/tcp/$1/$2"' _ "$W" "$PORT" > "$D/tcp.stdout" 2> "$D/tcp.stderr"; TCP_RC=$?
  w "$D/tcp.rc" "$TCP_RC"; E1="$(date -u +%FT%TZ)"
  S2="$(date -u +%FT%TZ)"
  timeout "$TLS_TMO" openssl s_client -connect "$W:$PORT" -brief < /dev/null > "$D/tls.stdout" 2> "$D/tls.stderr"; TLS_RC=$?
  w "$D/tls.rc" "$TLS_RC"; E2="$(date -u +%FT%TZ)"
  w "$D/times.txt" "tcp_start=$S1 tcp_end=$E1 tls_start=$S2 tls_end=$E2"
  case "$TCP_RC" in 0) TCP_OBS=TCP_CONNECTED;; 124) TCP_OBS=TCP_TIMEOUT;; *) TCP_OBS=TCP_OTHER;; esac
  if cat "$D/tls.stdout" "$D/tls.stderr" 2>/dev/null | grep -q 'Protocol version:'; then TLS_OBS=TLS_HANDSHAKE_OBSERVED; else TLS_OBS=TLS_HANDSHAKE_NOT_OBSERVED; fi
  SRC="$(sed -n 's/.* src \([0-9.]*\).*/\1/p' "$D/route.stdout" 2>/dev/null | head -1)"
  w "$SUMMARY" "row host=$HN target=$W:$PORT route_src=${SRC:-unknown} tcp_rc=$TCP_RC $TCP_OBS tls_rc=$TLS_RC $TLS_OBS"
done

# 봉인: 내부 목록, tar, sidecar, completion(아카이브 밖)
( cd "$OUT" && find . -type f ! -name SHA256SUMS | LC_ALL=C sort | xargs sha256sum > SHA256SUMS ) || FAIL=1
tar -czf "$OUT.tar.gz" "$OUT" 2>/dev/null || FAIL=1
sha256sum "$OUT.tar.gz" > "$OUT.tar.gz.sha256" 2>/dev/null || FAIL=1
if [ "$FAIL" -eq 0 ]; then ST=COMPLETE; RC=0; else ST=INCOMPLETE; RC=12; fi
printf 'COLLECTOR_STATUS=%s EXIT_CODE=%s REV=%s\n' "$ST" "$RC" "$REV" > "$OUT.completion.txt"
cat "$SUMMARY"; echo "COLLECTOR_STATUS=$ST EXIT_CODE=$RC  out=$OUT"
exit "$RC"
