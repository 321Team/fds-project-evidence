set -Eeuo pipefail
umask 077
cd /home/server01_ansible/worker02-dns-stage.yJfHG0vS
date -Is
test "$(sha256sum ansible-source.bundle | cut -d ' ' -f1)" = a2e6f28f1f62f9ed89d122b83a61c338f68fa9e3594a358f4c0b529196f63853
git init -q source
git -C source config core.autocrlf false
git -C source bundle verify ../ansible-source.bundle
git -C source fetch --no-tags ../ansible-source.bundle refs/remotes/origin/main:refs/heads/prepared-source
git -C source checkout --detach 5111c66f233fe0f84e2d63cef3837fe091a2a268
cd source
git merge-base --is-ancestor 98cf3f826ac0805bcc771ad760a15d931c1bd414 HEAD
test -z "$(git status --porcelain)"
sha256sum -c ../ANSIBLE_SOURCE_SHA256SUMS
python3 - <<'PY'
import subprocess,pathlib
files=subprocess.check_output(['git','ls-files','-z']).decode().split('\0')
count=0
for f in filter(None,files):
    if pathlib.Path(f).read_bytes()!=subprocess.check_output(['git','show','HEAD:'+f]):
        raise SystemExit('BLOB_MISMATCH: '+f)
    count+=1
print('TRACKED_BLOB_MATCHES='+str(count))
PY
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
export FDS_ANSIBLE_ENGINE_DIR=/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin
export FDS_ANSIBLE_ENGINE_VERSION=2.21.3
source scripts/lib/ansible-engine.sh
fds_engine_init
"$FDS_ANSIBLE_ENGINE_DIR/ansible" --version
stat -c '%U %G %a %n' /home/server01_ansible/.ssh/p1_ansible_ed25519 /home/server01_ansible/.ssh/known_hosts
ssh-keygen -F 10.1.93.107 -f /home/server01_ansible/.ssh/known_hosts | ssh-keygen -lf -
printf 'CONTROLLER_STAGE=READY; MANAGED_HOST_CONNECTIONS=0; DNS_RUNTIME=NOT_RUN; WINDOW=NOT_CONFIRMED\n'
date -Is
