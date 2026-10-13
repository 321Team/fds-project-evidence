
import datetime, hashlib, json, os, pathlib, pwd, socket, stat, subprocess
def filemeta(path):
 p=pathlib.Path(path);s=p.lstat()
 assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not p.is_symlink()
 return {'path':str(p),'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode)),
         'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def kitmeta(path):
 p=pathlib.Path(path);rows=(p/'SHA256SUMS').read_text().splitlines()
 values=[]
 for row in rows:
  expected,name=row.split('  ',1);assert not name.startswith('/') and '..' not in pathlib.PurePosixPath(name).parts
  m=filemeta(p/name);assert m['sha256']==expected;values.append(m)
 return {'root':str(p),'manifest':filemeta(p/'SHA256SUMS'),'files':values}
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),
     'user':pwd.getpwuid(os.getuid()).pw_name,'uid':os.getuid(),'home':os.environ.get('HOME'),
     'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}

assert out['user']=='ansible-verify' and out['home']=='/home/ansible-verify'
p=pathlib.Path('/home/ansible-verify/ansible-actions-1c6c4123b62a4ebcb4b1b9042a02e332/evidence/PREPARED.json')
out['prepared_meta']=filemeta(p)
value=json.loads(p.read_text())
keys=['status','repository','runner_version','bundle_sha256','image_id','container_cleanup','created_at']
out['prepared']={k:value[k] for k in keys}
assert value['status']=='PASS_PREPARE' and value['repository']=='321Team/infra-ansible'
assert value['bundle_sha256']=='e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6'
os.chdir('/tmp')
r=subprocess.run(['podman','ps','-a','--format','json'],capture_output=True,check=True,timeout=20)
out['containers']=[{k:x.get(k) for k in ['Id','Names','State']} for x in json.loads(r.stdout)]
r=subprocess.run(['podman','image','exists',value['image_id']],capture_output=True,timeout=20)
out['prepared_image_exists_rc']=r.returncode
r=subprocess.run(['pgrep','-u','1001','-f','runner.py'],capture_output=True,timeout=10)
assert r.returncode in (0,1)
out['runner_process_present']=r.returncode==0
print(json.dumps(out))
