#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
test "$(id -u)" = 0
test "$(hostname -s)" = harbor01
share=/mnt/hbr-a3-result
mountpoint -q "$share"
test ! -e "$share/A3_STOP"
test "$(date +%s)" -lt 1791462204
localdir=$(mktemp -d /root/hbr-a3-export-local-XXXXXXXX)
for name in export.py expires-epoch.txt SHA256SUMS; do
    test ! -L "$share/$name"
    install -m 600 "$share/$name" "$localdir/$name"
done
cd "$localdir"
printf '%s  SHA256SUMS\n' '20074c035ff564f4b35284b7c59594984cc6502f6ace9ebe042481937952e300' | sha256sum -c -
sha256sum -c SHA256SUMS
exec python3 -I "$localdir/export.py"
