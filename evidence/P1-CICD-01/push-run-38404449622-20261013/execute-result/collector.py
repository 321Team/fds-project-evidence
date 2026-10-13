FOLDER='/home/server01_cicd-runner/FDS_CICD_Push.9kxlkyaz'
# FOLDER is supplied only from the exact completed Actions Job log.
from pathlib import Path
from datetime import datetime, timezone
import base64, hashlib, json, os, socket, stat

assert socket.gethostname() == 'cicd-runner01' and os.geteuid() == 1000
root = Path(FOLDER)
assert root.parent == Path('/home/server01_cicd-runner') and root.name.startswith('FDS_CICD_Push.')
for node in (root, *root.parents): assert not node.is_symlink()
s = root.stat()
assert s.st_uid == 1000 and stat.S_IMODE(s.st_mode) == 0o700
out = dict(at_utc=datetime.now(timezone.utc).isoformat(), folder=FOLDER, files={}, missing=[], hash_only={})

def plain(path):
    for node in (path, *path.parents): assert not node.is_symlink()
    s = path.stat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and s.st_nlink == 1
    return s

names = ('dispatch.json', 'result.json', 'credential-cleanup.json', 'dispatch-result.json',
         'dispatch-SHA256SUMS', 'SHA256SUMS', 'fresh-scan/result.json',
         'fresh-scan/SHA256SUMS', 'fresh-scan/db/result.json', 'fresh-scan/db/SHA256SUMS',
         'fresh-scan/db/cache/db/metadata.json', 'fresh-scan/transaction-api/exit-code.txt',
         'fresh-scan/fds-engine/exit-code.txt')
for name in names:
    path = root / name
    if not path.exists():
        out['missing'].append(name)
        continue
    assert plain(path).st_size <= 65536
    raw = path.read_bytes()
    out['files'][name] = dict(sha256=hashlib.sha256(raw).hexdigest(), raw_b64=base64.b64encode(raw).decode())
    if name.endswith('.json'): out['files'][name]['data'] = json.loads(raw)
    else: out['files'][name]['text'] = raw.decode()
for name in ('fresh-scan/transaction-api/report.json', 'fresh-scan/fds-engine/report.json',
             'fresh-scan/db/cache/db/trivy.db'):
    path = root / name
    if not path.exists(): continue
    s = plain(path)
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    out['hash_only'][name] = dict(sha256=h.hexdigest(), bytes=s.st_size)
claim = root.parent/'FDS_CICD_PushClaims'/'8b7b4f4e64c271b54167bc768e4e3afc1b2326c480683aaaf4aa0ff3e18c2b06.json'
if claim.exists():
    assert plain(claim).st_size < 16384
    raw = claim.read_bytes()
    out['claim'] = dict(path=str(claim), sha256=hashlib.sha256(raw).hexdigest(),
                        raw_b64=base64.b64encode(raw).decode(), data=json.loads(raw))
else: out['claim'] = None
out['auth_directory_names_present'] = sorted(p.name for p in root.parent.glob('FDS_CICD_PushAuth.*'))
out['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
print(json.dumps(out))
