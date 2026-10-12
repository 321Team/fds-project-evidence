import os,stat,socket,pwd,json,hashlib,subprocess,datetime
from pathlib import Path
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000
home=Path(pwd.getpwuid(os.getuid()).pw_dir);assert str(home)=='/home/server01_cicd-runner'
def meta(p):
 if not p.exists() and not p.is_symlink():return {'path':str(p),'exists':False}
 s=p.lstat();return {'path':str(p),'exists':True,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'symlink':p.is_symlink(),'directory':p.is_dir(),'size':s.st_size}
out={'started_at_utc':now(),'host':socket.gethostname(),'uid':os.geteuid(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'home':meta(home),'commands':[],'paths':[],'supply':[],'mutation':False,'credential_read':False}
commands=[['/usr/bin/rpm','-q','skopeo','podman'],['/usr/bin/rpm','-V','skopeo'],['/usr/bin/skopeo','--version'],['/usr/bin/skopeo','copy','--help'],['/usr/bin/skopeo','inspect','--help']]
for argv in commands:
 try:
  p=subprocess.run(argv,capture_output=True,timeout=15);q={'argv':argv,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
  if '--help' in argv:q['supported_flags']={flag:flag.encode() in p.stdout for flag in ['--preserve-digests','--dest-authfile','--dest-tls-verify','--raw','--authfile','--tls-verify']}
  else:q['stdout']=p.stdout.decode(errors='replace')[:4096]
 except FileNotFoundError:q={'argv':argv,'error':'EXECUTABLE_NOT_FOUND'}
 out['commands'].append(q)
for name in ['FDS_CICD_PushInputs','FDS_CICD_DeployInputs','FDS_CICD_PushClaims','FDS_CICD_DeployClaims','FDS_DeploySockets']:
 p=home/name;q=meta(p)
 if q.get('directory') and not q.get('symlink'):
  entries=sorted(p.iterdir());assert len(entries)<=100
  q['entries']=[meta(x) for x in entries]
 out['paths'].append(q)
roots=sorted(home.glob('FDS_CICD_AppWorkflow.*'));assert len(roots)<=30
for root in roots:
 m=meta(root)
 if m.get('symlink') or not m.get('directory'):continue
 result=root/'result.json'
 if not result.is_file() or result.is_symlink():continue
 d=json.loads(result.read_bytes());ctx=d.get('context',{})
 row={'directory':m,'context':ctx,'APP_WORKFLOW':d.get('APP_WORKFLOW'),'APP_TEST_BUILD_SCAN':d.get('APP_TEST_BUILD_SCAN'),'result_sha256':sha(result)}
 if str(ctx.get('run_id'))=='37890963668':
  row['files']=[]
  for name in ['result.json','build-scan/result.json','build-scan/scan/result.json','build-scan/transaction-api.oci.tar','build-scan/fds-engine.oci.tar']:
   p=root/name;s0=p.stat();assert p.is_file() and not p.is_symlink()
   q=meta(p);q['sha256']=sha(p);s1=p.stat();assert (s0.st_ino,s0.st_size,s0.st_mtime_ns)==(s1.st_ino,s1.st_size,s1.st_mtime_ns)
   row['files'].append(q)
 out['supply'].append(row)
out['finished_at_utc']=now();print(json.dumps(out))
