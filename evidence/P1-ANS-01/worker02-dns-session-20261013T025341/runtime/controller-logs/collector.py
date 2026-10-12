ROOT='/home/server01_ansible/p1-worker02-dns-20261013-r1'
import datetime,hashlib,json,os,pathlib,stat
assert os.uname().nodename=='ansible01' and os.geteuid()==1000
root=pathlib.Path(ROOT);out={'host':'ansible01','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':ROOT,'files':[],'directories':[],'status':'PRIVATE_LOGS_COLLECTED'}
total=0
for p in [root]+sorted(root.rglob('*')):
 s=p.lstat();assert not p.is_symlink() and s.st_uid==1000
 if p.is_dir():
  assert stat.S_IMODE(s.st_mode)==0o700;out['directories'].append({'path':str(p),'mode':'0700','uid':s.st_uid})
 else:
  assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  b=p.read_bytes();total+=len(b);assert len(b)<256000 and total<1048576
  out['files'].append({'path':p.relative_to(root).as_posix(),'uid':s.st_uid,'gid':s.st_gid,'mode':'0600','size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'raw_utf8':b.decode('utf-8')})
assert len(out['files'])<=40
print(json.dumps(out))
