import datetime,json,os,pathlib,pwd,socket,stat
paths=['/home/server01_ansible/ansible-runner-token-m0b3cyfd.json', '/home/server01_ansible/ansible-runner-token-1qbirnu8.json', '/home/server01_ansible/ansible-runner-token-m83_ndt9.json', '/home/server01_ansible/ansible-runner-token-vju00pnh.json', '/home/server01_ansible/ansible-runner-token-mgj37_bj.json', '/home/server01_ansible/ansible-runner-token-qevmn2ca.json', '/home/server01_ansible/ansible-runner-token-41liumos.json', '/home/server01_ansible/ansible-runner-token-i7imped0.json', '/home/server01_ansible/ansible-runner-token-jvjrhbng.json', '/home/server01_ansible/ansible-runner-token-spac7gd9.json', '/home/server01_ansible/ansible-runner-token-94pel4u4.json', '/home/server01_ansible/ansible-runner-token-mcudiveg.json', '/home/server01_ansible/ansible-runner-token-p3a_yobr.json', '/home/server01_ansible/ansible-runner-token-kcf38_ue.json', '/home/server01_ansible/ansible-runner-token-233maro6.json', '/home/server01_ansible/ansible-runner-token-jwbk7jmr.json', '/home/server01_ansible/ansible-runner-token-k8xzzi1p.json', '/home/server01_ansible/ansible-runner-token-lefav9zh.json', '/home/server01_ansible/ansible-runner-token-2n6cj06d.json', '/home/server01_ansible/ansible-runner-token-y7rw22at.json', '/home/server01_ansible/ansible-runner-token-28z3k884.json', '/home/server01_ansible/ansible-runner-token-bg_s77ew.json', '/home/server01_ansible/ansible-runner-token-xvzln29_.json', '/home/server01_ansible/ansible-runner-token-diszdbny.json', '/home/server01_ansible/ansible-runner-token-ktg9bfqe.json', '/home/server01_ansible/ansible-runner-token-d0sn8ine.json', '/home/server01_ansible/ansible-runner-token-nq00ozqn.json', '/home/server01_ansible/ansible-runner-token-p7xtqw0x.json']
rows=[]
for name in paths:
 p=pathlib.Path(name)
 assert p.parent==pathlib.Path('/home/server01_ansible') and p.name.startswith('ansible-runner-token-') and p.suffix=='.json'
 s=p.lstat()
 rows.append({'path':name,'dev':s.st_dev,'ino':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),
  'regular':stat.S_ISREG(s.st_mode),'nlink':s.st_nlink,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,
  'mtime_utc':datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc).isoformat(),
  'ctime_utc':datetime.datetime.fromtimestamp(s.st_ctime,datetime.timezone.utc).isoformat()})
print(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),
 'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'uid':os.getuid(),'user':pwd.getpwuid(os.getuid()).pw_name,
 'scope':'lstat only; no packet contents or token hashes; no mutation','packets':rows}))
