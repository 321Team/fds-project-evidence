import concurrent.futures,datetime as dt,hashlib,importlib.util,json,shlex,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
def read(p):return json.loads((O/p).read_bytes())
def save(p,v):(O/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('collect',O.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=O
pre=read('native-preflight.stdout');run=read('native-execute.stdout')
assert run['TOKEN_LIFECYCLE']=='PASS'
dirs={'cp1':[],'runner':[],'ansible':[pre['local_source_workdir'],run['local_source_workdir'],read('PUBLIC_STAGING.json')['remote_directory']]}
for data in (pre,run):
    for row in data['sources']:dirs[row['role']].append(row['workdir'])
key='/home/server01_ansible/.ssh/p1_ansible_ed25519';cpkey='/home/server01_ansible/.ssh/id_ed25519'
tasks=[('app-after','10.1.93.102','svc_ansible',key,True,O/'app-before/collector.py',[]),
       ('runner-after','10.250.10.20','server01_cicd-runner',key,False,O/'runner-before/collector.py',[]),
       ('rbac-after','10.1.93.102','svc_ansible',key,True,O/'rbac-before/collector.py',[]),
       ('cp1-auth-after','10.1.93.102','server02',cpkey,False,O/'cp1-auth-before/collector.py',['cp1']),
       ('cleanup-cp1','10.1.93.102','server02',cpkey,False,O/'read_cleanup.py',dirs['cp1']),
       ('cleanup-runner','10.250.10.20','server01_cicd-runner',key,False,O/'read_cleanup.py',dirs['runner'])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(m.remote,tasks))
save('AFTER_COLLECTION_RESULTS.json',results);print(json.dumps(results))
assert all(x['rc']==0 and not x['stderr_bytes'] for x in results)
raw=(O/'read_cleanup.py').read_bytes();begin=dt.datetime.now(dt.timezone.utc).isoformat()
argv=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes',
      'fds-ansible01',shlex.join(['/usr/bin/python3','-I','-B','-S','-',*dirs['ansible']])]
p=subprocess.run(argv,input=raw,capture_output=True,timeout=30)
(O/'cleanup-ansible.stdout').write_bytes(p.stdout);(O/'cleanup-ansible.stderr').write_bytes(p.stderr)
save('cleanup-ansible.receipt.json',{'started_at_utc':begin,'finished_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
     'argv':argv,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),
     'source_sha256':hashlib.sha256(raw).hexdigest(),'classification':'PURE_READ_POSTCHECK'})
assert p.returncode==0 and not p.stderr
print('AFTER_COLLECTION_COMPLETE')
