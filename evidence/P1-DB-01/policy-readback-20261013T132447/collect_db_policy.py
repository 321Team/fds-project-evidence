"""One-shot read-only metadata capture; run through the existing control01 route."""
import datetime
import hashlib
import json
import os
import socket
import subprocess
import sys

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

result = {"started_utc": now(), "hostname": socket.gethostname(), "uid": os.getuid(),
          "collector_sha256": os.environ.get("COLLECTOR_SHA256"),
          "scope": "kubectl GET only; no Secret GET, pod exec, traffic probe or server writes",
          "queries": []}
if result["hostname"] != "k8s-control01" or result["uid"] != 0:
    result["error"] = "unexpected host or uid; queries not run"
    print(json.dumps(result))
    sys.exit(5)

queries = [
    ("app_pods_pre", ["pods", "-n", "fds-app"]),
    ("app_np", ["networkpolicies.networking.k8s.io", "-n", "fds-app"]),
    ("calico_np", ["networkpolicies.crd.projectcalico.org", "-A"]),
    ("calico_gnp", ["globalnetworkpolicies.crd.projectcalico.org"]),
    ("calico_tiers", ["tiers.crd.projectcalico.org"]),
    ("namespaces", ["namespaces"]),
    ("app_pods_post", ["pods", "-n", "fds-app"]),
]
for label, args in queries:
    command = ["kubectl", "--kubeconfig=/etc/kubernetes/admin.conf", "--request-timeout=10s",
               "get"] + args + ["-o", "json"]
    rec = {"label": label, "command": command, "started_utc": now()}
    try:
        process = subprocess.run(command, capture_output=True, timeout=15)
        rec.update(rc=process.returncode, stderr=process.stderr.decode(errors="replace"),
                   stdout_sha256=hashlib.sha256(process.stdout).hexdigest())
        if process.returncode == 0:
            data = json.loads(process.stdout)
            rec["list_metadata"] = data.get("metadata", {})
            items = []
            for obj in data.get("items", []):
                meta = obj["metadata"]
                projected = {"apiVersion": obj.get("apiVersion"), "kind": obj["kind"],
                    "metadata": {k: meta[k] for k in
                        ("name", "namespace", "uid", "resourceVersion", "generation", "labels") if k in meta}}
                spec = obj.get("spec", {})
                if obj["kind"] == "Pod":
                    projected["spec"] = {k: spec[k] for k in
                        ("nodeName", "hostNetwork", "serviceAccountName") if k in spec}
                    projected["containers"] = [{k: c[k] for k in ("name", "image", "ports") if k in c}
                        for c in spec.get("containers", [])]
                    status = obj.get("status", {})
                    projected["status"] = {k: status[k] for k in ("phase", "podIP", "hostIP", "conditions") if k in status}
                elif obj["kind"] != "Namespace":
                    projected["spec"] = spec
                items.append(projected)
            rec["items"] = items
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as exc:
        rec.update(rc=124 if isinstance(exc, subprocess.TimeoutExpired) else 2, error=type(exc).__name__)
    rec["finished_utc"] = now()
    result["queries"].append(rec)
result["finished_utc"] = now()
print(json.dumps(result, ensure_ascii=False))
sys.exit(0 if all(q["rc"] == 0 for q in result["queries"]) else 2)
