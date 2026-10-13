import base64, datetime, hashlib, json, os, pathlib, socket, stat
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
root=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.4_alowtt')
assert not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==0o700
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'root':str(root),'files':{}}
for name in ('result.json','SHA256SUMS','source-init.log','source-origin-set.log','source-fetch.log'):
    p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and s.st_nlink==1 and s.st_size<1024**2
    raw=p.read_bytes();out['files'][name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'base64':base64.b64encode(raw).decode()}
receipt=json.loads(base64.b64decode(out['files']['result.json']['base64']))
assert receipt['context']['run_id']=='38382090974' and receipt['context']['workflow_sha']=='fadc07f18b5bf7febc8cf601fa138d8f35e9ccb4'
assert receipt['APP_TEST_BUILD_SCAN']=='NOT_EXECUTED'
out['build_scan_directory_exists']=(root/'build-scan').exists()
out['handoff_exists']=(root/'handoff.json').exists()
assert not out['build_scan_directory_exists'] and not out['handoff_exists']
out['top_level_metadata']=[{'name':p.name,'mode':oct(stat.S_IMODE(p.lstat().st_mode)),'bytes':p.lstat().st_size} for p in root.iterdir()]
out['workers']=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
    try:
        if p.read_text().strip()=='Runner.Worker':out['workers'].append(int(p.parent.name))
    except (FileNotFoundError,PermissionError,ProcessLookupError):pass
print(json.dumps(out))
