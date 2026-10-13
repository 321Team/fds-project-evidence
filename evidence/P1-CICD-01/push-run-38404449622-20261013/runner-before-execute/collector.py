"""Bounded read-only preparation. No registry authentication or workflow dispatch."""
import datetime, hashlib, json, os, pathlib, socket, ssl, stat, subprocess, urllib.request

assert socket.gethostname() == 'cicd-runner01' and os.getuid() == 1000
home = pathlib.Path('/home/server01_cicd-runner')
out = {'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'host': socket.gethostname(), 'uid': os.getuid(), 'read_only': True,
       'push': 'NOT_EXECUTED', 'registry_authentication': 'NOT_TESTED'}
out['paths'] = {}
for p in (home, home/'FDS_CICD_PushInputs', home/'FDS_CICD_PushClaims'):
    s = p.lstat()
    assert stat.S_ISDIR(s.st_mode) and s.st_uid == 1000 and stat.S_IMODE(s.st_mode) == 0o700
    out['paths'][p.name] = {'uid': s.st_uid, 'mode': oct(stat.S_IMODE(s.st_mode)), 'symlink': False}
out['previous_claims'] = []
for p in sorted((home/'FDS_CICD_PushClaims').iterdir()):
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and s.st_size < 65536
    out['previous_claims'].append({'name': p.name, 'size': s.st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
out['worker_count'] = sum(1 for p in pathlib.Path('/proc').iterdir()
    if p.name.isdigit() and (p/'comm').exists() and (p/'comm').read_text().strip() == 'Runner.Worker')
for name, args in [('skopeo_version', ['/usr/bin/skopeo', '--version']),
                   ('skopeo_integrity', ['/usr/bin/rpm', '-V', 'skopeo'])]:
    r = subprocess.run(args, capture_output=True, text=True, timeout=10)
    out[name] = {'rc': r.returncode, 'stdout': r.stdout, 'stderr_sha256': hashlib.sha256(r.stderr.encode()).hexdigest()}
for sub, flags in [('copy', ['--preserve-digests', '--dest-authfile', '--dest-tls-verify']),
                   ('inspect', ['--raw', '--authfile', '--tls-verify'])]:
    r = subprocess.run(['/usr/bin/skopeo', sub, '--help'], capture_output=True, text=True, timeout=5)
    out[sub+'_options'] = {'rc': r.returncode, 'found': {f: f in r.stdout for f in flags}}
context = ssl.create_default_context()
try:
    with urllib.request.urlopen('https://10.1.93.54/api/v2.0/health', context=context, timeout=8) as r:
        raw = r.read(32769)
        assert len(raw) <= 32768
        body = json.loads(raw)
        out['harbor'] = {'tls_verified': True, 'http_status': r.status,
                         'status': body.get('status'),
                         'components': [{'name': x.get('name'), 'status': x.get('status')} for x in body.get('components', [])]}
except Exception as e:
    out['harbor'] = {'probe_result': 'FAILED', 'error_type': type(e).__name__}
print(json.dumps(out))
