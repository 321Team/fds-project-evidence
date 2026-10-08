#!/bin/bash
# Transfer only: no Docker, service restart, restore or Python invocation.
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
test "$(id -u)" = 0
test "$(hostname -s)" = harbor01
uuid=$(tr 'A-Z' 'a-z' < /sys/class/dmi/id/product_uuid)
case "$uuid" in 564d9e38-f024-efe2-b68f-137a5047788a|389e4d56-24f0-e2ef-b68f-137a5047788a) ;; *) exit 2 ;; esac
test "$(date +%s)" -lt 1791460595
share=/mnt/hbr-a3
mountpoint -q "$share"
test ! -e "$share/STAGED"
dest=/root/hbr-a3-bundle-20261008-192635
test ! -e "$dest"
install -d -m 700 "$dest"
for name in clone-daemon-restart.py trial.py observer.py SHA256SUMS; do
    test ! -L "$share/$name"
    install -m 600 "$share/$name" "$dest/$name"
done
cd "$dest"
printf '%s  SHA256SUMS\n' '07df86d31ae945ab259efaeda9572dda1d2da15db9f9a89886fddb65f317a77e' | sha256sum -c -
sha256sum -c SHA256SUMS
# A receipt means verified copying only, never a service/runtime result.
{ date -u +%FT%TZ; printf 'BUNDLE=%s\nMANIFEST_SHA256=%s\n' "$dest" '07df86d31ae945ab259efaeda9572dda1d2da15db9f9a89886fddb65f317a77e'; sha256sum -c SHA256SUMS; } > "$share/STAGED.pending"
mv "$share/STAGED.pending" "$share/STAGED"
printf 'STAGED_ONLY=%s; wait for host share closure before runtime.\n' "$dest"
