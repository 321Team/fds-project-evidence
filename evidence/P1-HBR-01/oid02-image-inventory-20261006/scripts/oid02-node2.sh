export PATH=$PATH:/usr/local/bin:/usr/bin:/usr/sbin
echo "# host=$(hostname -s) user=${SUDO_USER:-$(whoami)} time=$(date --iso-8601=seconds)"
echo "== 도구 위치"; command -v ctr crictl nerdctl
echo "== 이미지 (ctr: REF TYPE DIGEST SIZE PLATFORMS)"
ctr -n k8s.io images ls 2>&1 | grep -E "^REF|registry.k8s.io|quay.io/calico|10.1.93.54/fds/calico"
echo "== sandbox(pause) 설정"; grep -n "sandbox" /etc/containerd/config.toml | head -3
echo "(end)"
