#!/usr/bin/env bash
# Calico HEP/GNP 원문 읽기 전용 수집 (k8s-control01에서 1회, kubeconfig 보유 계정)
# 조회(get)만 실행. apply/edit/delete 없음.
# 사용(ansible01): ansible k8s-control01 -b -m ansible.builtin.script -a "collect-calico.sh <수집자>"
#   → control01 /root/ntp-recapture-calico-<UTC>.tar.gz
# 검증기와 같은 조건(root + /etc/kubernetes/admin.conf, kubectl get만)으로 조회한다.
set -u
umask 077
export LC_ALL=C
COLLECTOR=${1:-${COLLECTOR:-UNSET}}
export KUBECONFIG=${KUBECONFIG:-/etc/kubernetes/admin.conf}
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/root/ntp-recapture-calico-${TS}
mkdir -m 700 "$OUT" || exit 1
cd "$OUT" || exit 1
run() { local key=$1; shift; "$@" > "$key.stdout" 2> "$key.stderr"; echo $? > "$key.rc"; printf '%q ' "$@" > "$key.argv"; }
{ echo "collector=$COLLECTOR"; echo "host=$(hostname -s)"; echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)"; } > meta.txt

# 검증기 전제 확인: kubectl 경로·kubeconfig 존재(내용은 수집하지 않음)
run kubectl-path  /usr/bin/kubectl version --client
run kubeconfig    stat -c "%n %U:%G %a" "$KUBECONFIG"
run hep       kubectl get hostendpoints.crd.projectcalico.org -o yaml
run hep-json  kubectl get hostendpoints.crd.projectcalico.org -o json
run gnp-json  kubectl get globalnetworkpolicies.crd.projectcalico.org -o json
run felix-json kubectl get felixconfigurations.crd.projectcalico.org -o json
run gnp       kubectl get globalnetworkpolicies.crd.projectcalico.org -o yaml
run gns       kubectl get globalnetworksets.crd.projectcalico.org -o yaml
run felixcfg  kubectl get felixconfigurations.crd.projectcalico.org -o yaml
run nodes     kubectl get nodes -o wide --show-labels
# calicoctl이 있으면 v3 API 표현도 함께 (없으면 rc만 남음)
run hep-v3    calicoctl get hostendpoints -o yaml
run gnp-v3    calicoctl get globalnetworkpolicies -o yaml
run felix-v3  calicoctl get felixconfiguration -o yaml

echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)" >> meta.txt
find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
cd .. && tar -czf "$OUT.tar.gz" "$(basename "$OUT")" && chmod 600 "$OUT.tar.gz" && sha256sum "$OUT.tar.gz"
