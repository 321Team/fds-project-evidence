#!/bin/bash
set -euo pipefail
umask 077
[[ $(id -u) == 0 && $(hostname) == k8s-worker02 ]] || { echo STOP_HOST_OR_ROOT; exit 2; }
command -v python3.12 >/dev/null
stage=/home/svc_ansible/issue9-readonly.ut7KAPGq
archive="$stage/Issue9_Worker02_ReadOnly_ef5adb77.tar.gz"
[[ -f "$archive" && ! -L "$archive" ]] || { echo STOP_ARCHIVE_PATH; exit 2; }
expected=9f8bbc2321e71c8f3313d2f022b34953328c3ff5fc31fca3cc049814fe3d2746
[[ $(sha256sum "$archive" | cut -d ' ' -f1) == "$expected" ]] || { echo STOP_ARCHIVE_HASH; exit 2; }
work=$(mktemp -d /root/issue9-preflight.XXXXXXXX)
cp -- "$archive" "$work/input.tar.gz"
[[ $(sha256sum "$work/input.tar.gz" | cut -d ' ' -f1) == "$expected" ]] || { echo STOP_COPY_HASH; exit 2; }
tar --extract --gzip --file "$work/input.tar.gz" --directory "$work" --no-same-owner --no-same-permissions
cd "$work/Issue9_Worker02_ReadOnly_ef5adb77"
sha256sum -c SHA256SUMS > "$work/source-hash-check.log"
sha256sum -c docs/change/validation/issue-9-key-recovery-inspection/SOURCE_SHA256SUMS >> "$work/source-hash-check.log"
out="$work/evidence"
mkdir -m 700 "$out"
cp "$work/source-hash-check.log" "$out/"
{ date -Is; hostname; id; python3.12 --version; printf '%s\n' 'SOURCE=ef5adb773ff696a60bd5a055a35c7a40c4c4b2ec' 'COMMAND=python3.12 -I -B tools/inspect-worker02-key-recovery.py --read-only' 'SCOPE=READ_ONLY_KEY_RECOVERY_INSPECTION_NO_RESTORE'; } > "$out/context.txt"
set +e
python3.12 -I -B tools/inspect-worker02-key-recovery.py --read-only > "$out/stdout.json" 2> "$out/stderr.log"
rc=$?
set -e
printf '%s\n' "$rc" > "$out/EXIT_CODE"
date -Is > "$out/ended-at.txt"
(cd "$out" && sha256sum context.txt source-hash-check.log stdout.json stderr.log EXIT_CODE ended-at.txt > SHA256SUMS)
tar -czf "$work/worker02-readonly-evidence.tar.gz" -C "$work" evidence
(cd "$work" && sha256sum worker02-readonly-evidence.tar.gz > worker02-readonly-evidence.tar.gz.sha256)
cat "$out/stdout.json"
printf '\nEVIDENCE=%s\nRC=%s\n' "$work/worker02-readonly-evidence.tar.gz" "$rc"
exit "$rc"
