#!/usr/bin/env bash
# P1-SEC-01 Gate 2 원본·보안 후속 읽기 전용 수집기 (evidence #34).
# k8s-control01 root에서 실행한다. 클러스터·파일을 변경하지 않고 새 결과 폴더만 만든다.
# 키·비밀번호 값은 출력하지 않는다. etcd 값은 앞 26바이트(암호화 접두어)만 남긴다.
set -u
umask 077

VERSION="1.0"
LOG_DIR="${LOG_DIR:-$HOME/gate2-final-evidence/logs}"
ENC_CONFIG="${ENC_CONFIG:-/etc/kubernetes/enc/encryption-config.yaml}"
APISERVER_MANIFEST="${APISERVER_MANIFEST:-/etc/kubernetes/manifests/kube-apiserver.yaml}"
ETCD_POD="${ETCD_POD:-etcd-k8s-control01}"
OUT_PARENT="${OUT_PARENT:-$HOME}"
PREFIX="k8s:enc:secretbox:v1:"
export KUBECONFIG="${KUBECONFIG:-/etc/kubernetes/admin.conf}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
NAME="p1-sec-01-originals-$STAMP"
OUT="$OUT_PARENT/$NAME"
mkdir -p "$OUT/gate2-logs" || exit 1

run() {  # run <출력파일> <명령...> : 명령·시각·종료코드를 함께 남긴다
  local file="$OUT/$1"; shift
  {
    printf '# collected_at_utc: %s\n# command: %s\n\n' "$(date -u +%FT%TZ)" "$*"
    "$@" 2>&1
    printf '\n# exit_code: %s\n' "$?"
  } >"$file"
}

etcdctl_() {
  kubectl -n kube-system exec "$ETCD_POD" -- etcdctl \
    --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \
    --cert=/etc/kubernetes/pki/etcd/server.crt \
    --key=/etc/kubernetes/pki/etcd/server.key "$@"
}

# 00 실행 환경
{
  printf 'collector_version: %s\ncollected_at_utc: %s\nhostname: %s\nuser: %s\nkubeconfig: %s\n' \
    "$VERSION" "$STAMP" "$(hostname)" "$(id)" "$KUBECONFIG"
  kubectl version 2>&1
} >"$OUT/00-environment.txt"

# 01 Gate 2 원본 로그 6개: 바이트 그대로 복사하고 9/22 문서의 SHA-256과 대조
cat >"$OUT/01-gate2-expected-SHA256SUMS" <<'EOF'
f0cf80d520e667b18d2121b6bd9a75554dfe376b0eb7a2f2dc12bd45860d89ff  01-namespace-applied.txt
6071675a36f127fa253233c68b3947acb777931b379c27be4b694bbae60d80a4  02-rbac-limitrange-applied.txt
458a3bdc031f9cb5339da1e6eecc05c6a45df065068ed6d9ec0dc64f989c7658  03-networkpolicy-applied.txt
b064b76b3adccc6dc4613ad7f27b63c289e2650601b8fb3b9114a73234b5a34a  04-apiserver-restart-status.txt
7f21c23e55c526d3f93bc607fe87638ef5fa6b9f3213b8e660ef38942d5a9468  05-apiserver-flag-control01.txt
5f98cc4369bad73b5a938cf82fadeaaf05c7c66f852cfcdc0bf74bab4cd038d9  06-history-cleanup-confirmed.txt
EOF
{
  printf '# source_dir: %s\n\n' "$LOG_DIR"
  ls -la --time-style=full-iso "$LOG_DIR" 2>&1
  while read -r _ f; do
    if [ -f "$LOG_DIR/$f" ] && [ ! -L "$LOG_DIR/$f" ]; then
      cp -p "$LOG_DIR/$f" "$OUT/gate2-logs/$f"
    else
      printf 'MISSING_OR_NOT_REGULAR: %s\n' "$f"
    fi
  done <"$OUT/01-gate2-expected-SHA256SUMS"
  printf '\n# sha256sum --check (복사본 기준)\n'
  (cd "$OUT/gate2-logs" && sha256sum --check "$OUT/01-gate2-expected-SHA256SUMS") 2>&1
  printf '# check_exit_code: %s\n' "$?"
} >"$OUT/01-gate2-logs-verify.txt"

# 10 apiserver 암호화 설정: 3대 플래그와 control01 설정 파일 구조(키 값은 가림)
run 10-apiserver-encryption-flag.txt \
  kubectl -n kube-system get pods -l component=kube-apiserver -o wide
{
  printf '\n# control01 %s\n' "$APISERVER_MANIFEST"
  grep -nE 'encryption-provider-config|enc-config|/etc/kubernetes/enc' "$APISERVER_MANIFEST" 2>&1
  for p in $(kubectl -n kube-system get pods -l component=kube-apiserver -o name 2>/dev/null); do
    printf '\n# %s spec.containers[0].command 중 encryption 플래그\n' "$p"
    kubectl -n kube-system get "$p" -o jsonpath='{range .spec.containers[0].command[*]}{@}{"\n"}{end}' \
      | grep -E 'encryption-provider-config' 2>&1
  done
  printf '\n# control01 %s (stat, secret 값은 <REDACTED>)\n' "$ENC_CONFIG"
  stat -c '%n mode=%a owner=%U:%G size=%s mtime=%y' "$ENC_CONFIG" 2>&1
  sed -E 's/^([[:space:]]*secret:).*/\1 <REDACTED>/' "$ENC_CONFIG" 2>&1
} >>"$OUT/10-apiserver-encryption-flag.txt"

# 11 etcd raw: 모든 Secret 키의 저장 접두어(앞 26바이트)만 기록
{
  printf '# collected_at_utc: %s\n# 기대 접두어: %s<keyname>:\n\n' "$(date -u +%FT%TZ)" "$PREFIX"
  keys="$(etcdctl_ get /registry/secrets/ --prefix --keys-only 2>&1 | grep -v '^$')"
  total=0; enc=0
  while read -r k; do
    [ -n "$k" ] || continue
    total=$((total + 1))
    head26="$(etcdctl_ get "$k" --print-value-only 2>/dev/null | head -c 26 | tr -c '[:print:]' '.')"
    case "$head26" in "$PREFIX"*) enc=$((enc + 1)) ;; esac
    printf '%s\t%s\n' "$k" "$head26"
  done <<<"$keys"
  printf '\n# secrets_total: %s\n# secrets_with_secretbox_prefix: %s\n' "$total" "$enc"
} >"$OUT/11-etcd-secret-prefix.txt"

# 20 NodePort 30080 GNP와 HEP 라벨
run 20-gnp-nodeport-30080-allow.yaml \
  kubectl get globalnetworkpolicies.crd.projectcalico.org nodeport-30080-allow -o yaml
run 21-gnp-list.txt kubectl get globalnetworkpolicies.crd.projectcalico.org -o wide
run 22-hep-labels.txt kubectl get hostendpoints.crd.projectcalico.org --show-labels -o wide

# 30 transaction-api·fds-engine 배포 상태
run 30-fds-app-workloads.txt kubectl -n fds-app get deploy,rs,pods,svc -o wide
run 31-fds-app-deploy-images.txt kubectl -n fds-app get deploy \
  -o 'jsonpath={range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[*].image}{"\t"}{.status.readyReplicas}/{.status.replicas}{"\n"}{end}'
run 32-fds-app-secrets-meta.txt kubectl -n fds-app get secrets \
  -o 'custom-columns=NAME:.metadata.name,TYPE:.type,CREATED:.metadata.creationTimestamp,RV:.metadata.resourceVersion'

# 40 control01 history 잔존 확인: 건수만 기록(내용 미출력)
# 현재 설정 파일의 키 값 자체가 history에 남았는지 고정 문자열로 센다. 키가 교체됐다면
# 이전(노출) 키는 이 방법으로 찾을 수 없으므로 ENC_KEY= 줄 수를 함께 남긴다.
{
  printf '# collected_at_utc: %s\n# current_key_lines: 현재 설정 키 값과 같은 문자열을 포함한 줄 수\n# enc_key_assign_lines: ^ENC_KEY= 로 시작하는 줄 수\n\n' "$(date -u +%FT%TZ)"
  keyfile="$(mktemp)"
  sed -nE 's/^[[:space:]]*secret:[[:space:]]*"?([^"[:space:]]+)"?.*/\1/p' "$ENC_CONFIG" >"$keyfile" 2>/dev/null
  printf 'keys_in_config: %s\n' "$(wc -l <"$keyfile")"
  for h in /root/.bash_history /home/*/.bash_history; do
    [ -f "$h" ] || continue
    cur=0
    [ -s "$keyfile" ] && cur="$(grep -cFf "$keyfile" "$h" 2>/dev/null)"
    printf '%s\tcurrent_key_lines=%s\tenc_key_assign_lines=%s\tmtime=%s\n' \
      "$h" "$cur" "$(grep -c '^ENC_KEY=' "$h" 2>/dev/null)" "$(stat -c %y "$h")"
  done
  shred -u "$keyfile" 2>/dev/null || rm -f "$keyfile"
} >"$OUT/40-control01-history-check.txt"

# 결과 Manifest·압축
(cd "$OUT" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum | sed 's#  \./#  #' >SHA256SUMS)
tar -C "$OUT_PARENT" -czf "$OUT.tar.gz" "$NAME"
(cd "$OUT_PARENT" && sha256sum "$NAME.tar.gz" >"$NAME.tar.gz.sha256")
printf 'ARCHIVE=%s\nSIDECAR=%s\n' "$OUT.tar.gz" "$OUT.tar.gz.sha256"
