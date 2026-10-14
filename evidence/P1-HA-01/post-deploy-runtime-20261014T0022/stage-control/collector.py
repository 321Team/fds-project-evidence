HOST='k8s-control01'
UID=0
TARGET='/var/tmp/p1-ha-20261014-0015'
FILES={}
import os,pathlib,stat,socket,json,hashlib,base64,datetime
assert socket.gethostname()==HOST and os.geteuid()==UID
p=pathlib.Path(TARGET)
assert p.parent.is_dir() and not p.parent.is_symlink() and not os.path.lexists(p)
os.umask(0o077);p.mkdir(mode=0o700)
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'directory':str(p),'files':[],'probe_runs':0,'ha_mutations':0}
assert stat.S_IMODE(p.stat().st_mode)==0o700 and p.stat().st_uid==UID
for name,item in FILES.items():
 raw=base64.b64decode(item['content']);assert hashlib.sha256(raw).hexdigest()==item['sha256']
 f=p/name;fd=os.open(f,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 assert f.stat().st_uid==UID and stat.S_IMODE(f.stat().st_mode)==0o600 and hashlib.sha256(f.read_bytes()).hexdigest()==item['sha256']
 out['files'].append({'name':name,'sha256':item['sha256'],'uid':f.stat().st_uid,'mode':'0600'})
print(json.dumps(out))
