#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
test "$(id -u)" = 0
test "$(hostname -s)" = harbor01
share=/mnt/hbr-a3-diag
mountpoint -q "$share"
test ! -e "$share/A3_DIAGNOSTIC"
test "$(date +%s)" -lt 1791462917
localdir=$(mktemp -d /root/hbr-a3-diag-local-XXXXXXXX)
for name in export.py expires-epoch.txt SHA256SUMS; do
    test ! -L "$share/$name"
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' '8500275b8a7da3ea847b44dc0b268477ec00818f59150bd9b8b44f4ef1381708' | sha256sum -c -
sha256sum -c SHA256SUMS
exec python3 -I "$localdir/export.py"
