"""Future Linux operator staging only; exact archive + fresh owned destination.

Reads this one non-secret archive then passes bytes to the existing ansible-verify
account using sudo -n. No Podman invocation or role execution.
"""
import argparse,hashlib,io,json,os,pathlib,pwd,re,subprocess,tarfile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=pathlib.Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--session',required=True)
    a=p.parse_args()
    assert pwd.getpwuid(os.getuid()).pw_name=='server01_cicd-runner'
    assert re.fullmatch(r'p1-role-[0-9a-f]{16}',a.session) and re.fullmatch(r'[a-f0-9]{64}',a.sha256)
    raw=a.input.read_bytes();assert len(raw)<40_000_000 and hashlib.sha256(raw).hexdigest()==a.sha256
    code='''import hashlib,io,json,os,pathlib,stat,sys,tarfile
name,sha=sys.argv[1:];os.umask(0o077);assert os.getuid()==1001
raw=sys.stdin.buffer.read(40_000_001);assert len(raw)<40_000_000 and hashlib.sha256(raw).hexdigest()==sha
root=pathlib.Path('/home/ansible-verify')/name
assert root.parent==pathlib.Path('/home/ansible-verify') and not root.exists()
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tar:
 members=tar.getmembers();assert len({m.name for m in members})==len(members)
 for m in members:
  parts=pathlib.PurePosixPath(m.name).parts
  assert parts and parts[0]=='kit' and not m.name.startswith('/') and '..' not in parts
  assert m.isdir() or m.isfile()
 root.mkdir(mode=0o700)
 for m in members:
  dest=root/m.name
  if m.isdir():dest.mkdir(mode=0o700,exist_ok=False)
  else:
   dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
   fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as f:f.write(tar.extractfile(m).read())
   dest.chmod(m.mode&0o777)
manifest=json.loads((root/'kit/manifest.json').read_bytes())
for rel,row in manifest['files'].items():
 path=root/'kit'/rel;assert path.is_file() and not path.is_symlink()
 assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'] and stat.S_IMODE(path.stat().st_mode)==row['mode']
print(json.dumps({'status':'STAGED_ONLY','root':str(root),'archive_sha256':sha,'manifest_sha256':hashlib.sha256((root/'kit/manifest.json').read_bytes()).hexdigest(),'uid':os.getuid(),'container_created':False}))
'''
    argv=['sudo','-n','-u','ansible-verify','env','HOME=/home/ansible-verify','XDG_RUNTIME_DIR=/run/user/1001',
          '/usr/bin/python3','-I','-B','-c',code,a.session,a.sha256]
    r=subprocess.run(argv,input=raw,capture_output=True,timeout=60)
    print(r.stdout.decode(),end='')
    if r.stderr:print(r.stderr.decode(),file=__import__('sys').stderr,end='')
    return r.returncode

if __name__=='__main__':raise SystemExit(main())
