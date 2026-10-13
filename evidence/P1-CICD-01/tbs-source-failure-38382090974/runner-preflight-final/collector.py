"""Pure read-only preflight; no credential contents, environment, or process arguments."""
import datetime, hashlib, json, os, pathlib, pwd, shutil, socket, stat, subprocess
home=pathlib.Path('/home/server01_cicd-runner')
supply=home/'FDS_CICD_Runtime/FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a'
out={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'read_only':True,'credential_access':False,'hostname':socket.gethostname(),'user':pwd.getpwuid(os.getuid()).pw_name,'uid':os.getuid()}
assert out['hostname']=='cicd-runner01' and out['user']=='server01_cicd-runner' and out['uid']==1000
out['directories']={}
for p in (home,supply.parent,supply):
    s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==1000
    assert not p.is_symlink()
    out['directories'][str(p)]={'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode))}
assert stat.S_IMODE(home.stat().st_mode)==0o700
out['free_bytes']=shutil.disk_usage(home).free;assert out['free_bytes']>=4*1024**3
workers=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
    try:
        name=p.read_text().strip()
        if name in ('Runner.Worker','Runner.Worker.exe'):workers.append({'pid':int(p.parent.name),'name':name})
    except (FileNotFoundError,PermissionError,ProcessLookupError):pass
out['workers']=workers;assert not workers
p=subprocess.run(['/usr/bin/podman','--version'],capture_output=True,timeout=8)
assert p.returncode==0
out['podman_version']=p.stdout.decode().strip()
out['supply_top_level']=sorted(p.name for p in supply.iterdir())
out['manifest_files']={}
for p in supply.iterdir():
    if p.is_file() and not p.is_symlink() and ('manifest' in p.name.lower() or p.name=='SHA256SUMS'):
        s=p.stat();assert s.st_size<2*1024**2
        out['manifest_files'][p.name]={'bytes':s.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
assert out['manifest_files']['SUPPLY_MANIFEST.json']['sha256']=='6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4'
out['ready']=True
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(out))
