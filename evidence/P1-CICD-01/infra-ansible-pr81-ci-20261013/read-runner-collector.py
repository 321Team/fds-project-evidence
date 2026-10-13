
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

assert out['user']=='server01_cicd-runner' and out['home']=='/home/server01_cicd-runner'
out['kit']=kitmeta('/home/server01_cicd-runner/ansible-pr63-runner.nrPxm06G/FDS_Ansible_Actions_Runner_v1_3')
out['guard']=kitmeta('/home/server01_cicd-runner/ansible-pr63-runner.nrPxm06G/FDS_Ansible_Runner_Input_Guard_v1_0')
out['old_packet_paths_present']=[str(p) for p in pathlib.Path(out['home']).glob('ansible-runner-token-ci*.json*')]
print(json.dumps(out))
