CFG={'plan': {'prepared_at_kst': '2026-10-13T02:45:23.159426+09:00', 'session_id': 'w02-20261013T024523-85942d67', 'source_sha': '0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea', 'source_root': '/home/server01_ansible/worker02-session-plan-3hetha3t/source', 'engine': '/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin', 'engine_version': '2.21.3', 'host': 'k8s-worker02', 'endpoint': '10.1.93.107', 'interface': 'ens160', 'connection': 'fds-k8s-worker02', 'boot': 'f0015ee5-36c9-4184-a985-723170958f2c', 'dns': ['10.1.93.52', '10.1.93.53'], 'search': ['fds.internal'], 'ignore_auto_dns': True, 'controller_evidence_root': '/home/server01_ansible/p1-worker02-dns-20261013-r1', 'remote_backup': '/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions/w02-20261013T024523-85942d67/original-resolver.json', 'snapshot_sha256': None, 'actions': ['prepare', 'apply-check', 'apply', 'reapply', 'rollback-check', 'rollback', 'fresh-read'], 'runtime_started': False, 'nm_writer_exclusion_confirmed': False, 'console_confirmed_for_dns_round': False, 'new_lead_implementation_go_required': False, 'per_step_timeout_seconds': 180, 'first_apply_max_snapshot_age_seconds': 900, 'maximum_session_minutes': 15, 'artificial_drift': False, 'global_engine_switch': False, 'ac_accepted': False}, 'hashes': {'ansible.cfg': '73e6f6b5844a7a2dee8cf042b67a1c7b61c3e4b4198f4f7f7b65907e883de90e', 'inventory/hosts.yml': '15daf8f9257473772f8ecd7cfaf08369c88fd5c3775cb3bf67fcd95a1122ec0a', 'inventory/group_vars/all.yml': '4c079bd5dc95a94e640752cce05f27d778c93f3e3eb7929fcc450714f2a15648', 'scripts/cr-p1-ans-01-01-run.sh': '60b5a0a2a4815c5a9afc07885a2352158a18239cba475bd8715b3c8835f33f98', 'scripts/lib/ansible-engine.sh': 'aedf6cd8d2fa656784e5f93e4d507582efb39755655d2e2ad0696e6353f316dd', 'playbooks/cr-p1-ans-01-01-worker02-session.yml': '2885e052ea9deef95c98888bed48e9bd59f0243d7faeba2e5dd4363cb769b869', 'library/fds_dns_session.py': 'cda8c8f12ba7d960db0df0fd455bae4dd652171ed64aeb31a3ef11e9a351a07d', 'roles/dns_resolver/tasks/main.yml': '2a45bc2d3738d20dfb36aef62d37a38c50de6b5b2dba8b60bab5adecc5e8cb14', 'roles/dns_resolver/tasks/verify.yml': 'a75b7967edc543275ab69cd013bfdc6f89d72f42abe36d5a1e2f7f27f149eb61', 'roles/dns_resolver/tasks/session-bind.yml': '8b71d1688534a3252d0d78771ef58b498c7d407ea87efca99d11915430cf1905', 'roles/dns_resolver/tasks/session-rollback.yml': '9c9ce15d810645bc904bcb79da31b8a11fbf7a26c6470d4dd53518c05e23f4f4'}, 'authorization': {'user': '이권욱', 'recorded_at_kst': '2026-10-13T02:51:57.591887+09:00', 'reply_timestamp_not_inferred': True, 'question_id': 'call_HEqmiWd1bHIJpxxOtzgIdIby', 'answer': '가능 — 해당 단일 회차 진행', 'scope_sha256': '4856f065e7658ca77b4887a3d9b6fd219ed0f50dbb0d8b56f18c036dfecdc829', 'input_sha256': 'e96e80dbe23f3d91fccd29a4bf2b8246431812462f7c2fa4d2e56e8ca07c3246', 'single_session_authorized': True, 'nm_writer_exclusion_confirmed': True, 'worker02_console_confirmed': True, 'artificial_drift': False, 'global_engine_switch': False, 'ac_accepted': False}, 'step': 'rollback-check', 'action': 'rollback', 'check': True, 'backup_sha': 'ce6295bcc88b8129003f50cb4cbd4be36d18c32413bbcf46e9926a552a1ea5b2'}

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
  evidence.mkdir(mode=0o700);write_new(evidence/'USER_AUTHORIZATION.json',(json.dumps(CFG['authorization'],ensure_ascii=False,indent=2)+'\n').encode());write_new(evidence/'EXECUTION_INPUT.json',(json.dumps(plan,indent=2)+'\n').encode())
 else:
  assert evidence.is_dir() and not evidence.is_symlink() and stat.S_IMODE(evidence.stat().st_mode)==0o700 and evidence.stat().st_uid==1000
  old=json.loads((evidence/'EXECUTION_INPUT.json').read_bytes());assert old==plan
  pin=json.loads((evidence/'PINNED_BACKUP.json').read_bytes());assert pin['sha256']==CFG['backup_sha'] and pin['session_id']==plan['session_id']
 argv=['/usr/bin/bash','scripts/cr-p1-ans-01-01-run.sh','worker02-session',CFG['action'],plan['session_id']]+([CFG['backup_sha']] if CFG['backup_sha'] else [])
 env=dict(os.environ,LC_ALL='C.UTF-8',LANG='C.UTF-8',PYTHONDONTWRITEBYTECODE='1',ANSIBLE_FORCE_COLOR='0',FDS_ANSIBLE_ENGINE_DIR=plan['engine'],FDS_ANSIBLE_ENGINE_VERSION=plan['engine_version'],ANSIBLE_PRIVATE_KEY_FILE='/home/server01_ansible/.ssh/p1_ansible_ed25519',CR_CHANGE_APPROVED='CR-P1-ANS-01-01',CR_DNS_SOURCE_SHA=plan['source_sha'],CR_EVIDENCE_DIR=str(evidence/'logs'),CR_DNS_SESSION_APPROVED=plan['session_id']+':'+CFG['action'],CR_DNS_CHECK_ONLY='1' if CFG['check'] else '0')
 out['argv']=argv;out['selected_env']={k:env[k] for k in ['LC_ALL','LANG','FDS_ANSIBLE_ENGINE_DIR','FDS_ANSIBLE_ENGINE_VERSION','CR_CHANGE_APPROVED','CR_DNS_SOURCE_SHA','CR_EVIDENCE_DIR','CR_DNS_SESSION_APPROVED','CR_DNS_CHECK_ONLY']}
 write_new(evidence/(step+'.start.json'),(json.dumps({'argv':argv,'started_at_utc':now(),'check':CFG['check']},indent=2)+'\n').encode())
 p=subprocess.Popen(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);out['pid']=p.pid
 try:stdout,stderr=p.communicate(timeout=180);out['rc']=p.returncode
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGTERM)
  try:stdout,stderr=p.communicate(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);stdout,stderr=p.communicate()
  out.update(rc=None,error='TIMEOUT_REMOTE_EFFECT_UNKNOWN_NO_RETRY')
 write_new(evidence/(step+'.stdout.txt'),stdout);write_new(evidence/(step+'.stderr.txt'),stderr)
 out.update(stdout=stdout.decode(errors='replace'),stderr=stderr.decode(errors='replace'),stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),finished_at_utc=now())
 write_new(evidence/(step+'.result.json'),(json.dumps({k:v for k,v in out.items() if k not in ['stdout','stderr']},indent=2)+'\n').encode())
 assert out['rc']==0,'WRAPPER_FAILED'
 out['status']='WRAPPER_RC0_REVIEW_REQUIRED'
except Exception as e:out.update(status='STOP_NO_RETRY',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='WRAPPER_RC0_REVIEW_REQUIRED' else 2)
