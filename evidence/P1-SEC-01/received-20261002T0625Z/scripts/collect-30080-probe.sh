#!/usr/bin/env bash
# P1-SEC-01 .50/32 -> Worker:30080 Positive/Negative 접속 시험 (읽기 전용, 설정 변경 없음)
# 같은 스크립트를 "승인 Source(edge01 .50)"와 "비승인 Source(ansible01 .10)"에서 각각 1회 실행한다.
#   edge01 에서:    bash collect-30080-probe.sh approved
#   ansible01 에서: bash collect-30080-probe.sh unapproved
# 판정 기준
#   approved   : 30080 -> CONNECTED (Local 정책상 endpoint 없는 Worker는 REFUSED 가능, 기록만 한다)
#   unapproved : 30080 -> TIMEOUT 기대. 32085 -> TIMEOUT 또는 REFUSED (CONNECTED면 즉시 보고)
# REFUSED를 GNP 차단 PASS로 읽지 않는다 (listener 부재와 구분이 안 됨).
set -u
ROLE="${1:-}"
case "$ROLE" in approved|unapproved) ;; *) echo "사용: $0 approved|unapproved"; exit 2;; esac
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="p1-sec01-30080-$ROLE-$TS"
mkdir -p "$OUT"
{
  echo "# collected_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# host: $(hostname)  role: $ROLE"
  echo "# source_ips: $(hostname -I 2>/dev/null)"
} > "$OUT/00-environment.txt"

RES="$OUT/results.tsv"
printf 'target\tport\tresult\trc\tnote\n' > "$RES"
for ip in 10.1.93.105 10.1.93.107 10.1.93.108; do
  for port in 30080 32085; do
    timeout 3 bash -c "</dev/tcp/$ip/$port" 2>/dev/null
    rc=$?
    case $rc in
      0)   r=CONNECTED ;;
      124) r=TIMEOUT ;;
      *)   r=REFUSED_OR_ERROR ;;
    esac
    printf '%s\t%s\t%s\t%s\t\n' "$ip" "$port" "$r" "$rc" >> "$RES"
  done
done

# HTTP 응답은 approved 에서만 확인 (승인 Source의 정상 응답 대조용)
if [ "$ROLE" = approved ]; then
  for ip in 10.1.93.105 10.1.93.107 10.1.93.108; do
    {
      echo "# curl http://$ip:30080/readyz"
      curl -s -o /dev/null -m 3 -w 'http_code=%{http_code} time=%{time_total}s\n' "http://$ip:30080/readyz" 2>&1
      echo "# rc=$?"
    } > "$OUT/curl_$ip.txt"
  done
fi

cat "$RES"
( cd "$OUT" && sha256sum ./* > SHA256SUMS )
tar czf "$OUT.tar.gz" "$OUT"
sha256sum "$OUT.tar.gz" | tee "$OUT.tar.gz.sha256"
echo "완료: $OUT.tar.gz"
