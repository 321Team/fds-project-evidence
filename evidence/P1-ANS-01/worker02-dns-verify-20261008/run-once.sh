#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
base=/home/server01_ansible/worker02-dns-stage.yJfHG0vS
test "$(id -un)" = server01_ansible
test "$(hostname)" = ansible01
test "$(date +%s)" -lt "$(date -d '2026-10-08T17:28:00+09:00' +%s)"
if pgrep -x ansible-playboo >/dev/null || pgrep -f '^.*[/]ansible-playbook ' >/dev/null; then
  echo 'STOP: other ansible-playbook process'; exit 75
fi
mkdir "$base/runtime-once"
out="$base/runtime-once"
cd "$base/source"
test "$(git rev-parse HEAD)" = 5111c66f233fe0f84e2d63cef3837fe091a2a268
test -z "$(git status --porcelain)"
sha256sum -c ../ANSIBLE_SOURCE_SHA256SUMS > "$out/source-check.txt"
date -Is > "$out/start.txt"
printf '%s\n' 'User confirmed exclusive 15-minute DNS window in chat at 2026-10-08 ~17:17 KST; Edge and related trials paused. Probe excluded.' > "$out/window.txt"
printf '%s\n' 'timeout --signal=TERM --kill-after=10s 120s bash scripts/cr-p1-ans-01-01-run.sh verify-worker02' > "$out/invocation.txt"
export FDS_ANSIBLE_ENGINE_DIR=/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin
export FDS_ANSIBLE_ENGINE_VERSION=2.21.3
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
export ANSIBLE_PRIVATE_KEY_FILE=/home/server01_ansible/.ssh/p1_ansible_ed25519
export CR_EVIDENCE_DIR="$out/wrapper"
set +e
env -i HOME="$HOME" USER=server01_ansible LOGNAME=server01_ansible PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 \
  FDS_ANSIBLE_ENGINE_DIR="$FDS_ANSIBLE_ENGINE_DIR" FDS_ANSIBLE_ENGINE_VERSION="$FDS_ANSIBLE_ENGINE_VERSION" \
  ANSIBLE_CONFIG="$ANSIBLE_CONFIG" ANSIBLE_PRIVATE_KEY_FILE="$ANSIBLE_PRIVATE_KEY_FILE" CR_EVIDENCE_DIR="$CR_EVIDENCE_DIR" \
  timeout --signal=TERM --kill-after=10s 120s bash scripts/cr-p1-ans-01-01-run.sh verify-worker02 > "$out/runtime.stdout" 2> "$out/runtime.stderr"
rc=$?
set -e
printf '%s\n' "$rc" > "$out/runtime.rc"
date -Is > "$out/end.txt"
git status --porcelain > "$out/source-status-after.txt"
git rev-parse HEAD > "$out/source-commit.txt"
cd "$out"
find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
sha256sum -c SHA256SUMS
printf 'RUNTIME_RC=%s EVIDENCE=%s\n' "$rc" "$out"
exit "$rc"
