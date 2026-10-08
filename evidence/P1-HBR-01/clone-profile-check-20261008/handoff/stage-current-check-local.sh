#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
test "$(id -u)" = 0
test "$(hostname -s)" = harbor01
share=/mnt/hbr-check
mountpoint -q "$share"
test ! -e "$share/STARTED"
localdir=$(mktemp -d /root/hbr-check-local-XXXXXXXX)
install -m 600 "$share/run-local.py" "$share/clone-address-trial.py" "$share/expires-epoch.txt" "$share/LOCAL_SHA256SUMS" "$localdir/"
cd "$localdir"
printf '%s  LOCAL_SHA256SUMS\n' 'e1261ab7cee85d6d7863e843fa00fed9c6a16e1179239481aab8d6a5a962126d' | sha256sum -c -
sha256sum -c LOCAL_SHA256SUMS
printf 'LOCAL_COPY_VERIFIED=%s\n' "$localdir"
exec python3 -I "$localdir/run-local.py"
