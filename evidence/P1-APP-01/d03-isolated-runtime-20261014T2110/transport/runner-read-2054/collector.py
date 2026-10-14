
import datetime as dt, hashlib, json, os, pathlib, platform, shutil, socket, stat, subprocess
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def cmd(argv):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=15)
    return {'argv':argv,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
result={'started_at_utc':now(),'hostname':socket.gethostname(),'uid':os.getuid(),'arch':platform.machine(),'python':platform.python_version()}
assert result['hostname']=='cicd-runner01' and result['uid']==1000 and result['arch']=='x86_64'
result['disk_home']=shutil.disk_usage('/home')._asdict()
result['mem_available_kib']=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
workers=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
    try:
        if p.read_text().strip()=='Runner.Worker': workers.append(int(p.parent.name))
    except (FileNotFoundError,ProcessLookupError): pass
result['runner_worker_pids']=workers
result['podman_info']=cmd(['podman','info','--format','json'])
result['containers']=cmd(['podman','ps','-a','--format','json'])
result['images']=cmd(['podman','images','--format','json'])
result['port18081']=cmd(['ss','-H','-ltn','sport = :18081'])
home=pathlib.Path('/home/server01_cicd-runner')
result['bundle_target_exists']=(home/'FDS_D03_Preparation_192c5ab04a5e').exists()
result['app_archives']=[]
base=home/'FDS_CICD_AppWorkflow.3_geu2kf/build-scan'
for name,expected in [('transaction-api.oci.tar','ff3d145047f53b67f44b8a91994d7ab2b72998d9b276184b3c70a2148d52e3cf'),('fds-engine.oci.tar','319ab0af288d32a156feb1867193d3b7be0e663f2a17ee3efaa95aa505cd7031')]:
    p=base/name
    info=p.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_uid==1000 and p.resolve().is_relative_to(home)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    result['app_archives'].append({'path':str(p),'size':info.st_size,'sha256':h.hexdigest(),'matches_expected':h.hexdigest()==expected})
result['finished_at_utc']=now()
print(json.dumps(result))
