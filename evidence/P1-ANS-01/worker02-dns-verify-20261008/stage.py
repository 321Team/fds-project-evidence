"""Stage reviewed source on controller only. Never contacts managed hosts."""
import datetime, hashlib, json, pathlib, re, subprocess

root = pathlib.Path(__file__).resolve().parent
pack = root.parent / 'probe-ansible-next-20261008'
ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'fds-ansible01']
events = []
def call(label, args):
    p = subprocess.run(args, capture_output=True, timeout=90)
    (root / (label + '.stdout')).write_bytes(p.stdout)
    (root / (label + '.stderr')).write_bytes(p.stderr)
    events.append({'label': label, 'command': args, 'rc': p.returncode,
                   'at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()})
    (root / 'commands.json').write_text(json.dumps(events, indent=2), encoding='utf-8')
    if p.returncode:
        raise RuntimeError(f'{label}: rc={p.returncode}; inspect preserved logs')
    return p.stdout.decode().strip()

bundle = pack / 'ansible-source.bundle'
assert hashlib.sha256(bundle.read_bytes()).hexdigest() == 'a2e6f28f1f62f9ed89d122b83a61c338f68fa9e3594a358f4c0b529196f63853'
remote = call('allocate', ssh + ['umask 077; test "$(id -un)" = server01_ansible && test "$(hostname)" = ansible01 && mktemp -d /home/server01_ansible/worker02-dns-stage.XXXXXXXX'])
assert re.fullmatch('/home/server01_ansible/worker02-dns-stage\\.[A-Za-z0-9]{8}', remote)
(root / 'remote-path.txt').write_text(remote + '\n')
call('transfer', ['scp', '-o', 'BatchMode=yes', str(bundle), str(pack / 'ANSIBLE_SOURCE_SHA256SUMS'), 'fds-ansible01:' + remote + '/'])
script = '''set -Eeuo pipefail
umask 077
cd REMOTE
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
files=subprocess.check_output(['git','ls-files','-z']).decode().split('\\0')
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
printf 'CONTROLLER_STAGE=READY; MANAGED_HOST_CONNECTIONS=0; DNS_RUNTIME=NOT_RUN; WINDOW=NOT_CONFIRMED\\n'
date -Is
'''.replace('REMOTE', remote)
script_path = root / 'stage-controller.sh'
script_path.write_bytes(script.encode())
call('transfer-script', ['scp', '-o', 'BatchMode=yes', str(script_path), 'fds-ansible01:' + remote + '/'])
out = call('controller-stage', ssh + ['bash ' + remote + '/stage-controller.sh'])
print(out)
files = sorted(p for p in root.iterdir() if p.is_file() and p.name != 'SHA256SUMS')
(root / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
