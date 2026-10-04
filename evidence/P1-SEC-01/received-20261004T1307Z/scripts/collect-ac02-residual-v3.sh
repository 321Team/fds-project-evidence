#!/usr/bin/env bash
# P1-SEC-01 AC-02 residual flows: IF-12B (logs/exec to all 6 nodes), IF-13A (DNS + non-DNS egress deny), IF-03 (fds-engine:8001).
# Read-only: no Pod is created. Only logs/exec and short TCP connect attempts from existing Pods.
# Usage on control01: KUBECTL='sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf' bash collect-ac02-residual.sh
set -u
KUBECTL="${KUBECTL:-sudo -n kubectl --kubeconfig=/etc/kubernetes/admin.conf}"
OUT="p1-sec01-ac02-residual-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT"
R="$OUT/results.tsv"
printf 'result\tflow\ttest\texpect\tactual\tfrom\tto\ttool\n' > "$R"
{ echo "# $(date -u +%FT%TZ) host=$(hostname)"; $KUBECTL version 2>&1; } > "$OUT/00-environment.txt"
$KUBECTL get nodes -o wide > "$OUT/01-nodes.txt" 2>&1
$KUBECTL -n fds-app get pods -o wide > "$OUT/02-fds-app-pods.txt" 2>&1
$KUBECTL -n monitoring-api get pods -o wide > "$OUT/03-monitoring-api-pods.txt" 2>&1

# remote probe script, sent over stdin (sh -s)
cat > "$OUT/probe.sh" <<'PROBE'
H="$1"; P="$2"
if command -v python3 >/dev/null 2>&1; then PY=python3; elif command -v python >/dev/null 2>&1; then PY=python; else PY=""; fi
if [ -n "$PY" ]; then
  $PY -c 'import socket,sys
s=socket.socket(); s.settimeout(3)
try:
    s.connect((sys.argv[1],int(sys.argv[2]))); print("CONNECTED python")
except socket.timeout:
    print("TIMEOUT python")
except ConnectionRefusedError:
    print("REFUSED python")
except Exception as e:
    print("ERROR python " + type(e).__name__)' "$H" "$P"
elif command -v nc >/dev/null 2>&1; then
  S=$(date +%s)
  NO=$(echo | nc -w 3 "$H" "$P" 2>&1); RC=$?
  E=$(date +%s); D=$((E-S))
  if [ "$RC" -eq 0 ]; then echo "CONNECTED nc"
  elif echo "$NO" | grep -qi "refused"; then echo "REFUSED nc"
  elif [ "$D" -ge 2 ]; then echo "TIMEOUT nc"
  else echo "ERROR nc elapsed=${D}s $(echo "$NO" | head -c 60 | tr '\n' ' ')"; fi
else
  echo "NO_TOOL"
fi
PROBE
cat > "$OUT/dns.sh" <<'DNS'
H="$1"
if command -v python3 >/dev/null 2>&1; then PY=python3; elif command -v python >/dev/null 2>&1; then PY=python; else PY=""; fi
if [ -n "$PY" ]; then
  $PY -c 'import socket,sys
try:
    print("RESOLVED python " + socket.gethostbyname(sys.argv[1]))
except Exception as e:
    print("FAILED python " + type(e).__name__)' "$H"
elif command -v getent >/dev/null 2>&1; then
  if getent hosts "$H" >/dev/null 2>&1; then echo "RESOLVED getent"; else echo "FAILED getent"; fi
else
  echo "NO_TOOL"
fi
DNS

podname() { $KUBECTL -n "$1" get pods --no-headers 2>/dev/null | awk -v p="$2" '$1 ~ p && $3=="Running" {print $1; exit}'; }
probe() {  # ns pod host port
  local out; out="$($KUBECTL -n "$1" exec -i "$2" -- sh -s -- "$3" "$4" < "$OUT/probe.sh" 2>&1 | tail -1)"
  case "$out" in *"not found in"*|*"executable file not found"*|*"OCI runtime exec failed"*) out="NO_TOOL";; esac
  echo "${out:-NO_OUTPUT}"
}
dnsprobe() {  # ns pod host
  local out; out="$($KUBECTL -n "$1" exec -i "$2" -- sh -s -- "$3" < "$OUT/dns.sh" 2>&1 | tail -1)"
  case "$out" in *"not found in"*|*"executable file not found"*|*"OCI runtime exec failed"*) out="NO_TOOL";; esac
  echo "${out:-NO_OUTPUT}"
}
rec() {  # flow test expect actual-line from to
  local flow="$1" test="$2" exp="$3" line="$4" from="$5" to="$6" act tool r
  act="${line%% *}"; tool="${line#* }"; [ "$tool" = "$line" ] && tool=""
  # PASS = as expected, FAIL = real mismatch, SKIP = could not run (no tool/shell), CHECK = nc cannot tell timeout from refused
  r=FAIL; [ "$act" = "$exp" ] && r=PASS
  case "$act" in NO_TOOL|NO_OUTPUT) r=SKIP;; esac
  [ "$act" = "NOT_CONNECTED" ] && [ "$exp" = "TIMEOUT" ] && r=CHECK
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$r" "$flow" "$test" "$exp" "$act" "$from" "$to" "$tool" >> "$R"
}

TX="$(podname fds-app transaction-api)"; FE="$(podname fds-app fds-engine)"
DNSIP="$($KUBECTL -n kube-system get svc kube-dns -o jsonpath='{.spec.clusterIP}' 2>/dev/null)"
echo "transaction-api pod=$TX fds-engine pod=$FE kube-dns=$DNSIP" > "$OUT/04-targets.txt"

# IF-12B: CP -> every node :10250 (kubectl logs/exec go apiserver -> kubelet 10250)
$KUBECTL get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName --no-headers 2>/dev/null | awk '$2 ~ /^calico-node/ {print $1, $2, $3}' > "$OUT/05-calico-node-pods.txt"
echo "calico-node pods found: $(wc -l < "$OUT/05-calico-node-pods.txt")" >> "$OUT/04-targets.txt"
while read -r cns pod node; do
  [ -z "$pod" ] && continue
  if $KUBECTL -n "$cns" logs "$pod" --tail=1 > "$OUT/logs-$node.txt" 2>&1; then a=OK; else a=ERROR; fi
  rec IF-12B "logs via apiserver->kubelet" OK "$a" control01 "$node:10250"
  if $KUBECTL -n "$cns" exec "$pod" -- ls / > "$OUT/exec-$node.txt" 2>&1; then a=OK; else a=ERROR; fi
  rec IF-12B "exec via apiserver->kubelet" OK "$a" control01 "$node:10250"
done < "$OUT/05-calico-node-pods.txt"

# IF-13A: workload -> CoreDNS
rec IF-13A "approved pod resolves cluster DNS (UDP/53 via CoreDNS)" RESOLVED "$(dnsprobe fds-app "$FE" kubernetes.default.svc.cluster.local)" "$FE" kubernetes.default
rec IF-13A "approved pod resolves service name" RESOLVED "$(dnsprobe fds-app "$TX" fds-engine.fds-app.svc.cluster.local)" "$TX" fds-engine.fds-app
rec IF-13A "TCP/53 to kube-dns ClusterIP" CONNECTED "$(probe fds-app "$FE" "$DNSIP" 53)" "$FE" "$DNSIP:53"
rec IF-13A "non-DNS egress denied: fds-engine -> transaction-api:8000" TIMEOUT "$(probe fds-app "$FE" transaction-api.fds-app.svc.cluster.local 8000)" "$FE" transaction-api:8000
rec IF-13A "non-DNS egress denied: fds-engine -> db01:5432" TIMEOUT "$(probe fds-app "$FE" 10.1.93.55 5432)" "$FE" 10.1.93.55:5432
rec IF-13A "external DNS server denied: fds-engine -> 8.8.8.8:53" TIMEOUT "$(probe fds-app "$FE" 8.8.8.8 53)" "$FE" 8.8.8.8:53
rec IF-13A "external egress denied: fds-engine -> 1.1.1.1:443" TIMEOUT "$(probe fds-app "$FE" 1.1.1.1 443)" "$FE" 1.1.1.1:443

# IF-03: transaction-api -> fds-engine:8001 (approved) and unapproved Pods -> fds-engine:8001 (denied)
rec IF-03 "approved: transaction-api -> fds-engine:8001" CONNECTED "$(probe fds-app "$TX" fds-engine.fds-app.svc.cluster.local 8001)" "$TX" fds-engine:8001
for app in prometheus alertmanager grafana kube-state-metrics; do
  p="$(podname monitoring-api "$app")"; [ -z "$p" ] && continue
  rec IF-03 "unapproved: monitoring-api/$app -> fds-engine:8001" TIMEOUT "$(probe monitoring-api "$p" fds-engine.fds-app.svc.cluster.local 8001)" "$p" fds-engine:8001
done

P=$(awk -F'\t' 'NR>1&&$1=="PASS"' "$R" | wc -l); F=$(awk -F'\t' 'NR>1&&$1=="FAIL"' "$R" | wc -l)
S=$(awk -F'\t' 'NR>1&&$1=="SKIP"' "$R" | wc -l); C=$(awk -F'\t' 'NR>1&&$1=="CHECK"' "$R" | wc -l)
echo "PASS=$P FAIL=$F SKIP=$S CHECK=$C" | tee "$OUT/99-summary.txt"
awk -F'\t' 'NR>1&&($1=="FAIL"||$1=="SKIP"||$1=="CHECK"){print $1 ": " $2 " | " $3 " | expect " $4 ", actual " $5 " (" $8 ")"}' "$R"
# the unapproved-source negative for IF-03 must have run at least once
N=$(awk -F'\t' 'NR>1&&$2=="IF-03"&&$3 ~ /^unapproved/&&$1=="PASS"' "$R" | wc -l)
echo "IF-03 unapproved negative executed and passed: $N pod(s)" | tee -a "$OUT/99-summary.txt"
sha256sum "$OUT"/* > "$OUT/SHA256SUMS"
tar czf "$OUT.tar.gz" "$OUT" && sha256sum "$OUT.tar.gz" | tee "$OUT.tar.gz.sha256"
