#!/usr/bin/env bash
# P1-SEC-01 증적 수집 (읽기 전용 + server-side dry-run). 클러스터를 변경하지 않는다.
# 실행 위치: k8s-control01 (admin.conf 접근 가능한 곳)
# 사용: bash collect-sec01-evidence.sh
#   sudo 비밀번호가 필요한 환경이면 KUBECTL 환경변수로 덮어쓴다.
#   예) KUBECTL="kubectl" bash collect-sec01-evidence.sh
set -u
KUBECTL="${KUBECTL:-sudo -n kubectl --kubeconfig=/etc/kubernetes/admin.conf}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="p1-sec01-late-$TS"
mkdir -p "$OUT"
cd "$OUT" || exit 1

# run <파일명> <명령...> : 명령·시각·stdout/stderr·rc를 한 파일에 그대로 남긴다.
run() {
  local f="$1"; shift
  {
    echo "# collected_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# command: $*"
    "$@" 2>&1
    echo "# rc=$?"
  } > "$f"
}

# 환경
{
  echo "# collected_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# host: $(hostname)"
  $KUBECTL version 2>&1
} > 00-environment.txt

# 1) 네임스페이스 PSA 라벨 (kube-system 포함, version label 여부 확인)
run 10-ns-psa-labels.txt $KUBECTL get ns kube-system fds-app monitoring-api monitoring-node ci-cd --show-labels
run 11-kube-system-ns.yaml $KUBECTL get ns kube-system -o yaml

# 2) CoreDNS 실제 Manifest server-side dry-run
$KUBECTL -n kube-system get deployment coredns -o yaml > 20-coredns-current.yaml 2>&1
run 21-coredns-dry-run.txt $KUBECTL apply --dry-run=server -f 20-coredns-current.yaml

# 3) monitoring-node 신규 Workload 생성 제한 (비승인 SA와 node-exporter-sa 모두 no 기대)
for sa in system:serviceaccount:default:default system:serviceaccount:monitoring-node:node-exporter-sa; do
  for res in deployments daemonsets pods; do
    tag="$(echo "$sa" | awk -F: '{print $3"_"$4}')"
    run "30-monitoring-node_create-${res}_${tag}.txt" $KUBECTL auth can-i create "$res" -n monitoring-node --as="$sa"
  done
done

# 4) 실사용 SA prometheus-sa (monitoring-api) 권한
#    2026-09-27 infra-monitoring#20 로 prometheus -> prometheus-sa 전환, 구 SA `prometheus` 는 삭제됨.
#    구 SA 이름으로 can-i 를 하면 존재하지 않는 SA 라서 의미 없는 'no' 가 나오므로 사용하지 않는다.
P=system:serviceaccount:monitoring-api:prometheus-sa
run 40-prometheus-pod-sa.txt $KUBECTL -n monitoring-api get pod -l app=prometheus -o jsonpath='{.items[0].spec.serviceAccountName}'
run 40b-old-sa-prometheus-absent.txt $KUBECTL -n monitoring-api get sa prometheus
run 41-prometheus-can-i-list.txt $KUBECTL auth can-i --list --as="$P"
run 42-prometheus-nodes-metrics.txt $KUBECTL auth can-i get nodes --subresource=metrics --as="$P"
run 43-prometheus-nodes-proxy.txt $KUBECTL auth can-i get nodes --subresource=proxy --as="$P"
run 44-prometheus-nodes-plain.txt $KUBECTL auth can-i get nodes --as="$P"
run 45-prometheus-secrets-get.txt $KUBECTL auth can-i get secrets -A --as="$P"
run 46-prometheus-secrets-list.txt $KUBECTL auth can-i list secrets -A --as="$P"
run 47-prometheus-clusterrolebinding.yaml $KUBECTL get clusterrolebinding prometheus-sa-kubelet-metrics -o yaml
run 48-prometheus-clusterrole.yaml $KUBECTL get clusterrole prometheus-sa-kubelet-metrics -o yaml
# 알림·대시보드 SA 도 같은 방식으로 실사용 확인
run 49-alertmanager-grafana-sa.txt $KUBECTL -n monitoring-api get pod -l 'app in (alertmanager,grafana)' -o custom-columns=NAME:.metadata.name,SA:.spec.serviceAccountName

# 해시와 아카이브
sha256sum ./* > SHA256SUMS
cd ..
tar czf "$OUT.tar.gz" "$OUT"
sha256sum "$OUT.tar.gz" | tee "$OUT.tar.gz.sha256"
echo "완료: $OUT.tar.gz (+ .sha256)"
