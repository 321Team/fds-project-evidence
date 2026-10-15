import concurrent.futures,datetime as dt,hashlib,importlib.util,json,shlex,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('collect',O.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=O
key='/home/server01_ansible/.ssh/p1_ansible_ed25519';cpkey='/home/server01_ansible/.ssh/id_ed25519'
tasks=[('clock-cp1','10.1.93.102','server02',cpkey,False,O/'read_clock_version.py',[]),
       ('clock-runner','10.250.10.20','server01_cicd-runner',key,False,O/'read_clock_version.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(m.remote,tasks))
assert all(x['rc']==0 and not x['stderr_bytes'] for x in rows)
raw=(O/'read_clock_version.py').read_bytes();begin=dt.datetime.now(dt.timezone.utc)
p=subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8',
                  '-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3 -I -B -S -'],
                 input=raw,capture_output=True,timeout=20)
end=dt.datetime.now(dt.timezone.utc)
(O/'clock-ansible.stdout').write_bytes(p.stdout);(O/'clock-ansible.stderr').write_bytes(p.stderr)
assert p.returncode==0 and not p.stderr
out={'ansible':json.loads(p.stdout),'cp1':json.loads((O/'clock-cp1/stdout.json').read_bytes()),
     'runner':json.loads((O/'clock-runner/stdout.json').read_bytes())}
assert out['cp1']['api_version']=={'rc':0,'stderr_sha256':hashlib.sha256(b'').hexdigest(),'gitVersion':'v1.36.4'}
for role,row in out.items():
    assert row['ntp_synchronized']=={'rc':0,'value':'yes'}
    if role=='ansible':a,b=begin,end
    else:
        rec=json.loads((O/('clock-'+role)/'receipt.json').read_bytes())
        a=dt.datetime.fromisoformat(rec['started_at_utc']);b=dt.datetime.fromisoformat(rec['finished_at_utc'])
    observed=dt.datetime.fromisoformat(row['at_utc'])
    assert a-dt.timedelta(seconds=3)<=observed<=b+dt.timedelta(seconds=3)
    row['within_local_receipt_bounds_plus_3s']=True
(O/'CLOCK_VERSION_CHECK.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('CLOCK_VERSION_CHECK_PASS')
