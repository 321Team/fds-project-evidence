import datetime,hashlib,json,pathlib,pwd,shutil,socket,sys
p=json.load(sys.stdin);root=pathlib.Path(p['directory'])
assert socket.gethostname()=='ansible01' and pwd.getpwuid(__import__('os').geteuid()).pw_name=='server01_ansible'
assert str(root)=='/home/server01_ansible/app-supply-check.vbuuk32j' and root.resolve(strict=True)==root and not root.is_symlink()
items=list(root.rglob('*'));assert all(not f.is_symlink() for f in items)
files={f.relative_to(root).as_posix():f for f in items if f.is_file()}
assert set(files)==set(p['expected']),'STOP unexpected files'
for n,f in files.items():
 with f.open('rb') as s:assert hashlib.file_digest(s,'sha256').hexdigest()==p['expected'][n],n
dirs={f.relative_to(root).as_posix() for f in items if f.is_dir()};wanted=set()
for n in files:
 for parent in pathlib.PurePosixPath(n).parents:
  if str(parent)!='.':wanted.add(str(parent))
assert dirs==wanted,'STOP unexpected directories'
shutil.rmtree(root);assert not root.exists()
print(json.dumps({'schema':'fds.consumer-temp-cleanup.v1','finished_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'directory':str(root),'verified_files':len(files),'removed':True,'scope':'Exact temporary workspace only; every file hash checked against local receipts'}))
