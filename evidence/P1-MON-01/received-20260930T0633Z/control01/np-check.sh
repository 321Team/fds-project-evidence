#!/bin/bash
# P1-MON-01 NetworkPolicy 정리(infra-monitoring#25, main d71d00c) 적용 전후 확인.
# 순수 검증기: 조회(kubectl get, Prometheus·Alertmanager·Grafana 읽기 API)와 5초 연결 시도만 한다.
# 객체 생성·변경·삭제, 재시작, 설치는 하지 않는다. 결과는 이 폴더의 <단계>/ 아래에만 남긴다.
# 사용: bash np-check.sh pre   (적용 전)
#       bash np-check.sh post  (적용 후)
PH=${1:?pre 또는 post}
D=$(cd "$(dirname "$0")" && pwd)
O=$D/$PH
mkdir -p "$O"
K="sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf"
NS=monitoring-api

P(){ $K -n $NS exec deploy/prometheus -- wget -qO- -T 10 "http://localhost:9090$1"; }
ms(){ echo "($(( ($(date +%s%N) - $1) / 1000000 ))ms)"; }
hc(){ local t0=$(date +%s%N) r; r=$(timeout 5 bash -c "</dev/tcp/$1/$2" 2>/dev/null && echo OPEN || echo BLOCKED); echo "$r $(ms $t0)"; }
pc(){ $K -n $1 exec deploy/$2 -- python3 -c "import socket
s = socket.socket(); s.settimeout(5)
try:
    s.connect(('$3', $4)); print('OPEN')
except socket.timeout:
    print('TIMEOUT')
except Exception as e:
    print('ERR', type(e).__name__)" 2>&1 | tail -1; }
wx(){ local t0=$(date +%s%N) r; r=$($K -n $NS exec deploy/$1 -- sh -c "wget -q -T 5 -O /dev/null $2 2>&1; echo rc=\$?" 2>&1 | tr -s '\n' ' '); echo "$r$(ms $t0)"; }

echo "# $(date -Is) phase=$PH host=$(hostname) user=$(id -un)" | tee "$O/meta.txt"

# 1) 조회 기록
for n in monitoring-api monitoring-node fds-app; do
  $K -n $n get networkpolicy -o yaml > "$O/np-$n.yaml"
done
$K get networkpolicy -A > "$O/np-list.txt"
P '/api/v1/targets?state=active' > "$O/targets.json"
P '/api/v1/alertmanagers' > "$O/alertmanagers.json"
P '/metrics' | grep -E '^prometheus_(sd_dns_lookup|sd_discovered_targets|notifications_(alertmanagers_discovered|dropped_total|errors_total|sent_total))' > "$O/prom-metrics.txt"
$K -n $NS exec deploy/alertmanager -- wget -qO- -T 10 http://localhost:9093/metrics | grep -E '^alertmanager_notifications_(total|failed_total)' > "$O/am-metrics.txt"
$K -n $NS exec deploy/grafana -- sh -c 'wget -qO- -T 10 --header "Authorization: Basic $(printf %s "$GF_SECURITY_ADMIN_USER:$GF_SECURITY_ADMIN_PASSWORD" | base64 | tr -d "\n")" http://localhost:3000/api/datasources/uid/prometheus/health; echo " rc=$?"' > "$O/grafana-ds-health.txt" 2>&1
$K -n $NS get pods -o custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount,IMAGEID:.status.containerStatuses[0].imageID --no-headers > "$O/pods-monitoring-api.txt"
$K -n fds-app get pods -o wide > "$O/pods-fds-app.txt"
$K -n kube-system get pods -l k8s-app=kube-dns -o wide > "$O/kube-dns-pods.txt"
$K -n kube-system get pods -o custom-columns=HOSTNET:.spec.hostNetwork,IP:.status.podIP,APP:.metadata.labels.k8s-app,NAME:.metadata.name --no-headers > "$O/kube-system-pods.txt"

{
  echo "== targets: health / scrapePool"
  grep -o '"health":"[a-z]*"' "$O/targets.json" | sort | uniq -c
  grep -o '"scrapePool":"[^"]*"' "$O/targets.json" | sort | uniq -c
  echo "== targets: lastError(비어 있지 않은 것)"
  LE=$(grep -oE '"lastError":"([^"\\]|\\.)+"' "$O/targets.json" | sort | uniq -c); echo "${LE:-(없음)}"
  echo "== alertmanagers"; cat "$O/alertmanagers.json"; echo
  echo "== prometheus 자체 지표"; cat "$O/prom-metrics.txt"
  echo "== alertmanager 지표"; cat "$O/am-metrics.txt"
  echo "== grafana datasource health"; cat "$O/grafana-ds-health.txt"
  echo "== monitoring-api pods"; cat "$O/pods-monitoring-api.txt"
  echo "== kube-dns pods"; cat "$O/kube-dns-pods.txt"
  echo "== networkpolicy 수"; tail -n +2 "$O/np-list.txt" | awk '{print $1}' | sort | uniq -c
} 2>&1 | tee "$O/summary.txt"

# 2) 연결 시험 (5초)
TA=$($K -n fds-app get pods -l app=transaction-api -o jsonpath='{.items[0].status.podIP}')
FE=$($K -n fds-app get pods -l app=fds-engine -o jsonpath='{.items[0].status.podIP}')
KS=$(awk '$1=="true"{next} $3=="kube-dns"{next} {print $2; exit}' "$O/kube-system-pods.txt")
{
  echo "# $(date -Is) phase=$PH host=control01(.102, CP) TA=$TA FE=$FE KS=${KS:-없음}"
  echo "## 9/27 evidence#53과 같은 시험"
  for w in 10.1.93.105 10.1.93.107 10.1.93.108; do
    echo "NEG host .102 -> $w:9100 $(hc $w 9100)  (기대 BLOCKED)"
    echo "NEG host .102 -> $w:9101 $(hc $w 9101)  (기대 BLOCKED)"
    echo "POS host .102 -> $w:10250 $(hc $w 10250)  (기대 OPEN)"
  done
  echo "NEG fds-engine -> prometheus.monitoring-api.svc:9090 $(pc fds-app fds-engine prometheus.monitoring-api.svc.cluster.local 9090)  (기대 TIMEOUT)"
  echo "NEG fds-engine -> 10.1.93.105:9100 $(pc fds-app fds-engine 10.1.93.105 9100)  (기대 TIMEOUT)"
  echo "POS grafana -> prometheus:9090 $(wx grafana http://prometheus:9090/)  (기대 rc=0)"
  echo "NEG grafana -> 10.1.93.105:9100 $(wx grafana http://10.1.93.105:9100/)  (기대 timed out)"
  echo "NEG grafana -> kube-state-metrics:8080 $(wx grafana http://kube-state-metrics:8080/)  (기대 timed out)"
  echo "POS prometheus -> 10.1.93.107:9100 $(wx prometheus http://10.1.93.107:9100/)  (기대 rc=0)"
  echo "NEG prometheus -> 10.1.93.107:9101 $(wx prometheus http://10.1.93.107:9101/)  (기대 rc=1)"
  echo "## 필요 경로 양성 (이름으로 새 연결: DNS 해석 + 정책 허용을 함께 확인)"
  echo "POS prometheus -> alertmanager.monitoring-api.svc.cluster.local:9093 $(wx prometheus http://alertmanager.monitoring-api.svc.cluster.local:9093/-/healthy)  (기대 rc=0)"
  echo "POS prometheus -> kube-state-metrics.monitoring-api.svc.cluster.local:8080 $(wx prometheus http://kube-state-metrics.monitoring-api.svc.cluster.local:8080/livez)  (기대 rc=0)"
  echo "POS prometheus -> transaction-api-metrics.fds-app.svc.cluster.local:9091 $(wx prometheus http://transaction-api-metrics.fds-app.svc.cluster.local:9091/metrics)  (기대 rc=0)"
  echo "POS prometheus -> fds-engine-metrics.fds-app.svc.cluster.local:9090 $(wx prometheus http://fds-engine-metrics.fds-app.svc.cluster.local:9090/metrics)  (기대 rc=0)"
  echo "POS grafana -> prometheus.monitoring-api.svc:9090 $(wx grafana http://prometheus.monitoring-api.svc:9090/-/healthy)  (기대 rc=0)"
  echo "POS alertmanager -> 10.1.93.56:3128 $(wx alertmanager http://10.1.93.56:3128/)  (기대 HTTP 오류 응답=연결됨, timed out이면 실패)"
  echo "## 정리로 없어지는 경로 음성"
  if [ -n "$KS" ]; then
    echo "NEG prometheus -> kube-system 비DNS Pod $KS:53 $(wx prometheus http://$KS:53/)  (기대 적용 전 refused=정책 허용, 적용 후 timed out=차단)"
  else
    echo "NEG prometheus -> kube-system 비DNS Pod: 대상 Pod 없음(정적 확인만)"
  fi
  echo "NEG prometheus -> CP 10.1.93.102:9100 $(wx prometheus http://10.1.93.102:9100/)  (기대 적용 후 timed out)"
  echo "NEG prometheus -> transaction-api $TA:9090 $(wx prometheus http://$TA:9090/)  (기대 timed out)"
  echo "NEG prometheus -> fds-engine $FE:9091 $(wx prometheus http://$FE:9091/)  (기대 timed out)"
  echo "INFO namespace fds: $($K get ns fds 2>&1 | tail -1)"
} 2>&1 | tee "$O/np-matrix.txt"
echo "DONE phase=$PH dir=$O"
