"""Read exact supplied paths; preserve public-source directories as evidence."""
import datetime as dt, hashlib,json,os,pathlib,pwd,socket,stat,sys
role=sys.argv[1]
targets={
 'ansible':('ansible01','server01_ansible',['/home/server01_ansible/FDS_CICD_AC09_20261015_1535']),
 'control01':('k8s-control01','server02',['/home/server02/FDS_AC09_ConsoleRestore_20261015']),
 'runner':('cicd-runner01','server01_cicd-runner',['/home/server01_cicd-runner/FDS_CICD_DeployInputs/deploy-cd01e613-d576-41eb-8354-8e9283d0f60d.json','/home/server01_cicd-runner/FDS_CICD_DeployInputs/deploy-3451e56c-57bc-490e-8d15-6cede958229f.json'])}
host,user,roots=targets[role];assert socket.gethostname()==host and pwd.getpwuid(os.getuid()).pw_name==user
out={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'host':host,'user':user,'roots':{},'public_source_dirs_retained':[],'mutation':False}
def item(p):
 s=p.lstat();assert not p.is_symlink() and s.st_uid==os.getuid()
 result={'path':str(p),'mode':stat.S_IMODE(s.st_mode),'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'nlink':s.st_nlink,'type':'dir' if stat.S_ISDIR(s.st_mode) else 'file'}
 if result['type']=='file':
  assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<4*1024*1024
  result['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return result
for name in roots:
 p=pathlib.Path(name);assert p.is_absolute() and p.resolve()==p
 rows=[item(p)]
 if p.is_dir():rows.extend(item(x) for x in sorted(p.rglob('*')))
 out['roots'][name]=rows
for p in sorted(pathlib.Path.home().glob('FDS_NativeProbeSource.*')):
 s=p.lstat()
 if s.st_mtime>=dt.datetime.fromisoformat('2026-10-15T15:35:00+09:00').timestamp():
  assert p.is_dir() and not p.is_symlink()
  out['public_source_dirs_retained'].append({'root':item(p),'files':[item(x) for x in sorted(p.iterdir())]})
if role=='runner':
 out['sockets']={str(n):(pathlib.Path.home()/'FDS_DeploySockets'/('r'+str(n)+'.sock')).exists() for n in (38693979785,38694721511)}
print(json.dumps(out))
