import base64,json
import runtime as r
result=r.collect.remote(('recovery-archive-original','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,r.O/'read_recovery_archive.py',[]));assert result['rc']==0
v=r.load(r.O/'recovery-archive-original/stdout.json');raw=base64.b64decode(v['body_b64'])
assert r.sha(raw)==v['sha256']=='6fbd08b4c7e8001b1aac34732d2ca84eaf8fa221a5b40b41d5c0522cf8851cb6'
with (r.O/'recovery.tar').open('xb') as f:f.write(raw)
print(json.dumps({'sha256':v['sha256'],'preserved':True}))
