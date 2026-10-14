"""Copy only this completed run's receipts and named step logs; preserve bytes."""
import base64, datetime, hashlib, json, os, pathlib, re, socket, stat
assert socket.gethostname() == 'cicd-runner01' and os.getuid() == 1000
root = pathlib.Path('/home/server01_cicd-runner/FDS_CICD_UnitNegative.eb8ljt_m')
assert not root.is_symlink() and stat.S_IMODE(root.stat().st_mode) == 0o700
out = {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'root':str(root),'files':{}}
def read(name):
    p = root/name
    for part in (p,*p.parents): assert not part.is_symlink()
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and s.st_nlink == 1 and s.st_size < 8*1024**2
    raw = p.read_bytes(); after = p.stat()
    assert (s.st_size,s.st_mtime_ns,s.st_ino) == (after.st_size,after.st_mtime_ns,after.st_ino)
    out['files'][name] = {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mode':oct(stat.S_IMODE(s.st_mode)),'base64':base64.b64encode(raw).decode()}
    return raw
app_raw = read('result.json'); app = json.loads(app_raw)
assert read('SHA256SUMS').decode().strip() == hashlib.sha256(app_raw).hexdigest()+'  result.json'
assert app['context']['run_id'] == '38490368352' and app['context']['workflow_sha'] == '7171b0a3d636c3a15c78131b89bec4739cb6f49b' and app['context']['attempt'] == 1
assert hashlib.sha256(read('handoff.json')).hexdigest() == app['handoff_sha256']
build_raw = read('build-scan/result.json'); build = json.loads(build_raw)
assert hashlib.sha256(build_raw).hexdigest() == app['build_result_sha256']
assert read('build-scan/SHA256SUMS').decode().strip() == hashlib.sha256(build_raw).hexdigest()+'  result.json'
assert app['NEGATIVE_UNIT_PROBE'] == build['NEGATIVE_UNIT_PROBE'] == 'EXPECTED_FAILURE_OBSERVED'
assert build['images'] == {} and build['unit_negative']['cleanup'] == 'REMOVED'
for folder,receipt in (('',app),('build-scan/',build)):
    for step in receipt['steps']:
        name = step['name']; assert re.fullmatch('[A-Za-z0-9_.-]+',name) and '..' not in name
        assert hashlib.sha256(read(folder+name+'.log')).hexdigest() == step['log_sha256']
cidfile = 'build-scan/unit-negative/container.cid'
if (root/cidfile).exists():
    assert read(cidfile).decode().strip() == build['unit_negative']['container_id']
else:
    # Podman removal can remove its cidfile. The original identity and cleanup
    # logs still bind the CID; absence alone is not proof of container removal.
    out['optional_cidfile_absent'] = True
assert read('build-scan/unit-negative-create.log').decode().strip() == build['unit_negative']['container_id']
assert read('build-scan/unit-negative-remove.log').decode().strip() == build['unit_negative']['container_id']
assert read('build-scan/unit-negative-removed.log').strip() == b''
out['absence'] = {name:not (root/'build-scan'/name).exists() for name in ('scan','fds-engine.oci.tar','transaction-api.oci.tar')}
assert all(out['absence'].values())
out['workers'] = []
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
    try:
        if p.read_text().strip() == 'Runner.Worker': out['workers'].append(int(p.parent.name))
    except (FileNotFoundError,PermissionError,ProcessLookupError): pass
assert not out['workers']
print(json.dumps(out))
