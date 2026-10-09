import datetime,json,os,pathlib,shlex,stat,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent
M=json.loads((HERE/'session.json').read_text())
KEY='/home/server01_ansible/.ssh/p1_ansible_ed25519'
SSH=['ssh','-i',KEY,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes']
REPO='321Team/infra-ansible'
HEAD=M['head']
def call(argv,**kw):
 r=subprocess.run(argv,capture_output=True,timeout=60,**kw)
 if r.returncode:raise RuntimeError('COMMAND_FAILED')
 return r.stdout

def remote(cmd,user='server01_cicd-runner',data=None):
 return call(SSH+[user+'@10.250.10.20',cmd],input=data)

def api(path):return json.loads(call(['gh','api','repos/'+REPO+'/'+path]))
def fresh():
 pr=api('pulls/77')
 assert pr['head']['sha']==HEAD and pr['state']=='open'
 reviews=api('pulls/77/reviews')
 reviewer=[r for r in reviews if r['user']['login']=='hayeounglee' and r['state'] in {'APPROVED','CHANGES_REQUESTED','DISMISSED'}]
 assert reviewer and reviewer[-1]['state']=='APPROVED' and reviewer[-1]['commit_id']==HEAD
 job=api('actions/jobs/'+str(M['job']))
 assert job['head_sha']==HEAD and job['status']=='queued' and job['runner_id']==0
 assert set(job['labels'])=={'self-hosted','Linux','X64','fds-ci','ansible-isolated'}
 assert api('actions/runners')['total_count']==0
 assert api('actions/runs?status=in_progress')['total_count']==0
 active=[x for x in api('actions/runs?per_page=100')['workflow_runs'] if x['status'] in {'queued','pending','in_progress','waiting','requested'}]
 assert len(active)==1 and active[0]['id']==M['run']
 assert datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(M['not_before_kst'])
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(M['not_after_kst'])
 other=json.loads(call(['gh','api','repos/321Team/infra-cicd/actions/runs?status=in_progress']))
 assert other['total_count']==0
 containers=json.loads(remote('cd /tmp && sudo -n -u ansible-verify env HOME=/home/ansible-verify XDG_RUNTIME_DIR=/run/user/1001 podman ps -a --format json','svc_ansible'))
 assert containers==[]
 process=remote('cd /tmp; if sudo -n pgrep -u 1001 -f runner.py >/dev/null; then echo PRESENT; else echo ABSENT; fi','svc_ansible').strip()
 assert process==b'ABSENT'
 remote('test ! -e '+shlex.quote(M['task']+'/operator.rc')+' && test ! -e '+shlex.quote(M['task']+'/operator-ended.txt'))
 held=remote('if flock -n /home/server01_cicd-runner/ansible-ci-job-113754076550.lock -c true; then echo FREE; else echo HELD; fi').strip()
 assert held==b'HELD'
 ready=remote('cat '+shlex.quote(M['task']+'/auth-ready.txt')).decode().strip()
 age=time.time()-datetime.datetime.fromisoformat(ready).timestamp()
 assert 0<=age<=150
 return {'job':M['job'],'run':M['run'],'head':HEAD,'status':'queued','registered_runners':0,'running_containers':0,'observed_at_unix':time.time()}

def main():
 os.umask(0o077)
 fresh()
 kit=pathlib.Path('/home/server01_ansible/ansible-ipc-admin.9LFS6d7N/FDS_Ansible_Actions_Runner_v1_3')
 import hashlib
 assert hashlib.sha256((kit/'SHA256SUMS').read_bytes()).hexdigest()=='e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6'
 call(['sha256sum','-c','SHA256SUMS'],cwd=kit)
 remote('test ! -e '+shlex.quote(M['packet'])+' && test ! -e '+shlex.quote(M['packet']+'.incoming'))
 packet=None
 try:
  issued=call(['python3','-I','-B',str(kit/'admin-token.py')]).decode()
  values=[x.removeprefix('TOKEN_PACKET=') for x in issued.splitlines() if x.startswith('TOKEN_PACKET=')]
  assert len(values)==1
  packet=pathlib.Path(values[0]);s=packet.lstat()
  assert packet.parent==pathlib.Path.home() and stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  call(['scp','-q','-i',KEY,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',str(packet),'server01_cicd-runner@10.250.10.20:'+M['packet']+'.incoming'])
  remote('chmod 600 '+shlex.quote(M['packet']+'.incoming')+' && mv -T '+shlex.quote(M['packet']+'.incoming')+' '+shlex.quote(M['packet']))
  packet.unlink()
  preflight=fresh()
  raw=(json.dumps(preflight)+'\n').encode()
  (HERE/'preflight.json').write_bytes(raw)
  remote('umask 077; cat > '+shlex.quote(M['task']+'/preflight.json.incoming')+' && mv -T '+shlex.quote(M['task']+'/preflight.json.incoming')+' '+shlex.quote(M['task']+'/preflight.json'),data=raw)
  result={'status':'TOKEN_PRIVATELY_TRANSFERRED_PREFLIGHT_RELEASED','admin_packet_deleted':True,'released_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run':M['run'],'job':M['job'],'head':HEAD}
  (HERE/'release-result.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result))
 finally:
  if packet and packet.exists():
   s=packet.lstat()
   if stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1:packet.unlink()
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  print('STOP_'+type(exc).__name__)
  raise SystemExit(1)
