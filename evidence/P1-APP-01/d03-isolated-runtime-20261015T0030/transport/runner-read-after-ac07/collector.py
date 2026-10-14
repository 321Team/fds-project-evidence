
import datetime as dt,hashlib,json,os,pathlib,platform,shutil,socket,subprocess
def cmd(argv):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=10)
    assert p.returncode==0,'READ_FAILED '+argv[1]
    return p.stdout
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000 and platform.machine()=='x86_64'
home=pathlib.Path('/home/server01_cicd-runner')
result={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'read_only':True,'hostname':socket.gethostname(),'uid':os.getuid(),'arch':platform.machine()}
info=json.loads(cmd(['podman','info','--format','json']))
result['podman_version']=info['version']['Version'];result['rootless']=info['host']['security']['rootless']
result['container_count']=len(json.loads(cmd(['podman','ps','-a','--format','json'])))
workers=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
    try:
        if p.read_text().strip()=='Runner.Worker':workers.append(int(p.parent.name))
    except (FileNotFoundError,ProcessLookupError):pass
result['worker_pids']=workers
result['port18081_empty']=not cmd(['ss','-H','-ltn','sport = :18081']).strip()
result['mem_available_mib']=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
result['disk_free_bytes']=shutil.disk_usage('/home').free
images={'api':'sha256:ab34196baf2b878222857be47b200baed0151679a5b19fe15635ba50f77bffee','engine':'sha256:b82d35a60e7a7f4a30366a926699fa4b673e69610f64fa0e7f294673ed12f4fc','db':'quay.io/sclorg/postgresql-16-c9s@sha256:d33717fd33c1a4b11afef94568d0c20812a19d62fb8c633fadee1e491e2edd4a'}
result['images']=[]
for role,image in images.items():
    obj=json.loads(cmd(['podman','image','inspect',image]))[0]
    ident='sha256:'+obj['Id'].removeprefix('sha256:')
    expected='sha256:5f7659016ef769811a0fdc349c9cad11f520dc7e147633bb1025e499002d9cd2' if role=='db' else image
    assert ident==expected and obj['Architecture']=='amd64' and obj['Os']=='linux'
    if role=='db':assert image in obj['RepoDigests'] and obj['Config']['User']=='26'
    result['images'].append({'role':role,'id':ident,'repo_digests':obj.get('RepoDigests',[]),'user':obj['Config'].get('User'),'architecture':obj['Architecture'],'os':obj['Os'],'matches':True})
old=home/'FDS_D03_202610142110'
result['old_credential_files_absent']=not (old/'db.env').exists() and not (old/'api.env').exists()
result['old_claim_sha256']=hashlib.sha256((home/'FDS_D03_Claims/202610142110.json').read_bytes()).hexdigest()
assert result['old_claim_sha256']=='258a55eb0e9e26136fef8d04c5ba9a85b142a865c2313274f4386e7f50c7c687'
result['new_bundle_path_absent']=not (home/'FDS_D03_Preparation_6531b51c9915').exists()
result['proposed_claim_absent']=not (home/'FDS_D03_Claims/202610150030.json').exists()
result['proposed_output_absent']=not (home/'FDS_D03_202610150030').exists()
result['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
assert result['rootless'] and result['container_count']==0 and not workers and result['port18081_empty'] and result['old_credential_files_absent']
assert result['mem_available_mib']>=2048 and result['new_bundle_path_absent'] and result['proposed_claim_absent'] and result['proposed_output_absent']
print(json.dumps(result))
