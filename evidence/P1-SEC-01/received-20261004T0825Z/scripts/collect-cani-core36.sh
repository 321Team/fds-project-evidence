#!/usr/bin/env bash
# P1-SEC-01 core requirement 3 (monitoring-node) and 6 (Runner) read-only can-i check.
# Only runs "kubectl auth can-i" with --as impersonation. Nothing is created or changed.
# Usage on control01:  KUBECTL='sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf' bash collect-cani-core36.sh
set -u
KUBECTL="${KUBECTL:-sudo -n kubectl --kubeconfig=/etc/kubernetes/admin.conf}"
OUT="p1-sec01-cani-core36-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT"
R="$OUT/results.tsv"
printf 'result\texpect\tactual\tsubject\tns\tverb\tresource\tsub\n' > "$R"
{ echo "# $(date -u +%FT%TZ) host=$(hostname)"; $KUBECTL version 2>&1; } > "$OUT/00-environment.txt"
$KUBECTL -n monitoring-node get sa -o name > "$OUT/01-sa-monitoring-node.txt" 2>&1
$KUBECTL -n ci-cd get sa -o name > "$OUT/02-sa-ci-cd.txt" 2>&1

NE=system:serviceaccount:monitoring-node:node-exporter-sa
DEF=system:serviceaccount:default:default
RUN=system:serviceaccount:ci-cd:cicd-runner-sa

check() {  # expect|ns|subject|verb|resource|sub
  local exp="$1" ns="$2" sa="$3" verb="$4" res="$5" sub="$6" args out act r
  args=(auth can-i "$verb" "$res" --as="$sa")
  [ "$ns" = "-" ] && args+=(-A) || args+=(-n "$ns")
  [ -n "$sub" ] && args+=(--subresource="$sub")
  out="$($KUBECTL "${args[@]}" 2>/dev/null | grep -E '^(yes|no)' | head -1)"
  act="${out:-ERROR}"
  r=FAIL; [ "$act" = "$exp" ] && r=PASS
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$r" "$exp" "$act" "$sa" "$ns" "$verb" "$res" "$sub" >> "$R"
}

# core requirement 3: no way to create or modify workloads in monitoring-node
for sa in "$NE" "$DEF"; do
  for res in deployments statefulsets daemonsets jobs cronjobs replicasets pods; do check no monitoring-node "$sa" create "$res" ""; done
  for sub in exec attach portforward; do check no monitoring-node "$sa" create pods "$sub"; done
  for verb in update patch delete; do check no monitoring-node "$sa" "$verb" daemonsets ""; check no monitoring-node "$sa" "$verb" deployments ""; done
  check no monitoring-node "$sa" create serviceaccounts token
  check no monitoring-node "$sa" create rolebindings ""
  check no monitoring-node "$sa" create roles ""
  check no monitoring-node "$sa" get secrets ""
  check no monitoring-node "$sa" list secrets ""
  check no monitoring-node "$sa" '*' '*' ""
  check no - "$sa" create clusterrolebindings ""
  check no - "$sa" bind clusterroles ""
  check no - "$sa" escalate clusterroles ""
  for t in users groups serviceaccounts; do check no - "$sa" impersonate "$t" ""; done
done

# core requirement 6: Runner may only get/update/patch the two existing Deployments in fds-app
for d in transaction-api fds-engine; do
  for verb in get update patch; do check yes fds-app "$RUN" "$verb" "deployment/$d" ""; done
  check no fds-app "$RUN" delete "deployment/$d" ""
done
for verb in get update patch delete; do check no fds-app "$RUN" "$verb" deployment/other-app ""; done
for verb in create list delete; do check no fds-app "$RUN" "$verb" deployments ""; done
for res in statefulsets daemonsets jobs replicasets pods; do check no fds-app "$RUN" create "$res" ""; done
check no fds-app "$RUN" update daemonsets ""
check no fds-app "$RUN" update statefulsets ""
check no fds-app "$RUN" create pods exec
check no fds-app "$RUN" get secrets ""
check no fds-app "$RUN" list secrets ""
check no fds-app "$RUN" create rolebindings ""
check no - "$RUN" create clusterrolebindings ""
check no - "$RUN" bind clusterroles ""
check no - "$RUN" escalate clusterroles ""
check no - "$RUN" impersonate users ""
check no - "$RUN" impersonate serviceaccounts ""
check no kube-system "$RUN" get deployments ""
check no monitoring-api "$RUN" get deployments ""
check no - "$RUN" '*' '*' ""
$KUBECTL auth can-i --list -n fds-app --as="$RUN" > "$OUT/10-runner-list-fds-app.txt" 2>&1
$KUBECTL auth can-i --list -n monitoring-node --as="$NE" > "$OUT/11-nodeexp-list-monitoring-node.txt" 2>&1

P=$(awk -F'\t' 'NR>1&&$1=="PASS"' "$R" | wc -l); F=$(awk -F'\t' 'NR>1&&$1=="FAIL"' "$R" | wc -l)
echo "PASS=$P FAIL=$F" | tee "$OUT/99-summary.txt"
awk -F'\t' 'NR>1&&$1=="FAIL"{print "FAIL: " $4 " " $6 " " $7 " " $8 " (expect " $2 ", actual " $3 ")"}' "$R"
sha256sum "$OUT"/* > "$OUT/SHA256SUMS"
tar czf "$OUT.tar.gz" "$OUT" && sha256sum "$OUT.tar.gz" | tee "$OUT.tar.gz.sha256"
