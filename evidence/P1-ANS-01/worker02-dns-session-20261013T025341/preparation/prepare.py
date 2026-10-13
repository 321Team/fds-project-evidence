"""Fresh read-only preparation; no session backup or DNS write."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
OLD=P.parent/'p1-independent-work-20261012'
if not (P/'read_transport.py').exists():shutil.copyfile(OLD/'read_transport.py',P/'read_transport.py')
from read_transport import run
kind=sys.argv[1]
REPO=P.parent/'p1-preapply-until-0930-20261012/other-work/checkouts/infra-ansible'
HEAD='0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea'
files=['ansible.cfg','inventory/hosts.yml','inventory/group_vars/all.yml','scripts/cr-p1-ans-01-01-run.sh','scripts/lib/ansible-engine.sh','playbooks/cr-p1-ans-01-01-worker02-session.yml','library/fds_dns_session.py']
files+=['roles/dns_resolver/tasks/'+n for n in ['main.yml','verify.yml','session-bind.yml','session-rollback.yml']]
sources=P/'approved-source';sources.mkdir(exist_ok=True);hashes={}
for name in files:
 p=subprocess.run(['git','-C',str(REPO),'show',HEAD+':'+name],capture_output=True,check=True);dest=sources/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==p.stdout
 else:dest.write_bytes(p.stdout)
 hashes[name]=hashlib.sha256(p.stdout).hexdigest()
(P/'SOURCE_BINDING.json').write_bytes((json.dumps({'head':HEAD,'hashes':hashes,'review_pr':76},indent=2)+'\n').encode())
if kind=='worker':
 source=(OLD/'ansible-worker02/collector.py').read_text()
 source=source.replace("out['interface']=interface",'''out['boot']=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
out['addresses']=cmd(['ip','-j','-4','address','show',interface])
for args in [['getent','ahostsv4','k8s-api.fds.internal'],['getent','ahostsv4','k8s-api'],['getent','ahostsv4','github.com'],['dig','+time=2','+tries=1','+short','@10.1.93.52','k8s-api.fds.internal','A'],['dig','+time=2','+tries=1','+short','@10.1.93.53','k8s-api.fds.internal','A']]:out['commands'].append(cmd(args))
import socket,stat,hashlib
with socket.create_connection(('10.1.93.109',6443),timeout=3):out['api_tcp_6443']=True
out['state_paths']=[]
for name in ['/var/lib/fds-change','/var/lib/fds-change/CR-P1-ANS-01-01','/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions']:
 p=pathlib.Path(name)
 if os.path.lexists(p):
  s=p.lstat();out['state_paths'].append({'path':name,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'symlink':p.is_symlink(),'xattrs':os.listxattr(p,follow_symlinks=False)})
 else:out['state_paths'].append({'path':name,'exists':False})
out['interface']=interface''')
 r=run('worker02-fresh-read','10.1.93.107',source,timeout=90);raise SystemExit(0 if r['rc']==0 else 2)
elif kind=='controller':
 source='EXPECTED='+repr(hashes)+'\n'+'''import datetime,hashlib,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='ansible01' and os.geteuid()==1000
root=pathlib.Path('/home/server01_ansible/worker02-session-plan-3hetha3t/source');engine=pathlib.Path('/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin')
env=dict(os.environ,LC_ALL='C.UTF-8',LANG='C.UTF-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'root':str(root),'engine':str(engine),'commands':[],'files':[],'scope':'read only; no playbook, session backup, engine switch or DNS write'}
def cmd(args,keep=True):
 p=subprocess.run(args,cwd=root,env=env,capture_output=True,timeout=20);row={'argv':args,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()};out['commands'].append(row)
 if keep:row['stdout']=p.stdout.decode()
 assert p.returncode==0;return p.stdout
try:
 assert cmd(['git','rev-parse','HEAD']).decode().strip()=='0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea'
 assert not cmd(['git','status','--porcelain','--untracked-files=no']).strip()
 assert not cmd(['git','ls-files','--others','--exclude-standard','--','library','module_utils','roles','playbooks','scripts','inventory','ansible.cfg']).strip()
 for name,h in EXPECTED.items():
  p=root/name;s=p.lstat();b=p.read_bytes();assert not p.is_symlink() and hashlib.sha256(b).hexdigest()==h
  out['files'].append({'path':name,'sha256':h,'size':len(b),'uid':s.st_uid,'mode':oct(s.st_mode&0o7777)})
 for cli in ['ansible','ansible-playbook','ansible-inventory','ansible-config']:
  assert cmd([str(engine/cli),'--version']).decode().splitlines()[0]==cli+' [core 2.21.3]'
 inv=json.loads(cmd([str(engine/'ansible-inventory'),'-i','inventory/hosts.yml','--list'],keep=False));hv=inv['_meta']['hostvars']['k8s-worker02']
 out['inventory_selected']={k:hv.get(k) for k in ['ansible_host','ansible_user','ansible_become','ansible_python_interpreter','cr_dns_servers','cr_dns_search_domains','cr_dns_internal_name','cr_dns_short_name','cr_dns_expected_address','cr_dns_external_name']}
 assert hv['ansible_host']=='10.1.93.107' and hv['ansible_user']=='svc_ansible' and hv['cr_dns_servers']==['10.1.93.52','10.1.93.53'] and hv['cr_dns_search_domains']==['fds.internal']
 out['inventory_groups']={k:inv[k] for k in ['k8s_workers','k8s_nodes']}
 out['inherited_ansible_env_names']=[k for k in os.environ if k.startswith('ANSIBLE_')];assert not out['inherited_ansible_env_names'],'UNEXPECTED_ANSIBLE_ENV'
 out['status']='PRECHECK_VERIFIED'
except Exception as e:out.update(status='STOP',error=type(e).__name__+':'+str(e))
print(json.dumps(out));raise SystemExit(0 if out['status']=='PRECHECK_VERIFIED' else 2)
'''
 # Direct controller SSH; no second hop or sudo.
 import datetime as dt
 folder=P/'controller-fresh-read';folder.mkdir(exist_ok=False);raw=source.encode();(folder/'collector.py').write_bytes(raw)
 cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-']
 receipt={'started_at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'command':cmd,'source_sha256':hashlib.sha256(raw).hexdigest()}
 p=subprocess.run(cmd,input=raw,capture_output=True,timeout=115);(folder/'stdout.json').write_bytes(p.stdout);(folder/'stderr.txt').write_bytes(p.stderr)
 receipt.update(rc=p.returncode,finished_at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest());(folder/'receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
 print(json.dumps({'step':'controller-fresh-read','rc':p.returncode,'bytes':len(p.stdout)}));raise SystemExit(p.returncode)
else:raise SystemExit('invalid step')
