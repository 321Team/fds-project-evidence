"""Remove only exact supplied, hash-matched files; keep journals and public sources."""
import contextlib,io,json,shlex
import runtime as r
r.authorization()
assert r.load(r.O/'R2_STABLE_FINAL.json')['ready_pods']==6
bindings=r.load(r.O/'AUTHORIZATION_BINDINGS.json')
inventory={role:r.load(r.O/'cleanup-inventory-ansible.json') if role=='ansible' else r.load(r.O/('cleanup-inventory-'+role)/'stdout.json') for role in ('ansible','runner','control01')}
local={}
base='/home/server01_ansible/FDS_CICD_AC09_20261015_1535/'
for rel,digest in r.load(r.O/'CONTROLLER_PACKAGE.json')['members'].items():
 p=r.B/'source'/rel.split('/')[-1] if rel.startswith('tools/') else r.B/rel
 assert r.sha(p.read_bytes())==digest
 local[base+rel]=p
for name,p in [('controller.tar',r.O/'controller.tar'),('binding-38693979785.json',r.O/'R1/actual-scope-over-local-metadata.original.json'),('binding-38694721511.json',r.O/'R2/scope-binding.json')]:local[base+name]=p
for round,b in bindings.items():local['/home/server01_cicd-runner/FDS_CICD_DeployInputs/'+b['record_name']]=r.O/round/b['record_name']
for name,p in [('console_restore_current.py',r.B/'round4/console_restore_current.py'),('recovery-contract.json',r.O/'recovery-contract.json'),('recovery.tar',r.O/'recovery.tar')]:local['/home/server02/FDS_AC09_ConsoleRestore_20261015/'+name]=p
found={x['path'] for v in inventory.values() for rows in v['roots'].values() for x in rows if x['type']=='file'}
assert found==set(local),(found-set(local),set(local)-found)
for v in inventory.values():
 for rows in v['roots'].values():
  for x in rows:
   if x['type']=='file':assert r.sha(local[x['path']].read_bytes())==x['sha256'],x['path']
remote='''import datetime as dt,hashlib,json,os,pathlib,pwd,socket,stat
v=INVENTORY
assert socket.gethostname()==v['host'] and pwd.getpwuid(os.getuid()).pw_name==v['user']
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat('2026-10-15T16:20:00+09:00')
for proc in pathlib.Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  if (proc/'comm').read_text().strip()=='Runner.Worker':raise AssertionError('WORKER_ACTIVE')
 except (PermissionError,FileNotFoundError):pass
rows=[x for group in v['roots'].values() for x in group]
for root,group in v['roots'].items():
 p=pathlib.Path(root);assert p.is_absolute() and p.resolve()==p and p.parent!=pathlib.Path('/')
 if p.is_dir():assert {str(x) for x in p.rglob('*')}=={x['path'] for x in group if x['path']!=root}
for x in rows:
 p=pathlib.Path(x['path']);s=p.lstat()
 assert not p.is_symlink() and s.st_uid==os.getuid() and s.st_ino==x['inode'] and s.st_mtime_ns==x['mtime_ns']
 assert stat.S_IMODE(s.st_mode)==x['mode']
 if x['type']=='file':assert s.st_nlink==1 and stat.S_ISREG(s.st_mode) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 else:assert stat.S_ISDIR(s.st_mode)
removed=[]
for x in rows:
 if x['type']=='file':pathlib.Path(x['path']).unlink();removed.append(x['path'])
for x in sorted((x for x in rows if x['type']=='dir'),key=lambda x:len(pathlib.Path(x['path']).parts),reverse=True):pathlib.Path(x['path']).rmdir();removed.append(x['path'])
assert all(not pathlib.Path(n).exists() for n in v['roots'])
print(json.dumps({'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'host':v['host'],'removed':removed,'roots_absent':True,'claim_journals_and_public_source_dirs':'RETAINED','broad_delete':False}))
'''
receipt={}
for role in ('runner','control01','ansible'):
 code=remote.replace('INVENTORY',repr(inventory[role]));compile(code,'cleanup','exec')
 command=shlex.join(['/usr/bin/python3','-B','-I','-S','-'])
 if role=='control01':
  inner=r.ops.INNER.copy();inner[inner.index('/home/server01_ansible/.ssh/p1_ansible_ed25519')]='/home/server01_ansible/.ssh/id_ed25519';inner[-1]='server02@10.1.93.102';command=shlex.join(inner+[command])
 with contextlib.redirect_stdout(io.StringIO()):raw=r.ops.run('cleanup-exact-'+role,command,code.encode(),runner=role=='runner')
 receipt[role]=json.loads(raw); print(json.dumps({'role':role,'removed':len(receipt[role]['removed']),'roots_absent':True}),flush=True)
r.save(r.O/'EXACT_CLEANUP_RECEIPT.json',receipt)
