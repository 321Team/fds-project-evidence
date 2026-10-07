#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
test "$(hostname -s)" = db01 || { echo 'STOP: not db01'; exit 2; }
date -u +%FT%TZ
hostname -s
sudo -n -v
cd /tmp
sudo -n -u postgres psql -X -q -A -t -v ON_ERROR_STOP=1 -d fdsdb -f - < "$HERE/db-readiness.sql"
echo 'DB_READONLY_ACCESS=READY'
date -u +%FT%TZ
