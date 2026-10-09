#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
trap 'rc=$?; printf "RECOVERY_EXPORT_STAGE_STOP line=%s rc=%s\n" "$LINENO" "$rc" >&2' ERR
test "$(id -u)" = 0
test "$(hostname -s)" = harbor01
test "$(date +%s)" -lt 1791532800
share=/mnt/hbr-recovery-result
mountpoint -q "$share"
test ! -e "$share/RECOVERY_RESULT"
localdir=$(mktemp -d /root/hbr-recovery-export-local-XXXXXXXX)
for name in export.py expires-epoch.txt SHA256SUMS; do
  test ! -L "$share/$name"
  install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' '96ed2b40e884aa7ddb880dde29bdcc51b4766c7389e5a3d59b969ed5c4d61aeb' | sha256sum -c -
sha256sum -c SHA256SUMS
exec python3 -I "$localdir/export.py"
