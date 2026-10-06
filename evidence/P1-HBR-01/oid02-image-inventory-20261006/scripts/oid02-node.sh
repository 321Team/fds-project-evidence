export PATH=$PATH:/usr/local/bin:/usr/local/sbin:/usr/sbin
echo "# host=$(hostname -s) user=${SUDO_USER:-$(whoami)} time=$(date --iso-8601=seconds)"
echo "== sandbox(pause) 이미지"; crictl info 2>/dev/null | jq -r '.config.sandboxImage // empty'
echo "== 이미지(id | tags | repoDigests | size)"
crictl images -o json | jq -r '.images[]|select(any((.repoTags//[])[],(.repoDigests//[])[]; test("registry.k8s.io|quay.io/calico|10.1.93.54/fds/calico")))|[.id,((.repoTags//[])|join(",")),((.repoDigests//[])|join(",")),.size]|@tsv'
echo "== static pod 이미지"; grep -h "image:" /etc/kubernetes/manifests/*.yaml 2>/dev/null | sort -u
echo "== 반입 원본 후보(tar 파일, 깊이 3)"; find /root /home /opt /var/tmp /tmp -maxdepth 3 \( -name '*.tar' -o -name '*.tar.gz' -o -name '*.tgz' \) 2>/dev/null | head -20
echo "(end)"
