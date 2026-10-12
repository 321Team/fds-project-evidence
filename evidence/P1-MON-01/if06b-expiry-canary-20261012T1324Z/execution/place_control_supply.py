from pathlib import Path
import base64
import hashlib
import json
import control_runtime as r

pkg=Path('C:/Project321team/ClaudeCode/MON_IF06B_FIELD_PREP_20261012')
items={'supply-92c182f.tar':(pkg/'supply-92c182f.tar').read_bytes(),
       'if06b-aux-r1.tar':(pkg/'if06b-aux-r1.tar').read_bytes(),
       'input.json':(r.ROOT/'input.session.candidate.json').read_bytes()}
assert hashlib.sha256(items['supply-92c182f.tar']).hexdigest()=='8d1630c872eb9a88cecc3f5dec3cc6e2316f87ec6dacea420777967b5795fc20'
assert hashlib.sha256(items['if06b-aux-r1.tar']).hexdigest()=='fd5bb7c43fa8cf166f074eb78afb98bf4e552cfdc6f4762adac9eda1bab9d7ad'
payload={name:base64.b64encode(data).decode() for name,data in items.items()}
hashes={name:hashlib.sha256(data).hexdigest() for name,data in items.items()}
body='''import base64,hashlib,tarfile,io,stat
ses=Path(SES);incoming=Path(INCOMING)
for p in [ses,Path(SURV),Path(TOK),incoming]:assert not os.path.lexists(p),'PATH_ALREADY_PRESENT'
parent=ses.parent
assert parent.resolve()==parent and parent.stat().st_uid==0 and stat.S_IMODE(parent.stat().st_mode)==0o700
assert incoming.parent.resolve()==incoming.parent
files=FILES;hashes=HASHES
data={name:base64.b64decode(value) for name,value in files.items()}
for name,value in data.items():assert hashlib.sha256(value).hexdigest()==hashes[name]
expected={'supply-92c182f.tar':{'SHA256SUMS','canary-manifest.json','coordinator.py','decision.py','guardian.py','journal.py','supervisor.py','transport.py'},
          'if06b-aux-r1.tar':{'rbac/01-serviceaccount.yaml','rbac/02-clusterrole.yaml','rbac/03-clusterrolebinding.yaml','rbac/SHA256SUMS','tools/SHA256SUMS','tools/gate.py','tools/ident.py','tools/objinfo.py','tools/record.sh','tools/tokeninfo.py'}}
unpacked={}
for name in expected:
 with tarfile.open(fileobj=io.BytesIO(data[name]),mode='r:') as tar:
  members=tar.getmembers()
  assert len(members)==len(expected[name]) and {m.name for m in members}==expected[name] and all(m.isfile() for m in members)
  unpacked[name]={m.name:tar.extractfile(m).read() for m in members}
incoming.mkdir(mode=0o700)
for name,value in data.items():
 with (incoming/name).open('xb') as f:f.write(value)
ses.mkdir(mode=0o700)
for name in ['supply','aux','journal','evidence','results']:(ses/name).mkdir(mode=0o700 if name in ['journal','evidence','results'] else 0o755)
for archive,target in [('supply-92c182f.tar',ses/'supply'),('if06b-aux-r1.tar',ses/'aux')]:
 for name,value in unpacked[archive].items():
  p=target/name;p.parent.mkdir(mode=0o755,exist_ok=True)
  with p.open('xb') as f:f.write(value)
  p.chmod(0o644)
with (ses/'input.json').open('xb') as f:f.write(data['input.json'])
checks=[]
for folder in [ses/'supply',ses/'aux/rbac',ses/'aux/tools']:
 p=subprocess.run(['/usr/bin/sha256sum','-c','SHA256SUMS'],cwd=folder,capture_output=True,text=True)
 checks.append({'dir':str(folder),'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 assert p.returncode==0
record=['/usr/bin/env','IF06B_RESULTS='+str(ses/'results'),'/bin/sh',str(ses/'aux/tools/record.sh')]
p=subprocess.run(record+['1-4-layout','/bin/sh','-c','ls -lZ "$1/supply" "$1/aux/rbac" "$1/aux/tools"; ls -Zd "$1" "$1/journal" "$1/evidence" "$1/results"; ls -A "$1/journal" "$1/evidence"','sh',str(ses)],capture_output=True,text=True)
assert p.returncode==0
assert list((ses/'journal').iterdir())==[] and list((ses/'evidence').iterdir())==[]
receipt={'step':'SUPPLY_PLACED','input_sha256':hashlib.sha256((ses/'input.json').read_bytes()).hexdigest(),'checks':checks,
         'paths':{str(p):{'uid':p.stat().st_uid,'mode':oct(stat.S_IMODE(p.stat().st_mode))} for p in [ses,incoming,ses/'input.json',ses/'journal',ses/'evidence',ses/'results']},
         'rbac_created':0,'token_issued':0,'canary_created':0}
(ses/'results/supply-receipt.json').write_text(json.dumps(receipt,indent=2)+'\\n')
print(json.dumps(receipt))
'''
for key,value in [('SES',r.SES),('INCOMING',r.IN),('SURV',r.SURV),('TOK',r.TOK),('FILES',payload),('HASHES',hashes)]:body=body.replace(key,repr(value))
row=r.run('control01-supply-placed',body)
assert row['rc']==0
