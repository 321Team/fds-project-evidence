#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
trap 'rc=$?; printf "SSH_STAGE_STOP line=%s rc=%s; preserve output, no service changes.\n" "$LINENO" "$rc" >&2' ERR
stop() { printf 'SSH_STAGE_STOP %s\n' "$1" >&2; exit 2; }
test "$(id -u)" = 0 || stop ROOT_REQUIRED
test "$(hostname -s)" = harbor01 || stop HOST_MISMATCH
share=/mnt/hbr-ssh-check
mountpoint -q "$share" || stop SHARE_NOT_MOUNTED
test ! -e "$share/SSH_PRECHECK" || stop RECEIPT_ALREADY_EXISTS
test "$(date +%s)" -lt 1791484037 || stop HANDOFF_EXPIRED
localdir=$(mktemp -d /root/hbr-ssh-check-local-XXXXXXXX)
for name in export.py expires-epoch.txt SHA256SUMS; do
    test ! -L "$share/$name" || stop SOURCE_SYMLINK
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' 'a7531c917567ebdb367747c5f41eeb15d237afc602ddf0061962db3c13abc666' | sha256sum -c -
sha256sum -c SHA256SUMS
python3 -I "$localdir/export.py"
