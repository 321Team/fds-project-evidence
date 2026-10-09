import datetime,hashlib,json,pathlib,re,shlex,subprocess
r=pathlib.Path(__file__).resolve().parent;out=r/'private/consumer-supply-37859961937';out.resolve(strict=True)
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T08:55:00+09:00','STOP insufficient window'
assert not (out/'invocation.json').exists(),'STOP already attempted'
ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01']
prep="import os,pwd,socket,tempfile; assert socket.gethostname()=='ansible01' and pwd.getpwuid(os.geteuid()).pw_name=='server01_ansible'; os.umask(0o077); print(tempfile.mkdtemp(prefix='app-supply-check.',dir='/home/server01_ansible'))"
remote=subprocess.check_output(ssh+['python3.12 -I -c '+shlex.quote(prep)],timeout=15).decode().strip()
assert re.fullmatch('/home/server01_ansible/app-supply-check[.][A-Za-z0-9_]+',remote),remote
(out/'remote-path.txt').write_text(remote+'\n')
# mkdtemp can include underscores; collector path pattern must match the concrete name.
assert re.fullmatch('/home/server01_ansible/app-supply-check[.][A-Za-z0-9]+',remote),'STOP unexpected folder characters; leave empty folder for scoped cleanup'
started=now()
scp=['scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8',str(out/'input.tar'),str(r/'private/app-supply-37859961937/supply.zip'),'fds-ansible01:'+remote+'/']
p=subprocess.run(scp,capture_output=True,timeout=180);(out/'transfer.stderr.txt').write_bytes(p.stderr);assert p.returncode==0,'transfer failed'
h=hashlib.sha256((out/'input.tar').read_bytes()).hexdigest()
extract=f"import hashlib,pathlib,tarfile; p=pathlib.Path({remote!r}); t=p/'input.tar'; assert hashlib.sha256(t.read_bytes()).hexdigest()=={h!r}; tarfile.open(t).extractall(p,filter='data')"
cmd='python3.12 -I -B -c '+shlex.quote(extract)+' && python3.12 -I -B '+shlex.quote(remote+'/verify_consumer_supply.py')
p=subprocess.run(ssh+[cmd],capture_output=True,timeout=180)
(out/'stdout.json').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
meta={'started_at_kst':started,'finished_at_kst':now(),'host':'ansible01','account':'server01_ansible','remote_directory':remote,'command':ssh+[cmd],
      'rc':p.returncode,'input_tar_sha256':h,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'transfer_rc':0,'runtime_changes':'NONE; private temporary files only'}
(out/'invocation.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(meta,indent=2))
if p.returncode:print(p.stderr.decode(errors='replace'));raise SystemExit(p.returncode)
result=json.loads(p.stdout);print(json.dumps({k:result[k] for k in ('calls_passed','negative_cases','final_original_revalidation','source_approval','runtime_apply')},indent=2))
