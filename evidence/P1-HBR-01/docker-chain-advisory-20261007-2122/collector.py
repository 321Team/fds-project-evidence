import base64, datetime as dt, hashlib, json, pathlib, shlex, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / ('hbr-chain-readonly-' + dt.datetime.now().strftime('%H%M%S'))
OUT.mkdir()
HEAD = 'da4e273e7e26a9a0b51211e5146066960df072b5'
EXPECTED = '1090de081eb5969f2fc5e1d890f6f022494cf652356a6b8d541be70d6b62d83f'
BASE = '/var/lib/fds-change/P1-HBR-01-AC04'
records = []

def capture(name, command):
    remote = ['ssh', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10', 'svc_ansible@10.1.93.54', command]
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'fds-ansible01', shlex.join(remote)], capture_output=True, timeout=40)
    (OUT / (name + '.stdout')).write_bytes(r.stdout)
    (OUT / (name + '.stderr')).write_bytes(r.stderr)
    records.append(dict(name=name, command=command, start_utc=start, end_utc=dt.datetime.now(dt.timezone.utc).isoformat(), rc=r.returncode, stdout_sha256=hashlib.sha256(r.stdout).hexdigest()))
    (OUT / 'RECEIPT.json').write_text(json.dumps(dict(host='10.1.93.54', account='svc_ansible', source=HEAD, purpose='ADVISORY_ONLY_NOT_START_GATE', commands=records), indent=2)+'\n', encoding='utf-8')
    if r.returncode:
        raise RuntimeError(f'{name}: RC {r.returncode}; STOP')
    return r.stdout

def gh_json(endpoint):
    return json.loads(subprocess.check_output(['gh', 'api', endpoint]))

assert gh_json('repos/321Team/infra-ansible/commits/main')['sha'] == HEAD, 'main changed; STOP'
tool_path = 'tools/p1-hbr-ac04-docker-chain-analysis.py'
obj = gh_json(f'repos/321Team/infra-ansible/contents/{tool_path}?ref={HEAD}')
tool = base64.b64decode(obj['content'])
(OUT / 'analysis-tool.py').write_bytes(tool)
assert capture('hostname', 'hostname -s').strip() == b'harbor01', 'host mismatch; STOP'
capture('host-time', 'date --iso-8601=seconds')
capture('prestate-check', 'sudo -n sh -c ' + shlex.quote(f'cd {BASE} && sha256sum --check --strict PRESTATE_SHA256SUMS'))
original = capture('original-state', f'sudo -n cat {BASE}/original-state.json')
assert hashlib.sha256(original).hexdigest() == EXPECTED, 'original mismatch; STOP'
(OUT / 'original-state.json').write_bytes(original)
capture('prestate-manifest', f'sudo -n cat {BASE}/PRESTATE_SHA256SUMS')
chains = [('forward_rules','filter','FORWARD'), ('docker_user_rules','filter','DOCKER-USER'), ('docker_forward_rules','filter','DOCKER-FORWARD'), ('docker_filter_rules','filter','DOCKER'), ('docker_nat_rules','nat','DOCKER')]
current = {}
for field, table, chain in chains:
    current[field] = capture(field, f'sudo -n iptables -w 5 -t {table} -S {chain}').decode('utf-8').splitlines()
(OUT / 'current-state.json').write_text(json.dumps(current, indent=2)+'\n', encoding='utf-8')
# A second read detects changes during this multi-command advisory capture.
for field, table, chain in chains:
    assert capture(field+'-recheck', f'sudo -n iptables -w 5 -t {table} -S {chain}').decode('utf-8').splitlines() == current[field], 'chain changed during capture; STOP'
capture('original-sha-recheck', f'sudo -n sha256sum {BASE}/original-state.json')
assert (OUT/'original-sha-recheck.stdout').read_text().split()[0] == EXPECTED
r = subprocess.run([sys.executable, '-I', '-B', str(OUT/'analysis-tool.py'), '--original-state', str(OUT/'original-state.json'), '--original-sha256', EXPECTED, '--current-state', str(OUT/'current-state.json')], capture_output=True)
(OUT/'analysis.json').write_bytes(r.stdout)
(OUT/'analysis.stderr').write_bytes(r.stderr)
(OUT/'analysis.rc').write_text(str(r.returncode)+'\n')
result = json.loads(r.stdout)
(OUT/'SOURCE.json').write_text(json.dumps(dict(commit=HEAD, path=tool_path, git_blob=obj['sha'], sha256=hashlib.sha256(tool).hexdigest(), gate=False, runtime_changed=False),indent=2)+'\n',encoding='utf-8')
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file()),encoding='utf-8')
print(json.dumps(dict(output=str(OUT), rc=r.returncode, result=result), ensure_ascii=False, indent=2))
