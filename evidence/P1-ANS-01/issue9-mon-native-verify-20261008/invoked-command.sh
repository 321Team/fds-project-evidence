set -eu
umask 077
cd /home/server01_ansible/issue9-native-engine-2rz3_9f4/source
test "$(git rev-parse HEAD)" = da4e273e7e26a9a0b51211e5146066960df072b5
test -z "$(git status --porcelain --untracked-files=no)"
out=$(mktemp -d /home/server01_ansible/issue9-mon-verify.XXXXXXXX)
printf 'EVIDENCE=%s
' "$out"
set +e
timeout --signal=TERM --kill-after=10s 120s env -i PATH=/usr/bin:/bin HOME=/home/server01_ansible LANG=C.UTF-8 LC_ALL=C.UTF-8 ANSIBLE_CONFIG=/home/server01_ansible/issue9-native-engine-2rz3_9f4/source/ansible.cfg ANSIBLE_LOCAL_TEMP="$out/ansible-tmp" ANSIBLE_PRIVATE_KEY_FILE=/home/server01_ansible/.ssh/p1_ansible_ed25519 FDS_ANSIBLE_ENGINE_DIR=/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin FDS_ANSIBLE_ENGINE_VERSION=2.21.3 CR_EVIDENCE_DIR="$out/logs" /bin/bash scripts/cr-p1-mon-01-01-run.sh verify
rc=$?
printf 'RC=%s
' "$rc"
printf '%s
' "$rc" > "$out/operator.rc"
exit "$rc"
