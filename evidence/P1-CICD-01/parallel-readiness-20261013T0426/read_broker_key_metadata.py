"""Read existing public-key fingerprints/metadata only; no key/auth changes."""
import datetime, hashlib, ipaddress, json, os, pwd, re, socket, stat, subprocess, sys
from pathlib import Path

role = sys.argv[1]
expected = {'controller': ('ansible01', 'server01_ansible'), 'cp1': ('k8s-control01', 'root')}
host, user = expected[role]
assert socket.gethostname() == host and pwd.getpwuid(os.getuid()).pw_name == user
out = {'role': role, 'host': host, 'user': user,
       'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'scope': 'existing public fingerprints and path metadata only; no private-key contents, authentication attempts, token, or changes',
       'files': [], 'errors': []}

def metadata(p):
    s = p.lstat()
    return {'path': str(p), 'uid': s.st_uid, 'gid': s.st_gid,
            'mode': oct(stat.S_IMODE(s.st_mode)), 'regular': stat.S_ISREG(s.st_mode),
            'symlink': stat.S_ISLNK(s.st_mode), 'nlink': s.st_nlink, 'size': s.st_size}

def fingerprints(p):
    m = metadata(p)
    if not m['regular'] or m['symlink'] or m['size'] > 131072:
        return dict(m, status='UNSUPPORTED_FILE')
    r = subprocess.run(['/usr/bin/ssh-keygen', '-l', '-E', 'sha256', '-f', str(p)], capture_output=True, timeout=5)
    fps = []
    for line in r.stdout.decode('utf-8', errors='strict').splitlines():
        a = line.split()
        if len(a) >= 3 and re.fullmatch(r'SHA256:[A-Za-z0-9+/]+', a[1]):
            fps.append({'bits': a[0], 'fingerprint': a[1], 'type': a[-1]})
    return dict(m, rc=r.returncode, fingerprints=fps,
                stderr_sha256=hashlib.sha256(r.stderr).hexdigest())

if role == 'controller':
    r = subprocess.run(['/usr/sbin/ip', '-j', 'route', 'get', '10.1.93.102'], capture_output=True, timeout=5)
    assert r.returncode == 0
    out['route_to_cp1'] = json.loads(r.stdout)
    d = Path('/home/server01_ansible/.ssh')
    out['directory'] = metadata(d)
    assert not d.is_symlink()
    for p in sorted(d.glob('*.pub'))[:30]:
        f = fingerprints(p)
        private_path = p.with_suffix('')
        try:
            f['corresponding_private_metadata'] = metadata(private_path)
        except FileNotFoundError:
            f['corresponding_private_metadata'] = None
        out['files'].append(f)
else:
    for name in ('/home/server02/.ssh/authorized_keys', '/home/server02/.ssh/authorized_keys2'):
        try:
            out['files'].append(fingerprints(Path(name)))
        except FileNotFoundError:
            out['files'].append({'path': name, 'status': 'ABSENT'})
    for name in ('/home/server02', '/home/server02/.ssh', '/home/server02/.kube/config',
                 '/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem'):
        try:
            out.setdefault('metadata', []).append(metadata(Path(name)))
        except FileNotFoundError:
            out.setdefault('metadata', []).append({'path': name, 'status': 'ABSENT'})
    source_address = str(ipaddress.IPv4Address(sys.argv[2]))
    r = subprocess.run(['/usr/sbin/sshd', '-T', '-C', 'user=server02,addr='+source_address+',host=ansible01'], capture_output=True, timeout=8)
    allow = {'pubkeyauthentication', 'passwordauthentication', 'kbdinteractiveauthentication',
             'authorizedkeysfile', 'authenticationmethods', 'allowusers', 'denyusers', 'allowgroups', 'denygroups'}
    out['sshd_candidate'] = {'rc': r.returncode, 'controller_route_source': source_address, 'source_observation_limit': 'controller route source; CP1-observed peer and reverse name not verified',
        'settings': {line.split(' ', 1)[0]: line.split(' ', 1)[1] for line in r.stdout.decode().splitlines()
                     if line.split(' ', 1)[0] in allow and ' ' in line},
        'stderr_sha256': hashlib.sha256(r.stderr).hexdigest()}
print(json.dumps(out, ensure_ascii=True, sort_keys=True))
