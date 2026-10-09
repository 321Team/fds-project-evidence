#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
trap 'rc=$?; printf "TARGET_SYNTAX_STAGE_STOP line=%s rc=%s\n" "$LINENO" "$rc" >&2' ERR
stop() { printf 'TARGET_SYNTAX_STAGE_STOP %s\n' "$1" >&2; exit 2; }
test "$(id -u)" = 0 || stop ROOT_REQUIRED
test "$(hostname -s)" = harbor01 || stop HOST_MISMATCH
share=/mnt/hbr-ssh-syntax
mountpoint -q "$share" || stop SHARE_NOT_MOUNTED
test ! -e "$share/TARGET_SYNTAX" || stop RECEIPT_ALREADY_EXISTS
test "$(date +%s)" -lt 1791487631 || stop HANDOFF_EXPIRED
localdir=$(mktemp -d /root/hbr-ssh-syntax-local-XXXXXXXX)
for name in check.py render-clone-ssh-plan.py expires-epoch.txt source-head.txt SHA256SUMS; do
    test ! -L "$share/$name" || stop SOURCE_SYMLINK
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' '426e364a9b47fd4ec767c5137c9fc03a109bef0f21379d49b6da9f78a2029ee7' | sha256sum -c -
sha256sum -c SHA256SUMS
python3 -I "$localdir/check.py"
