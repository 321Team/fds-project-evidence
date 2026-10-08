import base64,hashlib,json,pathlib,shlex,subprocess
r=pathlib.Path(__file__).resolve().parent
ref='95af5b09e50f31f28101fb6f9840aef42c227a3f'
obj=json.loads(subprocess.check_output(['gh','api',f'repos/321Team/infra-kubernetes/contents/ops/edge01-cutover/control01-cutover-check.sh?ref={ref}']))
source=base64.b64decode(obj['content']);(r/'control01-cutover-check.sh').write_bytes(source)
sha=hashlib.sha256(source).hexdigest()
script='''set -euo pipefail
umask 077
test "$(hostname -s)" = k8s-control01
TASK=$(mktemp -d /root/sec19-edge-c0.XXXXXXXX)
cd "$TASK"
base64 -d > control01-cutover-check.sh <<'B64'
'''+base64.b64encode(source).decode()+'''
B64
echo 'SHA  control01-cutover-check.sh' | sha256sum -c -
date -u +%FT%TZ > started-utc.txt
kubectl --kubeconfig=/etc/kubernetes/admin.conf --request-timeout=12s get nodes -o json > nodes-before.json
python3 -c 'import json; d=json.load(open("nodes-before.json"))["items"]; assert len(d)==6 and all(any(c["type"]=="Ready" and c["status"]=="True" for c in n["status"]["conditions"]) for n in d)'
if ss -H -ltn '( sport = :19093 )' | grep -q .; then echo 'STOP port19093 already occupied'; exit 2; fi
set +e
bash control01-cutover-check.sh pre 20261008T0255 > pre.stdout 2> pre.stderr
rc=$?
set -e
printf '%s\n' "$rc" > pre.rc
date -u +%FT%TZ > finished-utc.txt
cat pre.stdout
cat pre.stderr >&2
printf 'TASK_DIR=%s PRE_RC=%s\n' "$TASK" "$rc"
'''.replace('SHA  control',sha+'  control')
(r/'c0-wrapper.sh').write_text(script,encoding='utf8',newline='\n')
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','svc_ansible@10.1.93.102','sudo -n bash -s']
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(inner)],input=script.encode(),capture_output=True,timeout=200)
for ext,b in [('stdout',p.stdout),('stderr',p.stderr),('rc',f'{p.returncode}\n'.encode())]: (r/('c0.'+ext)).write_bytes(b)
print(p.stdout.decode());print(p.stderr.decode());print('transport',p.returncode)
