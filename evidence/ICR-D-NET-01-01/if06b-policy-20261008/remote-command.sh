set -uo pipefail
set +x
umask 077
cd "$1" || exit 2
test "$(hostname -s)" = mgmt-gw01 || exit 2
sha256sum -c SOURCE_SHA256SUMS || exit 2
sudo -v || exit 2
date -u +%FT%TZ > started-utc.txt
sudo python3 "$PWD/collect.py" > collector.stdout 2> collector.stderr
rc=$?
printf '%s\n' "$rc" > collector.rc
cat collector.stdout
cat collector.stderr >&2
OUT=$(sed -n 's/^OUT=//p' collector.stdout | head -1)
[[ "$OUT" =~ ^/root/if06b-policy-[A-Za-z0-9_]+$ ]] || exit 2
# Redirect is performed by the original user into this private staging folder.
# No ownership/mode change to root evidence or system configuration.
sudo -n tar -C /root -czf - "${OUT##*/}" > capture.tar.gz || exit 12
sha256sum capture.tar.gz > capture.tar.gz.sha256 || exit 12
date -u +%FT%TZ > finished-utc.txt
printf 'COLLECTOR_RC=%s (raw results retained even on STOP)\n' "$rc"
