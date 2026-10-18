"""One adopted paired precheck. Central dispatch only, under the documented env -i."""
import base64,datetime as dt,hashlib,json,os,pathlib,pwd,shutil,socket,stat,subprocess,sys
import yaml
P=pathlib.Path
SRC=P('/home/server01_ansible/worker02-session-plan-3hetha3t/source')
HEAD='0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea'
HOME=P('/home/server01_ansible')
WORK=HOME/'ntp-paired-precheck-20261018-1940'
CORE=HOME/'ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin'
RUNTIME_SHA='ad2ef8749403de92bda060f9d51f1fb65862d842ab87be60f826fe0490dad6f4'
RUNTIME_BYTES=base64.b64decode('ewogICJjcl9udHBfbWlncmF0ZV9tYWluIjogdHJ1ZSwKICAiY3JfbnRwX3NvdXJjZV91cHN0cmVhbXMiOiBbCiAgICAiMTYyLjE1OS4yMDAuMSIsCiAgICAiMTYyLjE1OS4yMDAuMTIzIgogIF0sCiAgImNyX250cF9wcm9iZV9ldmlkZW5jZV9kaXIiOiAiL2hvbWUvc2VydmVyMDFfYW5zaWJsZS9udHAtcGFpcmVkLXByZWNoZWNrLTIwMjYxMDE4LTE5NDAvZXZpZGVuY2UiLAogICJjcl9udHBfcHJvYmVfcnVuX2lkIjogIm50cF9wYWlyZWRfcHJlY2hlY2tfMjAyNjEwMThfMTk0MCIsCiAgImNyX250cF9wcm9iZV9zb3VyY2VfaGVhZCI6ICIwZDU4NTk4ZDhhM2NlNzdjY2Q3ZWFhOWUxZGZiYTgyMGIwYTQzNmVhIiwKICAiY3JfbnRwX3Byb2JlX2lucHV0X3NoYTI1NiI6ICIzY2FlY2E1M2IyNjhlNzZiMzUxZjY1MTRhNDkwYjY5MDYxODc4MmNhMWYwNTk3MTVkNDcyNDMzYTZjZTE3YjQ4Igp9Cg==',validate=True)
TARGETS=[{'host': 'k8s-control01', 'ip': '10.1.93.102', 'machine_id': '43795458b5574726af93975cb8625c2b', 'boot_id': '8c78b577-62f8-4546-aac1-0b371b707bc5', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '5ebb2911e7b1e2a726f0a24dfacb1269c110897af80fd474771c5de1071b716b', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': '3035851d67a1ec1db89e3e5d2f3d9dc3202fb09393969bc9d8900d09918d88be', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}, {'host': 'k8s-control02', 'ip': '10.1.93.103', 'machine_id': '6467ff4113f945a4b100a4ae32647d81', 'boot_id': '17c645d2-2707-4c1f-abde-64872f345e54', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '3d516d3aad2498b4fe274a2e9162d3f36f078b78e031c1eac7df92eba816057d', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': 'a272059d959866ceb9781c29336133efd516400744105e98b6daf1770e643daa', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}, {'host': 'k8s-control03', 'ip': '10.1.93.104', 'machine_id': '05447f80fe754454a3c5c8f09f4c9ea6', 'boot_id': '1fb52585-01d5-4e6d-9565-04a6396504b0', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '3d516d3aad2498b4fe274a2e9162d3f36f078b78e031c1eac7df92eba816057d', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': '98789588dd7b3b822915397e4204107d221b0302035218df62471c5542bc4ccb', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}, {'host': 'k8s-worker01', 'ip': '10.1.93.105', 'machine_id': '19fba8c06cfa4ebf876bacbbc3423bb1', 'boot_id': 'bc7023a8-d697-45cb-afdb-d56b162965ce', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '3d516d3aad2498b4fe274a2e9162d3f36f078b78e031c1eac7df92eba816057d', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': '8eb9afd00b1b8f10489236323000c98bcf841d79b25bb6107c1365227fcd9e78', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}, {'host': 'k8s-worker02', 'ip': '10.1.93.107', 'machine_id': 'bed0e37c3c234c5e85c5b5d352f6fc65', 'boot_id': '2747f3a9-6b9d-43ea-a374-d0d38de92ca0', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '3d516d3aad2498b4fe274a2e9162d3f36f078b78e031c1eac7df92eba816057d', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': '35638fd246b6408fdbaebf9938a933ecd20689a984b79ac378b0a975cfb7b539', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}, {'host': 'k8s-worker03', 'ip': '10.1.93.108', 'machine_id': '0bb03794b5b04dc4bded6bd75d63f701', 'boot_id': '2e3c5d9a-b386-4c20-8c0b-f5f7f0e10b0c', 'files': [{'path': '/etc/chrony.conf', 'sha256': '949287680df0590a15a68cdf9236f7c7176bd4355eedbbe858f9c66e18e3075e', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/etc/chrony.d/50-cr-p1-ntp-01-01.conf', 'sha256': '3d516d3aad2498b4fe274a2e9162d3f36f078b78e031c1eac7df92eba816057d', 'uid': 0, 'gid': 0, 'mode': '0o644'}, {'path': '/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json', 'sha256': '4744a9a0b71f937286059a1608935fea6e732861829f4080da09ae9242a9840d', 'uid': 0, 'gid': 0, 'mode': '0o600'}]}]
SOURCE_HASHES={'ansible.cfg': '73e6f6b5844a7a2dee8cf042b67a1c7b61c3e4b4198f4f7f7b65907e883de90e', 'inventory/hosts.yml': '15daf8f9257473772f8ecd7cfaf08369c88fd5c3775cb3bf67fcd95a1122ec0a', 'scripts/cr-p1-ntp-01-01-run.sh': '3b89f74e31b000be343e7e512bf12369708b7ab334cd54a7ae1d0c0dcce20171', 'scripts/lib/ansible-engine.sh': 'aedf6cd8d2fa656784e5f93e4d507582efb39755655d2e2ad0696e6353f316dd', 'tools/ntp-workflow-lock.py': '91b7e14272c8bc470ba4d403d1d32aad889aeca8dd14760230da16955b10d218', 'playbooks/cr-p1-ntp-01-01-precheck.yml': 'be351f4eaddead684be1b240a6b1ab69e708b272ff1f9de5399021342ae9c7ee', 'roles/ntp_source/tasks/main.yml': '472555824ede130fed517589c2b4c66dc2c9e5b38b5343aed115db6430a3fe83', 'roles/ntp_source/tasks/_migration.yml': 'a08b93d3480c7b87a7af6840049594586384af60fc1a87deba57a538ae385d2d', 'roles/ntp_source/tasks/verify.yml': '1179ede0c2931df4a822ddffd84aec19c41791d5e6f1a4f21908b2b0ae03734d', 'library/fds_ntp_migration.py': '2e1ea06aebf856f42b950242e1cc913b4eda30173ebf19f0dd157f0181d24983', 'module_utils/fds_ntp_policy.py': '47ce10e94ea91eaa120d253ee99374502e3427cb83617f372f1a3e0f092e194a'}
INNER_PREFIX=['/usr/bin/ssh', '-F', '/dev/null', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes', '-o', 'ForwardAgent=no', '-o', 'ClearAllForwardings=yes', '-o', 'ControlMaster=no', '-o', 'ControlPath=none', '-o', 'UpdateHostKeys=no']
CONFIG_SHA='73e6f6b5844a7a2dee8cf042b67a1c7b61c3e4b4198f4f7f7b65907e883de90e'
ENV={'HOME':str(HOME),'USER':'server01_ansible','LOGNAME':'server01_ansible','PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
NODE_READER=r'''
import datetime as dt,hashlib,json,os,pathlib,socket,stat
P=pathlib.Path
def text(path):return P(path).read_text().strip()
out={'host':socket.gethostname(),'machine_id':text('/etc/machine-id'),'boot_id':text('/proc/sys/kernel/random/boot_id'),'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'files':[]}
assert os.geteuid()==0 and out['host']==EXPECTED['host']
assert out['machine_id']==EXPECTED['machine_id'] and out['boot_id']==EXPECTED['boot_id']
for expected in EXPECTED['files']:
 p=P(expected['path']);s=p.lstat()
 assert stat.S_ISREG(s.st_mode) and not stat.S_ISLNK(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and s.st_size<=1048576
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  start=os.fstat(fd);assert (start.st_dev,start.st_ino)==(s.st_dev,s.st_ino)
  raw=b''
  while True:
   chunk=os.read(fd,min(65536,1048577-len(raw)))
   if not chunk:break
   raw+=chunk;assert len(raw)<=1048576
  end=os.fstat(fd)
 finally:os.close(fd)
 assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(end.st_dev,end.st_ino,end.st_size,end.st_mtime_ns,end.st_ctime_ns)
 out['files'].append({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'bytes':len(raw)})
out['legacy_baseline_absent']=not os.path.lexists('/var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-dropin.json')
out['boot_stable']=out['boot_id']==text('/proc/sys/kernel/random/boot_id')
out['matches']=out['boot_stable'] and out['legacy_baseline_absent'] and all(all(actual[k]==expected[k] for k in ['path','sha256','uid','gid','mode']) for actual,expected in zip(out['files'],EXPECTED['files']))
print(json.dumps(out),flush=True)
raise SystemExit(0 if out['matches'] else 1)
'''
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):
 data=value if isinstance(value,bytes) else (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 fd=os.open(WORK/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def git(*args):
 q=subprocess.run(['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-c','core.untrackedCache=false','-C',str(SRC),*args],capture_output=True,env=ENV,check=True)
 return q.stdout.decode().strip()
def source_state():
 assert os.getuid()==os.geteuid()==1000 and os.getgid()==os.getegid()==1000
 assert pwd.getpwuid(os.geteuid()).pw_name=='server01_ansible' and socket.gethostname()=='ansible01'
 assert P('/etc/machine-id').read_text().strip()=='17501f5b4e3f4fc1b97cdc82ffc45b83'
 assert P('/proc/sys/kernel/random/boot_id').read_text().strip()=='0317c0f8-cdc9-4c5e-a28e-48961c75e62e'
 assert HOME.resolve()==HOME and SRC.resolve()==SRC
 h=HOME.lstat();assert h.st_uid==h.st_gid==1000 and stat.S_IMODE(h.st_mode)==0o700
 assert git('rev-parse','HEAD')==HEAD
 assert not git('status','--porcelain','--untracked-files=no','--ignore-submodules=none')
 assert not git('ls-files','--others','--exclude-standard','--','inventory','roles','scripts','tools','library','module_utils','playbooks','ansible.cfg')
 hashes={name:sha((SRC/name).read_bytes()) for name in SOURCE_HASHES}
 assert hashes==SOURCE_HASHES and hashes['ansible.cfg']==CONFIG_SHA
 inv=yaml.safe_load((SRC/'inventory/hosts.yml').read_text())
 actual={h:v['ansible_host'] for g in inv['all']['children']['k8s_nodes']['children'].values() for h,v in g['hosts'].items()}
 assert actual=={t['host']:t['ip'] for t in TARGETS}
 assert inv['all']['vars']['ansible_user']=='svc_ansible' and inv['all']['vars']['ansible_python_interpreter']=='/usr/bin/python3'
 v=yaml.safe_load((SRC/'inventory/group_vars/all.yml').read_text())
 assert v['cr_ntp_migrate_main'] is False and v['cr_ntp_source_upstreams']==[]
 assert v['cr_ntp_change_id']=='CR-P1-NTP-01-01' and v['cr_ntp_state_dir']=='/var/lib/fds-change/CR-P1-NTP-01-01'
 assert v['cr_ntp_source_host']=='k8s-control01' and v['cr_ntp_source_ip']=='10.1.93.102'
 assert v['cr_ntp_client_ips']==['10.1.93.103','10.1.93.104','10.1.93.105','10.1.93.107','10.1.93.108']
 assert v['cr_ntp_dropin_path']=='/etc/chrony.d/50-cr-p1-ntp-01-01.conf' and v['cr_ntp_offset_max_ms']==100
 import shlex
 assert shlex.split(v['ansible_ssh_common_args'])==['-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=%d/.ssh/known_hosts','-o','IdentitiesOnly=yes']
 for path in [HOME/'.ssh/p1_ansible_ed25519',HOME/'.ssh/known_hosts']:
  s=path.lstat();assert stat.S_ISREG(s.st_mode) and not path.is_symlink() and s.st_uid==s.st_gid==1000 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
 for cli in ['ansible','ansible-playbook','ansible-inventory','ansible-config']:assert (CORE/cli).is_file() and os.access(CORE/cli,os.X_OK)
 return {'head':HEAD,'tracked_dirty':False,'source_hashes':hashes,'inventory_targets':actual,'boot_id':'0317c0f8-cdc9-4c5e-a28e-48961c75e62e','uid':1000,'gid':1000}
def read_targets(phase):
 (WORK/phase).mkdir(mode=0o700)
 rows=[]
 for target in TARGETS:
  payload=('EXPECTED='+repr(target)+'\n'+NODE_READER).encode()
  argv=INNER_PREFIX+['svc_ansible@'+target['ip'],'sudo -n /usr/bin/python3 -B -I -S -']
  save(phase+'/'+target['host']+'.intent.json',{'at_kst':now(),'argv':argv,'payload_sha256':sha(payload),'retry':False})
  # Read-only query. Preserve real foreground return; no timeout kill or retry.
  q=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=ENV)
  out,err=q.communicate(payload)
  save(phase+'/'+target['host']+'.json',out);save(phase+'/'+target['host']+'.stderr',err)
  row={'host':target['host'],'rc':q.returncode,'stdout_sha256':sha(out),'stderr_sha256':sha(err)}
  if q.returncode==0:
   value=json.loads(out);row['matches']=value['matches']
  else:row['matches']=False
  save(phase+'/'+target['host']+'.receipt.json',row);rows.append(row)
  if phase=='before' and not row['matches']:break
 save(phase+'/SUMMARY.json',rows)
 return len(rows)==6 and all(r['matches'] for r in rows)
def cleanup_owned(identity):
 assert WORK==HOME/'ntp-paired-precheck-20261018-1940' and WORK.resolve()==WORK
 root=WORK.lstat();assert (root.st_dev,root.st_ino)==identity and root.st_uid==1000 and stat.S_IMODE(root.st_mode)==0o700
 # Validate both trees before deleting either. Existing global lock stays intact.
 for name in ['tmp','cp']:
  target=WORK/name;s=target.lstat();assert stat.S_ISDIR(s.st_mode) and not target.is_symlink() and s.st_uid==1000
  for base,dirs,files in os.walk(target,followlinks=False):
   for child in dirs+files:
    p=P(base)/child;z=p.lstat()
    assert z.st_uid==1000 and not p.is_symlink()
    assert stat.S_ISDIR(z.st_mode) or (stat.S_ISREG(z.st_mode) and z.st_nlink==1)
 for name in ['tmp','cp']:shutil.rmtree(WORK/name)
 save('LOCAL_TEMP_CLEANUP.json',{'removed_owned_children':['tmp','cp'],'work_evidence_preserved':True,'remote_temp_absence_claimed':False,'existing_lock_deleted':False})
def main():
 assert sha(RUNTIME_BYTES)==RUNTIME_SHA
 runtime=json.loads(RUNTIME_BYTES)
 assert len(runtime)==6 and runtime['cr_ntp_migrate_main'] is True and runtime['cr_ntp_source_upstreams']==['162.159.200.1','162.159.200.123']
 assert not any(k in os.environ for k in ['CR_CHANGE_APPROVED','CR_NTP_WORKFLOW_LOCK_FD','FDS_ANSIBLE_ENGINE_DIR','FDS_ANSIBLE_ENGINE_VERSION'])
 os.umask(0o077)
 before_source=source_state() # No directory created before controller/source check.
 WORK.mkdir(mode=0o700) # Exact new root is the one-shot local claim; no reuse.
 root=WORK.lstat();identity=(root.st_dev,root.st_ino)
 stage='CREATED'
 try:
  save('CLAIM.json',{'at_kst':now(),'action':'existing paired precheck only','max_wrapper_calls':1,'source':str(SRC),'head':HEAD,'runtime_vars_sha256':RUNTIME_SHA,'work':str(WORK),'retry':False})
  save('SOURCE_BEFORE.json',before_source)
  for name in ['tmp','cp','evidence']:(WORK/name).mkdir(mode=0o700)
  save('runtime-vars.json',RUNTIME_BYTES)
  st=(WORK/'runtime-vars.json').lstat()
  assert stat.S_ISREG(st.st_mode) and st.st_uid==st.st_gid==1000 and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600
  assert sha((WORK/'runtime-vars.json').read_bytes())==RUNTIME_SHA
  save('RUNTIME_VARS_RECEIPT.json',{'sha256':RUNTIME_SHA,'uid':st.st_uid,'gid':st.st_gid,'mode':oct(stat.S_IMODE(st.st_mode)),'nlink':st.st_nlink})
  print('WORK='+str(WORK),flush=True)
  stage='TARGET_BEFORE'
  ready=read_targets('before')
  precheck_rc=125
  if ready:
   stage='PRECHECK'
   runenv=dict(ENV,ANSIBLE_CONFIG=str(SRC/'ansible.cfg'),ANSIBLE_PRIVATE_KEY_FILE=str(HOME/'.ssh/p1_ansible_ed25519'),ANSIBLE_LOCAL_TEMP=str(WORK/'tmp'),ANSIBLE_SSH_CONTROL_PATH_DIR=str(WORK/'cp'),ANSIBLE_SSH_ARGS='-C -o ControlMaster=no -o ControlPersist=no -o ConnectionAttempts=1 -o ConnectTimeout=10 -o BatchMode=yes',ANSIBLE_HOST_KEY_CHECKING='True',ANSIBLE_NOCOLOR='1',FDS_ANSIBLE_ENGINE_DIR=str(CORE),FDS_ANSIBLE_ENGINE_VERSION='2.21.3',CR_NTP_MIGRATE_MAIN='1',CR_NTP_RUNTIME_VARS_FILE=str(WORK/'runtime-vars.json'),CR_EVIDENCE_DIR=str(WORK/'evidence'))
   argv=['/bin/bash',str(SRC/'scripts/cr-p1-ntp-01-01-run.sh'),'precheck']
   save('PRECHECK_INTENT.json',{'at_kst':now(),'argv':argv,'cwd':str(SRC),'runtime_vars_sha256':RUNTIME_SHA,'retry':False})
   with (WORK/'precheck.log').open('xb') as log:
    child=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=SRC,env=runenv)
    save('PRECHECK_SPAWN.json',{'pid':child.pid,'at_kst':now()})
    precheck_rc=child.wait() # No timeout, kill, retry or process restart.
   save('PRECHECK_RETURN.json',{'rc':precheck_rc,'at_kst':now()})
  stage='AFTER'
  # Nonzero ordinary rc is still a foreground return. Signal exit remains hold.
  if precheck_rc<0 or precheck_rc>=128:
   save('HOLD.json',{'reason':'SIGNAL_OR_UNKNOWN_RETURN','rc':precheck_rc,'cleanup':False})
   return 1
  if ready:
   after_ok=read_targets('after')
  else:
   after_ok=False
   save('AFTER_SKIPPED.json',{'reason':'BEFORE_READ_FAILED_PRECHECK_NOT_INVOKED','retry':False})
  after_source=source_state();save('SOURCE_AFTER.json',after_source)
  assert before_source==after_source
  assert sha((WORK/'runtime-vars.json').read_bytes())==RUNTIME_SHA
  paths={cli:shutil.which(cli,path='/usr/bin:/bin') for cli in ['ansible','ansible-playbook','ansible-inventory','ansible-config']}
  assert all(path=='/usr/bin/'+cli for cli,path in paths.items())
  save('RETURN_PATHS.json',{'paths':paths,'cli_executed':False,'versions_reused_from':'2026-10-18 19:27 exact CLI4 return evidence','global_path_changed':False,'engine_variables_child_only':True})
  stage='LOCAL_CLEANUP';cleanup_owned(identity)
  summary={'at_kst':now(),'status':'RETURNED_REQUIRES_EVIDENCE_REVIEW','precheck_rc':precheck_rc,'before6_match':ready,'after6_match':after_ok,'source_unchanged':True,'runtime_vars_unchanged':True,'owned_temp_cleanup':True,'remote_temp_absence_claimed':False,'explicit_cli_tests':0,'wrapper_mandatory_cli_preserved':True,'full_ntp_ac_accepted':False}
  save('RESULT.json',summary);print(json.dumps(summary),flush=True)
  return 0 if ready and precheck_rc==0 and after_ok else 1
 except BaseException as error:
  # A failure/interruption does not prove descendants are gone. No auto cleanup.
  try:save('HOLD.json',{'at_kst':now(),'stage':stage,'error_type':type(error).__name__,'cleanup':False,'retry':False})
  except BaseException:pass
  raise
if __name__=='__main__':raise SystemExit(main())
