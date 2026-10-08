import base64,datetime,fcntl,hashlib,json,os,pathlib,shlex,subprocess,sys,tempfile
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
home=pathlib.Path.home()
repo=home/'p1-sec-b2-runtime-20261001T115520'
head='c0d784fa9a1d9dfc57f504ed969c036d0860acef'
collector=repo/'playbooks/p1-sec-01-b2-collect-58.yml'
lock=open(home/'.sec19-p4-collection.lock','a')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
task=pathlib.Path(tempfile.mkdtemp(prefix='sec19-edge-p4.',dir=home))
os.chmod(task,0o700)
print('TASK_DIR='+str(task),flush=True)
def record(name,args,timeout=25):
    p=subprocess.run(args,capture_output=True,timeout=timeout)
    (task/(name+'.stdout')).write_bytes(p.stdout);(task/(name+'.stderr')).write_bytes(p.stderr)
    (task/(name+'.rc')).write_text(str(p.returncode)+'\n')
    return p
def remote(ip,command):
    return ['ssh','-i',str(home/'.ssh/p1_ansible_ed25519'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@'+ip,command]
started=now();(task/'started-utc.txt').write_text(started+'\n')
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,7,18,10,tzinfo=datetime.timezone.utc),'window expired'
assert record('source-head',['git','-C',str(repo),'rev-parse','HEAD']).stdout.decode().strip()==head
assert not record('source-status',['git','-C',str(repo),'status','--porcelain']).stdout.strip()
assert hashlib.sha256(collector.read_bytes()).hexdigest()=='42fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024'
(task/'collector.yml').write_bytes(collector.read_bytes())
for rel in ['ansible.cfg','inventory/hosts.yml','inventory/group_vars/all.yml']:
    (task/rel.replace('/','__')).write_bytes((repo/rel).read_bytes())
record('ansible-version',['ansible-playbook','--version'])
probe='''import pathlib,json,os
out=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit(): continue
 try: args=(p/'cmdline').read_bytes().split(b'\\0'); names=[pathlib.Path(x.decode(errors='replace')).name for x in args if x]
 except (OSError,ValueError): continue
 if any(x in names for x in ['tcpdump','ansible-playbook','backup.sh','probe.sh','edge01-cutover.sh']): out.append({'pid':int(p.name),'programs':[x for x in names if x in ['tcpdump','ansible-playbook','backup.sh','probe.sh','edge01-cutover.sh']]})
print(json.dumps(out))
'''
p=record('controller-processes',['python3','-c',probe]);assert p.returncode==0 and json.loads(p.stdout)==[]
for suffix in ('102','105','107','108'):
    p=record('processes-'+suffix,remote('10.1.93.'+suffix,'sudo -n python3 -c '+shlex.quote(probe)))
    assert p.returncode==0 and json.loads(p.stdout)==[], 'conflicting process '+suffix
state='''import subprocess,json
k=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s']
n=json.loads(subprocess.check_output(k+['get','nodes','-o','json']))['items']
assert len(n)==6 and all(any(c['type']=='Ready' and c['status']=='True' for c in x['status']['conditions']) for x in n)
pods=json.loads(subprocess.check_output(k+['-n','fds-app','get','pods','-o','json']))['items']
eps=json.loads(subprocess.check_output(k+['-n','fds-app','get','endpointslices','-l','kubernetes.io/service-name=transaction-api-nodeport','-o','json']))['items']
result={'nodes':[{'name':x['metadata']['name'],'ready':True} for x in n],
'pods':[{'name':x['metadata']['name'],'uid':x['metadata']['uid'],'node':x['spec'].get('nodeName'),'phase':x['status'].get('phase'),'ready':next((c['status'] for c in x['status'].get('conditions',[]) if c['type']=='Ready'),None),'restarts':[c.get('restartCount') for c in x['status'].get('containerStatuses',[])]} for x in pods],
'endpoints':sorted([{'node':e['nodeName'],'addresses':e['addresses'],'conditions':e['conditions'],'uid':e.get('targetRef',{}).get('uid')} for s in eps for e in s['endpoints']],key=lambda x:x['node'])}
assert len(result['endpoints'])==3 and {e['node'] for e in result['endpoints']}=={'k8s-worker01','k8s-worker02','k8s-worker03'}
assert all(e['conditions'].get('ready') and not e['conditions'].get('terminating',False) for e in result['endpoints'])
assert all(p['ready']=='True' for p in result['pods'])
print(json.dumps(result,sort_keys=True))
'''
p=record('state-before',remote('10.1.93.102','sudo -n python3 -c '+shlex.quote(state)));assert p.returncode==0
# Preserve the one hard-coded previous temporary output before the approved collector replaces it.
preserve="import pathlib,base64,json,hashlib; p=pathlib.Path('/tmp/00_cluster-state.txt'); b=p.read_bytes() if p.is_file() else None; print(json.dumps({'path':str(p),'exists':b is not None,'sha256':hashlib.sha256(b).hexdigest() if b is not None else None,'base64':base64.b64encode(b).decode() if b is not None else None}))"
p=record('prior-control-temp',remote('10.1.93.102','sudo -n python3 -c '+shlex.quote(preserve)));assert p.returncode==0
tag=task.name
extra={'out_root':str(task/'raw'),'out':"{{ out_root }}/{{ hostvars[control_host].run_id }}",
       'td_file':'/tmp/'+tag+'-tcpdump_{{ inventory_hostname }}.txt','curl_file':'/tmp/'+tag+'-curl_{{ inventory_hostname }}.txt'}
(task/'extra-vars.json').write_text(json.dumps(extra,indent=2)+'\n')
cmd=['ansible-playbook','-i',str(repo/'inventory/hosts.yml'),str(collector),'--private-key',str(home/'.ssh/p1_ansible_ed25519'),'-e','@'+str(task/'extra-vars.json')]
(task/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
env=os.environ.copy();env['ANSIBLE_CONFIG']=str(repo/'ansible.cfg');env['ANSIBLE_NOCOLOR']='1'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,7,18,10,tzinfo=datetime.timezone.utc),'latest start expired'
(task/'runtime-started-utc.txt').write_text(now()+'\n')
with (task/'runtime.stdout').open('wb') as out,(task/'runtime.stderr').open('wb') as err:
    try:
        p=subprocess.run(cmd,cwd=repo,env=env,stdout=out,stderr=err,timeout=540)
        runtime_rc=p.returncode
    except subprocess.TimeoutExpired:
        runtime_rc=124
        err.write(b'controller timeout; no automatic retry; capture absence must be checked\n')
(task/'runtime.rc').write_text(str(runtime_rc)+'\n')
(task/'runtime-finished-utc.txt').write_text(now()+'\n')
post=record('state-after',remote('10.1.93.102','sudo -n python3 -c '+shlex.quote(state)))
cleanup=[]
for suffix in ('105','107','108'):
    q=record('processes-after-'+suffix,remote('10.1.93.'+suffix,'sudo -n python3 -c '+shlex.quote(probe)))
    cleanup.append(q.returncode==0 and json.loads(q.stdout)==[])
report={'runtime_rc':runtime_rc,'post_rc':post.returncode,'baseline_equal':post.returncode==0 and (task/'state-before.stdout').read_bytes()==post.stdout,'captures_absent':all(cleanup),'source_head':head,'finished_utc':now()}
(task/'result.json').write_text(json.dumps(report,indent=2)+'\n')
files=sorted(p for p in task.rglob('*') if p.is_file())
(task/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(task).as_posix()+'\n' for p in files))
print(json.dumps(report),flush=True)
print('TASK_DIR='+str(task),flush=True)
sys.exit(0 if runtime_rc==0 and post.returncode==0 and report['baseline_equal'] and report['captures_absent'] else 2)
