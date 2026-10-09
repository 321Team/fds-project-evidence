#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
trap 'rc=$?; printf "SSH_SUPPLEMENT_STAGE_STOP line=%s rc=%s\n" "$LINENO" "$rc" >&2' ERR
stop() { printf 'SSH_SUPPLEMENT_STAGE_STOP %s\n' "$1" >&2; exit 2; }
test "$(id -u)" = 0 || stop ROOT_REQUIRED
test "$(hostname -s)" = harbor01 || stop HOST_MISMATCH
share=/mnt/hbr-ssh-supplement
mountpoint -q "$share" || stop SHARE_NOT_MOUNTED
test ! -e "$share/SUPPLEMENT" || stop RECEIPT_ALREADY_EXISTS
test "$(date +%s)" -lt 1791488339 || stop HANDOFF_EXPIRED
localdir=$(mktemp -d /root/hbr-ssh-supplement-local-XXXXXXXX)
for name in supplement.py 90-hbr-no-auto-default.conf.candidate expires-epoch.txt SHA256SUMS; do
    test ! -L "$share/$name" || stop SOURCE_SYMLINK
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' 'cb25bfdd2e1805e6ee4170888955c5357877a42325b1ac88a1a70882baf3c70b' | sha256sum -c -
sha256sum -c SHA256SUMS
python3 -I "$localdir/supplement.py"
