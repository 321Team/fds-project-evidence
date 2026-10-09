#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
trap 'rc=$?; printf "SSH_NAMING_STAGE_STOP line=%s rc=%s\n" "$LINENO" "$rc" >&2' ERR
stop() { printf 'SSH_NAMING_STAGE_STOP %s\n' "$1" >&2; exit 2; }
test "$(id -u)" = 0 || stop ROOT_REQUIRED
test "$(hostname -s)" = harbor01 || stop HOST_MISMATCH
share=/mnt/hbr-ssh-naming
mountpoint -q "$share" || stop SHARE_NOT_MOUNTED
test ! -e "$share/NAMING_PRECHECK" || stop RECEIPT_ALREADY_EXISTS
test "$(date +%s)" -lt 1791491892 || stop HANDOFF_EXPIRED
localdir=$(mktemp -d /root/hbr-ssh-naming-local-XXXXXXXX)
for name in collect.py expires-epoch.txt SHA256SUMS; do
    test ! -L "$share/$name" || stop SOURCE_SYMLINK
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' '435e36c284c9e6266a0b09017e06fe2e14f20d983aadfcee878bbb3815072659' | sha256sum -c -
sha256sum -c SHA256SUMS
python3 -I "$localdir/collect.py"
