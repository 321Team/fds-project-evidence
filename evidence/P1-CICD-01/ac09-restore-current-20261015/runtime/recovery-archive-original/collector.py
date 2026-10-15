import base64,hashlib,json,os,pathlib,pwd,socket,stat
assert socket.gethostname()=='k8s-control01' and pwd.getpwuid(os.getuid()).pw_name=='server02'
p=pathlib.Path('/home/server02/FDS_AC09_ConsoleRestore_20261015/recovery.tar')
s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and s.st_size<1024*1024
with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW),'rb') as f:raw=f.read()
assert s.st_mtime_ns==p.lstat().st_mtime_ns
print(json.dumps({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'body_b64':base64.b64encode(raw).decode()}))
