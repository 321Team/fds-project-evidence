#!/usr/bin/env bash
# P1-SEC-01 SEC-AC-05 Secretbox backup 증적 수집 (backup 전용, 클러스터 설정을 바꾸지 않는다)
# 암호화 설정과 apiserver manifest를 root-only로 백업하고 etcd snapshot을 저장·검증한다.
# 키 값은 출력하지 않는다(sha256, mode만). 사용: sudo bash sec01-secretbox-backup.sh
set -u
ENC=/etc/kubernetes/enc/encryption-config.yaml
MANIFEST=/etc/kubernetes/manifests/kube-apiserver.yaml
ADMIN=/etc/kubernetes/admin.conf
KC="kubectl --kubeconfig=$ADMIN"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="/root/p1-sec01-secretbox-backup-$TS"
HOST="$(hostname)"
umask 077
mkdir -p "$OUT"
LOG="$OUT/run.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

etcdctl_in_pod() {
  $KC -n kube-system exec "etcd-$HOST" -- etcdctl --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt \
    --key=/etc/kubernetes/pki/etcd/server.key "$@"
}

if [ "$(id -u)" -ne 0 ]; then echo "root 로 실행하세요: sudo bash $0"; exit 2; fi

say "== backup: host=$HOST"
{
  echo "# collected_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  stat -c '%n mode=%a owner=%U:%G size=%s mtime=%y' "$ENC" "$MANIFEST"
  sha256sum "$ENC" "$MANIFEST"
  ls -l /etc/kubernetes/manifests/kube-apiserver.yaml.bak-preenc 2>&1
} > "$OUT/10-config-state.txt"
cp -p "$ENC" "$OUT/encryption-config.yaml.bak" && chmod 600 "$OUT/encryption-config.yaml.bak"
cp -p "$MANIFEST" "$OUT/kube-apiserver.yaml.bak"
( cd "$OUT" && sha256sum encryption-config.yaml.bak kube-apiserver.yaml.bak > 11-backup-SHA256SUMS && sha256sum -c 11-backup-SHA256SUMS ) > "$OUT/12-backup-verify.txt" 2>&1
etcdctl_in_pod snapshot save /var/lib/etcd/snapshot-sec01.db > "$OUT/20-etcd-snapshot-save.txt" 2>&1
etcdctl_in_pod snapshot status /var/lib/etcd/snapshot-sec01.db -w table > "$OUT/21-etcd-snapshot-status.txt" 2>&1
cp -p /var/lib/etcd/snapshot-sec01.db "$OUT/etcd-snapshot-sec01.db" 2>>"$LOG" && chmod 600 "$OUT/etcd-snapshot-sec01.db"
sha256sum "$OUT/etcd-snapshot-sec01.db" > "$OUT/22-snapshot-SHA256SUMS" 2>&1
say "backup 완료: $OUT"
say "주의: etcd snapshot 과 .bak 파일은 root-only 이며 evidence 저장소에 올리지 않는다(해시·상태 파일만 편입)."

# 아카이브 (키 포함 파일은 제외하고 로그·상태만 묶는다)
ARC="/root/$(basename "$OUT").evidence.tar.gz"
tar czf "$ARC" -C "$(dirname "$OUT")" --exclude='*.bak' --exclude='*.db' "$(basename "$OUT")"
sha256sum "$ARC" | tee "$ARC.sha256"
say "evidence 아카이브(키·snapshot 제외): $ARC"
