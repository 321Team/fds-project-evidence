
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

assert out['user']=='server01_ansible' and out['home']=='/home/server01_ansible'
out['kit']=kitmeta('/home/server01_ansible/ansible-ipc-admin.9LFS6d7N/FDS_Ansible_Actions_Runner_v1_3')
print(json.dumps(out))
