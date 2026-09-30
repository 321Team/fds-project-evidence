#!/bin/bash
# P1-MON-01 #17 "P0 기본 Dashboard 3종과 기본 Alert Rule을 Source 관리한다" / "monitoring-node 통제 예외" 현장 확인.
# 순수 검증기: kubectl get, Grafana·Prometheus 읽기 API 조회만 한다. 변경·재시작·설치 없음.
# 결과는 이 폴더의 out-<이름>/ 아래에만 남긴다. 사용: bash mon-src-check.sh pre|post
# 기준값 expected.txt = infra-monitoring main e4acbdc(#28 병합 fa208c7 포함)
D=$(cd "$(dirname "$0")" && pwd)
O=$D/out-${1:-run}
mkdir -p "$O"
K="sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf"
NS=monitoring-api

P(){ $K -n $NS exec deploy/prometheus -- wget -qO- -T 10 "http://localhost:9090$1"; }
G(){ $K -n $NS exec deploy/grafana -- env P="$1" sh -c 'wget -qO- -T 10 --header "Authorization: Basic $(printf %s "$GF_SECURITY_ADMIN_USER:$GF_SECURITY_ADMIN_PASSWORD" | base64 | tr -d "\n")" "http://localhost:3000$P"'; }

echo "# $(date -Is) host=$(hostname) user=$(id -un)" | tee "$O/meta.txt"

echo "== 1. ConfigMap 소스 대조 (infra-monitoring main e4acbdc 기준 키별 SHA-256)"
while read ns cm key sha; do
  got=$($K -n "$ns" get configmap "$cm" -o json 2>/dev/null | python3 -c "
import sys, json, hashlib
k = sys.argv[1]
try:
    d = json.load(sys.stdin).get('data', {})
except ValueError:
    d = {}
print(hashlib.sha256(d[k].encode('utf-8')).hexdigest() if k in d else 'MISSING')" "$key")
  if [ "$got" = "$sha" ]; then r=SAME; else r=DIFF; fi
  echo "$r $ns/$cm $key field=${got:0:12} source=${sha:0:12}"
done < "$D/expected.txt" | tee "$O/cm-compare.txt"
for cm in grafana-datasources grafana-dashboards-provider grafana-dashboards prometheus-alert-rules prometheus-alert-rules-optional prometheus-p0-test-alert; do
  $K -n $NS get configmap $cm -o json > "$O/cm-$cm.json" 2>&1
done
python3 - "$O" <<'PY' | tee "$O/cm-keys.txt"
import json, sys, glob, os
for f in sorted(glob.glob(os.path.join(sys.argv[1], "cm-*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
        print(os.path.basename(f)[3:-5], "keys:", sorted(d.get("data", {}).keys()))
    except ValueError:
        print(os.path.basename(f), "읽기 실패")
PY

echo "== 2. Grafana Provisioning"
G '/api/search?type=dash-db' > "$O/grafana-search.json" 2>&1
for uid in $(python3 -c "import json,sys; print(' '.join(x['uid'] for x in json.load(open(sys.argv[1]))))" "$O/grafana-search.json" 2>/dev/null); do
  G "/api/dashboards/uid/$uid" > "$O/grafana-dash-$uid.json" 2>&1
done
python3 - "$O" <<'PY' | tee "$O/grafana-summary.txt"
import json, sys, glob, os
O = sys.argv[1]
try:
    s = json.load(open(os.path.join(O, "grafana-search.json"), encoding="utf-8"))
except ValueError:
    s = []
    print("search 읽기 실패:", open(os.path.join(O, "grafana-search.json"), encoding="utf-8").read()[:200])
for x in s:
    f = os.path.join(O, "grafana-dash-%s.json" % x["uid"])
    try:
        m = json.load(open(f, encoding="utf-8"))["meta"]
        print("uid=%s title=%s provisioned=%s file=%s version=%s" % (x["uid"], x["title"], m.get("provisioned"), m.get("provisionedExternalId"), m.get("version")))
    except (ValueError, KeyError):
        print("uid=%s 상세 읽기 실패" % x["uid"])
print("dashboard 수:", len(s))
PY
G '/api/datasources/uid/prometheus/health' > "$O/grafana-ds-health.json" 2>&1
echo "datasource health: $(cat "$O/grafana-ds-health.json")"

echo "== 3. Prometheus Rule"
P '/api/v1/rules' > "$O/prom-rules.json" 2>&1
python3 - "$O/prom-rules.json" <<'PY' | tee "$O/prom-rules-summary.txt"
import json, sys
try:
    r = json.load(open(sys.argv[1], encoding="utf-8"))["data"]["groups"]
except (ValueError, KeyError):
    r = []
    print("rules 읽기 실패")
for g in r:
    print("group=%s file=%s" % (g["name"], g["file"]))
    for x in g["rules"]:
        lb = x.get("labels") or {}
        print("   %s %s health=%s state=%s severity=%s known_issue=%s" % (x["type"], x["name"], x.get("health"), x.get("state", "-"), lb.get("severity", "-"), lb.get("known_issue", "-")))
PY

echo "== 4. monitoring-node 통제 예외"
$K get ns monitoring-api monitoring-node -o json > "$O/ns.json" 2>&1
$K -n monitoring-node get daemonset,deployment,statefulset,pod -o wide > "$O/monitoring-node-workloads.txt" 2>&1
$K -n monitoring-node get daemonset node-exporter -o json > "$O/node-exporter-ds.json" 2>&1
$K -n monitoring-node get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount,IMAGEID:.status.containerStatuses[0].imageID --no-headers > "$O/node-exporter-pods.txt" 2>&1
P '/api/v1/query?query=node_scrape_collector_success' > "$O/node-collectors.json" 2>&1
python3 - "$O" <<'PY' | tee "$O/node-summary.txt"
import json, sys, os
O = sys.argv[1]
def load(n):
    try:
        return json.load(open(os.path.join(O, n), encoding="utf-8"))
    except ValueError:
        return None
ns = load("ns.json")
for it in (ns or {}).get("items", []):
    lb = it["metadata"].get("labels", {})
    print("ns %s psa enforce=%s audit=%s warn=%s" % (it["metadata"]["name"], lb.get("pod-security.kubernetes.io/enforce"), lb.get("pod-security.kubernetes.io/audit"), lb.get("pod-security.kubernetes.io/warn")))
ds = load("node-exporter-ds.json")
if ds:
    sp = ds["spec"]["template"]["spec"]
    print("hostNetwork=%s hostPID=%s hostIPC=%s serviceAccount=%s automountToken=%s" % (sp.get("hostNetwork"), sp.get("hostPID"), sp.get("hostIPC"), sp.get("serviceAccountName"), sp.get("automountServiceAccountToken")))
    vols = {v["name"]: v.get("hostPath", {}).get("path") for v in sp.get("volumes", [])}
    for c in sp["containers"]:
        print("container=%s image=%s" % (c["name"], c["image"]))
        print("   args=%s" % c.get("args"))
        print("   securityContext=%s" % json.dumps(c.get("securityContext"), sort_keys=True))
        for m in c.get("volumeMounts", []):
            print("   mount %s -> %s readOnly=%s hostPath=%s" % (m["name"], m["mountPath"], m.get("readOnly"), vols.get(m["name"])))
col = load("node-collectors.json")
if col:
    by = {}
    for x in col["data"]["result"]:
        by.setdefault(x["metric"].get("instance"), []).append("%s=%s" % (x["metric"].get("collector"), x["value"][1]))
    for inst in sorted(by):
        print("collectors %s (%d): %s" % (inst, len(by[inst]), " ".join(sorted(by[inst]))))
PY
cat "$O/node-exporter-pods.txt"

echo "== 5. 반영 상태 (Pod 안 파일·reload·rollout)"
{
  echo "prometheus rule file: $($K -n $NS exec deploy/prometheus -- sha256sum /etc/prometheus/rules/alert-rules.yml 2>&1)"
  echo "grafana provider file: $($K -n $NS exec deploy/grafana -- sha256sum /etc/grafana/provisioning/dashboards/provider.yaml 2>&1)"
  echo "prometheus args: $($K -n $NS get deploy prometheus -o jsonpath='{.spec.template.spec.containers[0].args}' 2>&1)"
  echo "prometheus reload metrics:"
  P '/api/v1/query?query=prometheus_config_last_reload_successful' 2>&1; echo
  P '/api/v1/query?query=prometheus_config_last_reload_success_timestamp_seconds' 2>&1; echo
  echo "node_exporter build:"
  P '/api/v1/query?query=node_exporter_build_info' 2>&1; echo
  echo "node-exporter target up:"
  P '/api/v1/query?query=up%7Bjob%3D~%22.*node-exporter.*%22%7D' 2>&1; echo
  echo "daemonset: $($K -n monitoring-node get daemonset node-exporter -o jsonpath='strategy={.spec.updateStrategy} desired={.status.desiredNumberScheduled} updated={.status.updatedNumberScheduled} ready={.status.numberReady} available={.status.numberAvailable} generation={.metadata.generation} observed={.status.observedGeneration}' 2>&1)"
  echo "pods monitoring-api:"
  $K -n $NS get pods -o custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount,START:.status.startTime --no-headers 2>&1
} | tee "$O/apply-state.txt"
echo "DONE dir=$O"
