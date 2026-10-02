K="kubectl --kubeconfig=/etc/kubernetes/admin.conf -n monitoring-api"
ts() { date '+%F %T %Z'; }
echo "T_PRE $(ts)"; $K get deploy prometheus -o wide; $K get pods -o wide | grep '^prometheus-'
R=$($K get deploy prometheus -o jsonpath='{.spec.replicas}')
if [ "$R" != "1" ]; then echo "ABORT replicas=$R (expected 1)"; exit 1; fi
echo "T_SCALE0 $(ts)"; $K scale deploy/prometheus --replicas=0 || { echo "ABORT scale0 failed"; exit 1; }
for i in $(seq 1 60); do $K get pods --no-headers 2>/dev/null | grep -q '^prometheus-' || break; sleep 2; done
echo "T_POD_GONE $(ts)"
sleep 420
echo "T_SCALE1 $(ts)"; $K scale deploy/prometheus --replicas=1
$K rollout status deploy/prometheus --timeout=300s; echo "T_READY $(ts) rc=$?"
$K get pods -o wide | grep '^prometheus-'; $K get deploy prometheus -o wide
echo "RUN_DONE $(ts)"
