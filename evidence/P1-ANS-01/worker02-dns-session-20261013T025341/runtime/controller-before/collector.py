EXPECTED={'ansible.cfg': '73e6f6b5844a7a2dee8cf042b67a1c7b61c3e4b4198f4f7f7b65907e883de90e', 'inventory/hosts.yml': '15daf8f9257473772f8ecd7cfaf08369c88fd5c3775cb3bf67fcd95a1122ec0a', 'inventory/group_vars/all.yml': '4c079bd5dc95a94e640752cce05f27d778c93f3e3eb7929fcc450714f2a15648', 'scripts/cr-p1-ans-01-01-run.sh': '60b5a0a2a4815c5a9afc07885a2352158a18239cba475bd8715b3c8835f33f98', 'scripts/lib/ansible-engine.sh': 'aedf6cd8d2fa656784e5f93e4d507582efb39755655d2e2ad0696e6353f316dd', 'playbooks/cr-p1-ans-01-01-worker02-session.yml': '2885e052ea9deef95c98888bed48e9bd59f0243d7faeba2e5dd4363cb769b869', 'library/fds_dns_session.py': 'cda8c8f12ba7d960db0df0fd455bae4dd652171ed64aeb31a3ef11e9a351a07d', 'roles/dns_resolver/tasks/main.yml': '2a45bc2d3738d20dfb36aef62d37a38c50de6b5b2dba8b60bab5adecc5e8cb14', 'roles/dns_resolver/tasks/verify.yml': 'a75b7967edc543275ab69cd013bfdc6f89d72f42abe36d5a1e2f7f27f149eb61', 'roles/dns_resolver/tasks/session-bind.yml': '8b71d1688534a3252d0d78771ef58b498c7d407ea87efca99d11915430cf1905', 'roles/dns_resolver/tasks/session-rollback.yml': '9c9ce15d810645bc904bcb79da31b8a11fbf7a26c6470d4dd53518c05e23f4f4'}
import datetime,hashlib,json,os,pathlib,socket,subprocess
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
