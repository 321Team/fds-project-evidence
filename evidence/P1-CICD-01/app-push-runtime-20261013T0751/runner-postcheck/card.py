from pathlib import Path
import datetime, hashlib, http.client, json, os, pwd, socket, ssl, stat

assert socket.gethostname() == 'cicd-runner01' and os.geteuid() == 1000
home = Path(pwd.getpwuid(os.getuid()).pw_dir)
assert str(home) == '/home/server01_cicd-runner'
paths = [home, home/'FDS_CICD_PushInputs', home/'FDS_CICD_AppWorkflow.57rithja']
result = dict(started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              hostname=socket.gethostname(), uid=os.geteuid(), home=str(home),
              boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(), paths={})
for p in paths:
    for q in (p,*p.parents): assert not q.is_symlink()
    s = p.lstat()
    assert stat.S_ISDIR(s.st_mode) and s.st_uid == 1000 and stat.S_IMODE(s.st_mode) == 0o700
    result['paths'][str(p)] = dict(uid=s.st_uid, mode=oct(stat.S_IMODE(s.st_mode)))
name = 'push-20261013-window1200.json'
claim = home/'FDS_CICD_PushClaims'/'13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89.json'
result['target_exists'] = os.path.lexists(paths[1]/name)
result['claim_exists'] = os.path.lexists(claim)
ctx = ssl.create_default_context()
assert ctx.check_hostname and ctx.verify_mode == ssl.CERT_REQUIRED
c = http.client.HTTPSConnection('10.1.93.54', 443, timeout=12, context=ctx)
try:
    c.connect()
    result['tls'] = dict(verified=True, leaf_sha256=hashlib.sha256(c.sock.getpeercert(binary_form=True)).hexdigest(), version=c.sock.version())
    c.request('GET', '/api/v2.0/health', headers={'Connection':'close','Accept':'application/json'})
    r = c.getresponse()
    body = r.read(65537)
    assert len(body) <= 65536
    result['health'] = dict(http_status=r.status, body_sha256=hashlib.sha256(body).hexdigest(), body=json.loads(body))
    assert r.status == 200 and result['health']['body']['status'] == 'healthy'
finally:
    c.close()
result['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(result))
