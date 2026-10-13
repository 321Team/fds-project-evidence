import datetime,hashlib,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='ansible01','STOP_HOST'
root=pathlib.Path('/home/server01_ansible/worker02-session-plan-3hetha3t/source')
engine=pathlib.Path('/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin')
def cmd(argv):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=10,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1',LC_ALL='C'))
 return {'argv':argv,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.geteuid(),'scope':'existing source/engine read only; no runner supply, playbook, clone or guest staging','root':str(root),'engine':str(engine),'commands':[],'files':[]}
for args in [['git','-C',str(root),'rev-parse','HEAD'],['git','-C',str(root),'status','--porcelain','--untracked-files=no']]+[[str(engine/name),'--version'] for name in ['ansible','ansible-playbook','ansible-inventory','ansible-config']]:out['commands'].append(cmd(args))
for rel in ['ansible.cfg','inventory/hosts.yml','inventory/group_vars/all.yml','scripts/cr-p1-ans-01-01-run.sh','playbooks/cr-p1-ans-01-01-worker02-session.yml']:
 p=root/rel;s=p.stat();raw=p.read_bytes();after=p.stat()
 out['files'].append({'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(s.st_mode&0o7777),'stable':(s.st_mtime_ns,s.st_ctime_ns,s.st_size,s.st_ino)==(after.st_mtime_ns,after.st_ctime_ns,after.st_size,after.st_ino)})
out['status']='COLLECTED_REVIEW_REQUIRED' if all(c['rc']==0 for c in out['commands']) and all(f['stable'] for f in out['files']) else 'INCOMPLETE'
print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
