import concurrent.futures,json
import runtime as r
tasks=[]
for role,host,user,key in [('ansible','10.250.10.10','server01_ansible',''),('control01','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519'),('runner','10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519')]:
 if role=='ansible':continue
 tasks.append(('cleanup-inventory-'+role,host,user,key,False,r.O/'cleanup_inventory.py',[role]))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:results=list(p.map(r.collect.remote,tasks))
assert all(x['rc']==0 for x in results)
import shlex
raw=r.ops.run('cleanup-inventory-ansible',shlex.join(['/usr/bin/python3','-B','-I','-S','-','ansible']),(r.O/'cleanup_inventory.py').read_bytes())
r.save(r.O/'cleanup-inventory-ansible.json',json.loads(raw))
for role in ['ansible','control01','runner']:
 v=r.load(r.O/'cleanup-inventory-ansible.json') if role=='ansible' else r.load(r.O/('cleanup-inventory-'+role)/'stdout.json')
 print(json.dumps({'role':role,'files':sum(len(x) for x in v['roots'].values()),'retained_native_dirs':len(v['public_source_dirs_retained']),'sockets':v.get('sockets')}))
