import datetime,json,os,socket,subprocess
assert socket.gethostname()=='ansible01'
env=dict(os.environ,LC_ALL='C.UTF-8',LANG='C.UTF-8',PYTHONDONTWRITEBYTECODE='1')
engine='/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin/'
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'scope':'only version reads repeated with UTF-8 locale; no system locale modification','locale':'C.UTF-8','commands':[]}
for argv in [['locale','charmap']]+[[engine+n,'--version'] for n in ['ansible','ansible-playbook','ansible-inventory','ansible-config']]:
 p=subprocess.run(argv,capture_output=True,text=True,timeout=10,env=env)
 out['commands'].append({'argv':argv,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode:break
out['status']='COLLECTED_REVIEW_REQUIRED' if len(out['commands'])==5 and all(x['rc']==0 for x in out['commands']) else 'INCOMPLETE'
print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
