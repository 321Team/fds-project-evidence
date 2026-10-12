"""One exclusively-created archive received from the existing strict SSH channel."""
import hashlib,json,os,pathlib,sys
root=pathlib.Path('/root/p1-oid02-20261013-r1')
name,expected,size=sys.argv[1:];size=int(size)
assert os.geteuid()==0 and name in ['kube-controllers-linux-amd64.oci.tar','coredns-linux-amd64.oci.tar'] and 0<size<128*1024*1024
assert root.is_dir() and not root.is_symlink() and root.stat().st_mode&0o777==0o700
fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);h=hashlib.sha256();n=0
with os.fdopen(fd,'wb') as f:
 while True:
  b=sys.stdin.buffer.read(1024*1024)
  if not b:break
  n+=len(b);assert n<=size;h.update(b);f.write(b)
 f.flush();os.fsync(f.fileno())
assert n==size and h.hexdigest()==expected,'RECEIVE_MISMATCH'
print(json.dumps({'status':'RECEIVED_HASH_VERIFIED','path':str(root/name),'size':n,'sha256':h.hexdigest()}))
