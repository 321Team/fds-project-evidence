"""Reproduce only the local evidence comparisons; no network or runtime calls."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "evidence/P1-SEC-01/network-gaps-20261008/policy-post.json"
ARCHIVE = ROOT / "evidence/P1-SEC-01/received-20261004T1307Z/p1-sec01-ac02-residual-20261004T130105Z.tar.gz"
OLD_COMMIT = "6014e9a961af497e78be9c383d270291013db5cf"
ARCHIVE_COMMIT = "7c33d459e009da208b06f9341a7801051a241392"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(item):
    meta = item["metadata"]
    return meta.get("namespace", ""), meta["name"]


def compare(current_items, previous_items):
    current = {identity(x): x for x in current_items}
    previous = {identity(x): x for x in previous_items}
    rows = []
    for key in sorted(current.keys() | previous.keys()):
        row = {"namespace": key[0], "name": key[1],
               "present_current": key in current, "present_previous": key in previous}
        if key in current and key in previous:
            row.update({k + "_equal": current[key]["metadata"].get(k) == previous[key]["metadata"].get(k)
                        for k in ("uid", "resourceVersion", "generation")})
            row["spec_equal"] = current[key].get("spec") == previous[key].get("spec")
        rows.append(row)
    return rows


def main():
    current = json.loads((HERE / "policy-current.json").read_bytes())
    receipt = json.loads((HERE / "capture-receipt.json").read_bytes())
    previous = json.loads(OLD.read_bytes())
    by_label = {q["label"]: q for q in current["queries"]}
    expected_labels = ["app_pods_pre", "app_np", "calico_np", "calico_gnp", "calico_tiers", "namespaces", "app_pods_post"]
    assert [q["label"] for q in current["queries"]] == expected_labels
    assert current["hostname"] == "k8s-control01" and current["uid"] == 0
    assert receipt["rc"] == 0 and all(q["rc"] == 0 for q in current["queries"])
    assert sha(HERE / "collect_db_policy.py") == receipt["source_sha256"] == current["collector_sha256"]
    assert sha(HERE / "policy-current.json") == receipt["stdout_sha256"]
    assert (HERE / "policy-current.stderr").read_bytes() == b""

    def old_items(resource, namespace=None):
        query = next(q for q in previous["queries"] if resource in q["command"])
        assert query["rc"] == 0
        return [x for x in query["items"] if namespace is None or x["metadata"].get("namespace") == namespace]

    archive_sha = sha(ARCHIVE)
    assert archive_sha == "1087547663c339df8167d55056e7cc172bc3b678cffe2e52c172f51eea29ae55"
    member = "p1-sec01-ac02-residual-20261004T130105Z/results.tsv"
    with tarfile.open(ARCHIVE) as archive:
        rows = archive.extractfile(member).read().decode("utf-8").splitlines()
    db_rows = [row for row in rows if "fds-engine -> db01:5432" in row]
    assert len(db_rows) == 1

    pods = by_label["app_pods_pre"]["items"]
    report = {
        "scope": "Evidence continuity and current API configuration only; no AC or packet-enforcement verdict",
        "runtime_read": {
            "hostname": current["hostname"], "uid": current["uid"],
            "server_started_utc": current["started_utc"], "server_finished_utc": current["finished_utc"],
            "client_started_utc": receipt["started_utc"], "client_finished_utc": receipt["finished_utc"],
            "clock_note": "Client and server timestamps are preserved without clock adjustment; clock synchronization was not tested",
            "queries": [{"label": q["label"], "rc": q["rc"], "items": len(q["items"])} for q in current["queries"]],
            "source_sha256_match": True, "received_stdout_sha256_match": True,
            "pods_pre_post_projected_items_equal": pods == by_label["app_pods_post"]["items"],
            "pods": [{"name": x["metadata"]["name"], "uid": x["metadata"]["uid"],
                      "app": x["metadata"].get("labels", {}).get("app"), "node": x["spec"].get("nodeName"),
                      "hostNetwork": x["spec"].get("hostNetwork", False), "phase": x["status"].get("phase")}
                     for x in pods],
        },
        "previous_policy": {"repository": "321Team/fds-project-evidence", "commit": OLD_COMMIT,
                            "path": OLD.relative_to(ROOT).as_posix(), "sha256": sha(OLD)},
        "app_np_comparison": compare(by_label["app_np"]["items"], old_items("networkpolicies.networking.k8s.io", "fds-app")),
        "calico_gnp_comparison": compare(by_label["calico_gnp"]["items"], old_items("globalnetworkpolicies.crd.projectcalico.org")),
        "calico_np_comparison": compare(by_label["calico_np"]["items"], old_items("networkpolicies.crd.projectcalico.org")),
        "historical_engine_db_observation": {"repository": "321Team/fds-project-evidence", "commit": ARCHIVE_COMMIT,
            "path": ARCHIVE.relative_to(ROOT).as_posix(), "sha256": archive_sha,
            "member": member, "original_tsv_row": db_rows[0],
            "scope": "2026-10-04 historical TCP TIMEOUT; not a new 2026-10-13 probe or sole proof of enforcement"},
        "unperformed": ["new TCP/DB transaction probe", "DB host configuration readback", "Calico endpoint/profile/dataplane inspection",
                        "Kubernetes NetworkPolicy inventory outside fds-app", "independent review", "AC acceptance", "ticket closure"],
    }
    sys.stdout.buffer.write((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
