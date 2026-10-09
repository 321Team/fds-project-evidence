"""Remove only the verified dedicated temporary workspace after receipt."""
import datetime,hashlib,json,pathlib,shlex,subprocess,zipfile
r=pathlib.Path(__file__).resolve().parent;out=r/'private/consumer-supply-37859961937'
inv=json.loads((out/'invocation.json').read_bytes());raw=(out/'stdout.json').read_bytes()
assert inv['rc']==0 and hashlib.sha256(raw).hexdigest()==inv['stdout_sha256']
d=json.loads(raw);assert d['final_original_revalidation']=='PASS'
expected=dict(d['input_hashes']);expected['INPUT_HASHES.json']=hashlib.sha256((out/'bundle/INPUT_HASHES.json').read_bytes()).hexdigest()
expected['input.tar']=inv['input_tar_sha256'];expected['result.json']=inv['stdout_sha256'];expected['supply.zip']=d['archive_sha256']
with zipfile.ZipFile(r/'private/app-supply-37859961937/supply.zip') as z:
    for i in z.infolist():
        h=hashlib.sha256(z.read(i)).hexdigest();expected['supplied/'+i.filename]=h
        if i.filename in ('builder.oci.tar','runtime.oci.tar'):expected['staged/'+i.filename]=h
        elif i.filename.startswith('profiles/'):expected['staged/'+i.filename.removeprefix('profiles/')]=h
payload={'directory':inv['remote_directory'],'expected':expected}
code="""import datetime,hashlib,json,pathlib,pwd,shutil,socket,sys
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
"""
(out/'cleanup-remote.py').write_text(code,encoding='utf-8',newline='\n')
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01','python3.12 -I -B -c '+shlex.quote(code)]
p=subprocess.run(cmd,input=json.dumps(payload).encode(),capture_output=True,timeout=60)
(out/'cleanup.stdout.json').write_bytes(p.stdout);(out/'cleanup.stderr.txt').write_bytes(p.stderr)
(out/'cleanup.invocation.json').write_text(json.dumps({'rc':p.returncode,'remote_script_sha256':hashlib.sha256(code.encode()).hexdigest(),'payload_sha256':hashlib.sha256(json.dumps(payload).encode()).hexdigest(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest()},indent=2)+'\n')
(out/'cleanup-payload.json').write_bytes(json.dumps(payload).encode())
assert p.returncode==0,p.stderr.decode(errors='replace');print(p.stdout.decode())
