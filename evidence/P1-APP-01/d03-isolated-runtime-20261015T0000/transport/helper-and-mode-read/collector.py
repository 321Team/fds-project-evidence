
import base64,datetime as dt,hashlib,json,os,pathlib,socket,stat,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
home=pathlib.Path('/home/server01_cicd-runner');run='202610150000';runtime=home/('FDS_D03_'+run)
root=home/'FDS_D03_Precheck.qobwb70m'
allowed={'started_at.txt','hostname.txt','identity.txt','command.json','stdout.txt','stderr.txt','rc.txt','finished_at.txt','result.json'}
manifest=(root/'SHA256SUMS').read_bytes();out={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'read_only':True,'files':[],'modes':[],'exact_names':[]}
seen=set()
for line in manifest.decode().splitlines():
    digest,name=line.split('  ',1);assert name in allowed and name not in seen;seen.add(name)
    p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and s.st_size<100000
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    out['files'].append({'name':name,'sha256':digest,'base64':base64.b64encode(raw).decode()})
assert seen==allowed
out['files'].append({'name':'SHA256SUMS','sha256':hashlib.sha256(manifest).hexdigest(),'base64':base64.b64encode(manifest).decode()})
for rel in ['.','stage','stage/code','stage/hooks','stage/code/d03_lab.py','stage/hooks/10-fds-schema.sh','stage/hooks/fds-schema.sql','stage/hooks/20-d03-logging.sh']:
    p=runtime/rel;s=p.lstat();out['modes'].append({'path':str(p),'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid,'gid':s.st_gid,'directory':stat.S_ISDIR(s.st_mode)})
p=subprocess.run(['ls','-Zd',str(runtime/'stage/code'),str(runtime/'stage/hooks')],capture_output=True,text=True,timeout=5)
out['ls_context']={'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
for role in ('db','api','engine','fixture'):
    name='fds-d03-'+run+'-'+role;p=subprocess.run(['podman','container','exists',name],capture_output=True,text=True,timeout=10)
    assert p.returncode==1;out['exact_names'].append({'name':name,'rc':p.returncode,'absent':True})
out['containers']=json.loads(subprocess.check_output(['podman','ps','-a','--format','json'],timeout=10));assert not out['containers']
out['credential_files_absent']=not (runtime/'db.env').exists() and not (runtime/'api.env').exists();assert out['credential_files_absent']
out['post_intent_count']=len(list(runtime.glob('*-post-intent.json')));assert out['post_intent_count']==0
out['claim_sha256']=hashlib.sha256((home/'FDS_D03_Claims'/('202610150000.json')).read_bytes()).hexdigest()
out['runtime_original_result']=json.loads((runtime/'result.json').read_bytes())
print(json.dumps(out))
