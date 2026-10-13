from pathlib import Path
from datetime import datetime, timezone
import os, socket, stat, hashlib, json, base64

assert socket.gethostname() == 'cicd-runner01' and os.geteuid() == 1000
root = Path('/home/server01_cicd-runner/FDS_CICD_Push.aisebqro')
for n in (root, *root.parents): assert not n.is_symlink()
s = root.stat()
assert s.st_uid == 1000 and stat.S_IMODE(s.st_mode) == 0o700
out = dict(at_utc=datetime.now(timezone.utc).isoformat(), folder=str(root), files={})
for name in ('dispatch.json', 'result.json', 'SHA256SUMS'):
    path = root / name
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and s.st_nlink == 1 and s.st_size < 65536
    raw = path.read_bytes()
    out['files'][name] = dict(sha256=hashlib.sha256(raw).hexdigest(), raw_b64=base64.b64encode(raw).decode())
    if name.endswith('.json'): out['files'][name]['data'] = json.loads(raw)
    else: out['files'][name]['text'] = raw.decode()
d = out['files']['dispatch.json']['data']
r = out['files']['result.json']['data']
assert d['record_sha256'] == '13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89' and d['mode'] == 'false'
assert str(d['execution_context']['run_id']) == '38318762530' and d['execution_context']['attempt'] == 1
assert d['execution_context']['workflow_sha'] == '2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
assert r['VALIDATION'] == 'PASS' and r['PUSH'] == 'NOT_EXECUTED' and r['error_code'] == 'NONE'
assert out['files']['SHA256SUMS']['text'] == out['files']['result.json']['sha256']+'  result.json\n'
out['VALIDATION'] = 'PASS'
print(json.dumps(out))
