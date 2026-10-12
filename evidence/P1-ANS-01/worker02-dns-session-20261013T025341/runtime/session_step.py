"""Run exactly one approved existing wrapper action, save original output, no retry."""
from pathlib import Path
import datetime as dt,hashlib,json,re,sys
from controller_transport import run
R=Path(__file__).resolve().parent;P=R.parent
step=sys.argv[1];steps=['prepare','apply-check','apply','reapply','rollback-check','rollback'];assert step in steps
plan=json.loads((P/'EXECUTION_INPUT.json').read_bytes());binding=json.loads((P/'SOURCE_BINDING.json').read_bytes());auth=json.loads((R/'USER_AUTHORIZATION.json').read_bytes())
assert auth['single_session_authorized'] and auth['nm_writer_exclusion_confirmed'] and auth['worker02_console_confirmed']
index=steps.index(step)
for previous in steps[:index]:assert json.loads((R/(previous+'-VERIFIED.json')).read_bytes())['status']=='VERIFIED'
if step!='prepare':
 pinned=json.loads((R/'PINNED_BACKUP.json').read_bytes());backup_sha=pinned['sha256']
 assert re.fullmatch('[0-9a-f]{64}',backup_sha)
 start=dt.datetime.fromisoformat(json.loads((R/'prepare/stdout.json').read_bytes())['started_at_utc'])
 assert (dt.datetime.now(dt.timezone.utc)-start).total_seconds()<900,'SESSION_TIME_BUDGET'
else:backup_sha=''
cfg={'plan':plan,'hashes':binding['hashes'],'authorization':auth,'step':step,'action':step.split('-')[0],'check':step.endswith('-check'),'backup_sha':backup_sha}
source='CFG='+repr(cfg)+'\n'+'''
import datetime,hashlib,json,os,pathlib,signal,socket,stat,subprocess,time
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
plan=CFG['plan'];root=pathlib.Path(plan['source_root']);evidence=pathlib.Path(plan['controller_evidence_root']);step=CFG['step']
out={'host':socket.gethostname(),'started_at_utc':now(),'step':step,'source':plan['source_sha'],'commands':[]}
def write_new(p,b):
 fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def checked(argv):
 p=subprocess.run(argv,cwd=root,capture_output=True,timeout=10,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
 out['commands'].append({'argv':argv,'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()});assert p.returncode==0;return p.stdout
try:
 assert socket.gethostname()=='ansible01' and os.geteuid()==1000
 assert checked(['git','rev-parse','HEAD']).decode().strip()==plan['source_sha']
 assert not checked(['git','status','--porcelain','--untracked-files=no']).strip()
 for name,h in CFG['hashes'].items():assert sha((root/name).read_bytes())==h,'SOURCE_DRIFT:'+name
 assert not [k for k in os.environ if k.startswith('ANSIBLE_')],'UNEXPECTED_ANSIBLE_ENV'
 os.umask(0o077)
 if step=='prepare':
  evidence.mkdir(mode=0o700);write_new(evidence/'USER_AUTHORIZATION.json',(json.dumps(CFG['authorization'],ensure_ascii=False,indent=2)+'\\n').encode());write_new(evidence/'EXECUTION_INPUT.json',(json.dumps(plan,indent=2)+'\\n').encode())
 else:
  assert evidence.is_dir() and not evidence.is_symlink() and stat.S_IMODE(evidence.stat().st_mode)==0o700 and evidence.stat().st_uid==1000
  old=json.loads((evidence/'EXECUTION_INPUT.json').read_bytes());assert old==plan
  pin=json.loads((evidence/'PINNED_BACKUP.json').read_bytes());assert pin['sha256']==CFG['backup_sha'] and pin['session_id']==plan['session_id']
 argv=['/usr/bin/bash','scripts/cr-p1-ans-01-01-run.sh','worker02-session',CFG['action'],plan['session_id']]+([CFG['backup_sha']] if CFG['backup_sha'] else [])
 env=dict(os.environ,LC_ALL='C.UTF-8',LANG='C.UTF-8',PYTHONDONTWRITEBYTECODE='1',ANSIBLE_FORCE_COLOR='0',FDS_ANSIBLE_ENGINE_DIR=plan['engine'],FDS_ANSIBLE_ENGINE_VERSION=plan['engine_version'],ANSIBLE_PRIVATE_KEY_FILE='/home/server01_ansible/.ssh/p1_ansible_ed25519',CR_CHANGE_APPROVED='CR-P1-ANS-01-01',CR_DNS_SOURCE_SHA=plan['source_sha'],CR_EVIDENCE_DIR=str(evidence/'logs'),CR_DNS_SESSION_APPROVED=plan['session_id']+':'+CFG['action'],CR_DNS_CHECK_ONLY='1' if CFG['check'] else '0')
 out['argv']=argv;out['selected_env']={k:env[k] for k in ['LC_ALL','LANG','FDS_ANSIBLE_ENGINE_DIR','FDS_ANSIBLE_ENGINE_VERSION','CR_CHANGE_APPROVED','CR_DNS_SOURCE_SHA','CR_EVIDENCE_DIR','CR_DNS_SESSION_APPROVED','CR_DNS_CHECK_ONLY']}
 write_new(evidence/(step+'.start.json'),(json.dumps({'argv':argv,'started_at_utc':now(),'check':CFG['check']},indent=2)+'\\n').encode())
 p=subprocess.Popen(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);out['pid']=p.pid
 try:stdout,stderr=p.communicate(timeout=180);out['rc']=p.returncode
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGTERM)
  try:stdout,stderr=p.communicate(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);stdout,stderr=p.communicate()
  out.update(rc=None,error='TIMEOUT_REMOTE_EFFECT_UNKNOWN_NO_RETRY')
 write_new(evidence/(step+'.stdout.txt'),stdout);write_new(evidence/(step+'.stderr.txt'),stderr)
 out.update(stdout=stdout.decode(errors='replace'),stderr=stderr.decode(errors='replace'),stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),finished_at_utc=now())
 write_new(evidence/(step+'.result.json'),(json.dumps({k:v for k,v in out.items() if k not in ['stdout','stderr']},indent=2)+'\\n').encode())
 assert out['rc']==0,'WRAPPER_FAILED'
 out['status']='WRAPPER_RC0_REVIEW_REQUIRED'
except Exception as e:out.update(status='STOP_NO_RETRY',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='WRAPPER_RC0_REVIEW_REQUIRED' else 2)
'''
# The remote source must contain real newline escapes in JSON file writes.
source=source.replace("+'\\\\n'","+'\\n'")
receipt=run(step,source,timeout=220)
assert receipt['rc']==0,'STEP_FAILED_STOP'
d=json.loads((R/step/'stdout.json').read_bytes());assert d['status']=='WRAPPER_RC0_REVIEW_REQUIRED' and d['rc']==0
stdout=d['stdout'];(R/step/'ansible.stdout.txt').write_bytes(stdout.encode());(R/step/'ansible.stderr.txt').write_bytes(d['stderr'].encode())
pattern=r'^([A-Za-z0-9_.-]+)\s+:\s+ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)\s+skipped=(\d+)\s+rescued=(\d+)\s+ignored=(\d+)\s*$'
recaps={m[0]:dict(zip(['ok','changed','unreachable','failed','skipped','rescued','ignored'],map(int,m[1:]))) for m in re.findall(pattern,stdout,re.M)}
assert set(recaps)=={'localhost','k8s-worker02'},'RECAP_TARGETS'
assert all(x[k]==0 for x in recaps.values() for k in ['failed','unreachable','rescued','ignored']),'RECAP_FAILURE'
expected={'prepare':1,'apply-check':0,'apply':0,'reapply':0,'rollback-check':0,'rollback':2}[step]
assert recaps['k8s-worker02']['changed']==expected and recaps['localhost']['changed']==0,'UNEXPECTED_CHANGED'
records=[];decoder=json.JSONDecoder()
for m in re.finditer(r'\{',stdout):
 try:obj,_=decoder.raw_decode(stdout[m.start():])
 except ValueError:continue
 if isinstance(obj,dict) and isinstance(obj.get('msg'),dict) and obj['msg'].get('session_id')==plan['session_id'] and 'snapshot_written' in obj['msg']:records.append(obj['msg'])
assert len(records)==1,'SESSION_RECEIPT_COUNT';s=records[0];assert s['source_sha']==plan['source_sha'] and s['path']==plan['remote_backup']
if step=='prepare':assert s['snapshot_written'] is True and re.fullmatch('[0-9a-f]{64}',s['sha256'])
else:assert s['snapshot_written'] is False and s['sha256']==backup_sha
ver={'status':'VERIFIED','step':step,'recap':recaps,'session_receipt':s,'stdout_sha256':d['stdout_sha256'],'runtime_changed_count':expected,'same_values_restore_not_failure_recovery':step=='rollback'}
(R/(step+'-VERIFIED.json')).write_bytes((json.dumps(ver,indent=2)+'\n').encode())
print(json.dumps(ver))
