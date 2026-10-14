"""Scoped read-only Phase 1 collection. Remote source uses stdin; no remote files.
No HTTP transaction, exec, Secret, reload, reboot, mutation, or automatic retry.
"""
import argparse, datetime as dt, hashlib, json, pathlib, shlex, subprocess, textwrap

ROOT = pathlib.Path(__file__).resolve().parent
SSH = ['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes', 'fds-ansible01']
HOSTS = {'edge01':'10.1.93.50', 'k8s-control01':'10.1.93.102', 'k8s-control02':'10.1.93.103', 'k8s-control03':'10.1.93.104', 'k8s-worker01':'10.1.93.105', 'k8s-worker02':'10.1.93.107', 'k8s-worker03':'10.1.93.108'}
COMMON = r'''
import datetime as dt, glob, hashlib, json, os, pathlib, pwd, re, socket, subprocess
now=lambda: dt.datetime.now(dt.timezone.utc).isoformat()
out={'started_at_utc':now(),'host':socket.gethostname().split('.')[0],'uid':os.geteuid(),'scope':MODE,'commands':[],'status':'STARTED'}
def run(argv, allowed=(0,)):
 p=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=18)
 if len(p.stdout)>8*1024*1024: raise RuntimeError('OUTPUT_LIMIT')
 out['commands'].append({'argv':argv,'rc':p.returncode,'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_bytes':len(p.stderr),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'at_utc':now()})
 if p.returncode not in allowed: raise RuntimeError('READ_COMMAND_FAILED: '+argv[0]+' rc='+str(p.returncode))
 return p.stdout.decode('utf-8')
def meta(p, content=False):
 p=pathlib.Path(p)
 if not p.exists(): return {'path':str(p),'exists':False}
 s=p.stat(); d={'path':str(p),'exists':True,'mode':oct(s.st_mode&0o7777),'uid':s.st_uid,'gid':s.st_gid,'size':s.st_size,'mtime_ns':s.st_mtime_ns}
 if content:
  if not p.is_file() or s.st_size>1024*1024: raise RuntimeError('UNEXPECTED_FILE')
  d['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return d
assert out['host']==EXPECTED, 'HOST_MISMATCH'
assert (MODE=='edge' and pwd.getpwuid(os.geteuid()).pw_name=='svc_ansible') or (MODE!='edge' and out['uid']==0), 'ACCOUNT_MISMATCH'
out['boot_id']=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
'''
EDGE = r'''
root=pathlib.Path('/etc/nginx/nginx.conf'); queue=[root]; seen=set(); files=[]
allowed={'user','worker_processes','worker_connections','events','http','include','upstream','server','listen','server_name','location','proxy_pass','proxy_set_header','return','allow','deny','satisfy','auth_request','auth_basic','real_ip_header','set_real_ip_from','real_ip_recursive','limit_except','map','if','rewrite','try_files','root','index'}
while queue:
 p=queue.pop(0)
 if str(p) in seen: continue
 if len(seen)>=80: raise RuntimeError('CONFIG_FILE_LIMIT')
 seen.add(str(p)); raw=p.read_bytes()
 if len(raw)>1024*1024: raise RuntimeError('CONFIG_SIZE_LIMIT')
 lines=raw.decode('utf-8',errors='replace').splitlines(); projected=[]; unknown=[]
 for i,line in enumerate(lines,1):
  s=line.strip()
  if not s or s.startswith('#'): continue
  if s=='}': projected.append({'line':i,'text':s}); continue
  key=s.split()[0]
  if key=='include':
   pattern=s.split(None,1)[1].rstrip(';').strip().strip('"')
   if '$' in pattern: raise RuntimeError('DYNAMIC_INCLUDE')
   if not pattern.startswith('/'): pattern='/etc/nginx/'+pattern
   if not pattern.startswith(('/etc/nginx/','/usr/share/nginx/modules/')): raise RuntimeError('INCLUDE_OUTSIDE_SCOPE')
   matches=sorted(glob.glob(pattern))
   if not matches and not any(c in pattern for c in '*?['): raise RuntimeError('INCLUDE_MISSING')
   queue += [pathlib.Path(x) for x in matches]
  if key in allowed:
   if re.search(r'authorization|password|token|secret|://[^ /;]+@',s,re.I): projected.append({'line':i,'directive':key,'text':'REDACTED_REVIEW_REQUIRED'})
   else: projected.append({'line':i,'text':s})
  else: unknown.append({'line':i,'directive':key})
 files.append({**meta(p,True),'routing_projection':projected,'other_directives':unknown})
out['files']=files
out['nginx_service']=run(['/usr/bin/systemctl','show','nginx.service','--no-pager','-p','LoadState','-p','ActiveState','-p','SubState','-p','MainPID','-p','ExecMainStartTimestamp','-p','ActiveEnterTimestamp','-p','FragmentPath','-p','DropInPaths'])
out['port80_listener']=run(['/usr/sbin/ss','-H','-ltn','sport = :80'])
out['nginx_processes']=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
 try:
  if p.read_text().strip()=='nginx':
   stat=(p.parent/'stat').read_text(); tail=stat[stat.rfind(')')+2:].split()
   out['nginx_processes'].append({'pid':int(p.parent.name),'ppid':int(tail[1]),'start_ticks':int(tail[19])})
 except (FileNotFoundError,ProcessLookupError): pass
out['loaded_configuration_identity']='NOT_PROVEN_BY_DISK_READ'
'''
CONTROL = r'''
K=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s']
def get(*args): return json.loads(run(K+list(args)+['-o','json']))
def metadata(o): return {k:o.get('metadata',{}).get(k) for k in ['name','namespace','uid','resourceVersion','generation','labels']}
out['services']=[{'metadata':metadata(x),'spec':x['spec']} for x in get('-n','fds-app','get','svc','transaction-api','transaction-api-nodeport')['items']]
out['endpoints']=get('-n','fds-app','get','endpointslices','-l','kubernetes.io/service-name=transaction-api-nodeport')['items']
out['endpoints']=[{'metadata':metadata(x),'addressType':x.get('addressType'),'endpoints':x.get('endpoints'),'ports':x.get('ports')} for x in out['endpoints']]
out['deployments']=[]
for x in get('-n','fds-app','get','deployments','transaction-api','fds-engine')['items']:
 out['deployments'].append({'metadata':metadata(x),'replicas':x['spec'].get('replicas'),'containers':[{'name':c['name'],'image':c['image']} for c in x['spec']['template']['spec']['containers']],'status':x.get('status')})
out['pods']=[]
for x in get('-n','fds-app','get','pods')['items']:
 out['pods'].append({'metadata':metadata(x),'node':x['spec'].get('nodeName'),'podIP':x['status'].get('podIP'),'phase':x['status'].get('phase'),'containers':[{'name':c['name'],'image':c.get('image'),'imageID':c.get('imageID'),'ready':c.get('ready'),'restartCount':c.get('restartCount')} for c in x['status'].get('containerStatuses',[])]})
out['policies']={}
for kind in ['globalnetworkpolicies.crd.projectcalico.org','hostendpoints.crd.projectcalico.org','tiers.crd.projectcalico.org']:
 out['policies'][kind]=[{'metadata':metadata(x),'spec':x['spec']} for x in get('get',kind)['items']]
out['policies']['fds-app-networkpolicy']=[{'metadata':metadata(x),'spec':x['spec']} for x in get('-n','fds-app','get','networkpolicies')['items']]
'''
GRAFANA = r'''
K=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s']
def get(*args): return json.loads(run(K+list(args)+['-o','json']))
out['credential_files']=[meta('/etc/kubernetes/admin.conf'),meta('/etc/kubernetes/super-admin.conf')]
d=get('-n','monitoring-api','get','deployment','grafana')
out['grafana']={'uid':d['metadata']['uid'],'resourceVersion':d['metadata']['resourceVersion'],'generation':d['metadata'].get('generation'),'status':d.get('status'),'serviceAccount':d['spec']['template']['spec'].get('serviceAccountName'),'secret_refs':[]}
for c in d['spec']['template']['spec']['containers']:
 for e in c.get('env',[]):
  if e['name'] in ['GF_SECURITY_ADMIN_USER','GF_SECURITY_ADMIN_PASSWORD']:
   out['grafana']['secret_refs'].append({'container':c['name'],'env_name':e['name'],'secretKeyRef':e.get('valueFrom',{}).get('secretKeyRef'),'literal_value_present':'value' in e})
out['human_receipt_revocation']='REQUIRES_CUSTODIAN_STATEMENT_NO_SECRET_VALUE'
'''
BOOT = r'''
listing=run(['/usr/bin/systemctl','list-unit-files','--type=service','--no-pager','--no-legend'])
names={'firewalld.service','nftables.service','kubelet.service','containerd.service'}
names.update(l.split()[0] for l in listing.splitlines() if re.search(r'fds|calico|guard|iptables|ip6tables',l,re.I))
if len(names)>30: raise RuntimeError('UNIT_LIMIT')
props=['Id','LoadState','ActiveState','SubState','UnitFileState','Before','After','Requires','Wants','ActiveEnterTimestampMonotonic','InactiveExitTimestampMonotonic','ExecMainStartTimestampMonotonic','FragmentPath','DropInPaths']
out['units']=[]
for name in sorted(names):
 text=run(['/usr/bin/systemctl','show',name,'--no-pager']+[z for p in props for z in ['-p',p]])
 d=dict(l.split('=',1) for l in text.splitlines() if '=' in l)
 d['files']=[meta(p,True) for p in ([d.get('FragmentPath','')]+d.get('DropInPaths','').split()) if p]
 out['units'].append(d)
out['current_boot_protection']='NOT_PROVEN_CONTINUOUS_BY_UNIT_METADATA'
'''
END = "\nexcept Exception as e:\n out['status']='READ_FAILED'; out['error_type']=type(e).__name__; out['error']=str(e)\nout['ended_at_utc']=now()\nprint(json.dumps(out,ensure_ascii=False))\nraise SystemExit(0 if out['status']=='READ_COMPLETE_REVIEW_REQUIRED' else 2)\n"
def source(mode,host):
 body={'edge':EDGE,'control':CONTROL,'grafana':GRAFANA,'boot':BOOT}[mode]+"\nout['status']='READ_COMPLETE_REVIEW_REQUIRED'\n"
 return ('MODE='+repr(mode)+'\nEXPECTED='+repr(host)+'\n'+COMMON+'\ntry:\n'+textwrap.indent(body,' ')+END).encode()
def collect(mode,host,label):
 dest=ROOT/'runtime'/label;dest.mkdir(parents=True,exist_ok=False)
 src=source(mode,host);(dest/'collector.py').write_bytes(src)
 command='/usr/bin/python3 -B -I -S -' if mode=='edge' else '/usr/bin/sudo -n /usr/bin/python3 -B -I -S -'
 inner=['/usr/bin/ssh','-F','/dev/null','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ControlPath=none','-o','UpdateHostKeys=no','svc_ansible@'+HOSTS[host],command]
 bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(src)+',capture_output=True,timeout=180)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
 (dest/'bridge.py').write_bytes(bridge)
 receipt={'start_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':mode,'target':host,'outer_argv':SSH,'inner_argv':inner,'collector_sha256':hashlib.sha256(src).hexdigest(),'bridge_sha256':hashlib.sha256(bridge).hexdigest(),'source_review':'AUTHOR_STATIC_ONLY','authority':'user: 권장순서로 착수; scoped read-only prerequisites'}
 try:
  p=subprocess.run(SSH+['/usr/bin/python3 -B -I -S -'],input=bridge,capture_output=True,timeout=195)
  (dest/'stdout.json').write_bytes(p.stdout);(dest/'stderr.txt').write_bytes(p.stderr)
  receipt.update(rc=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
 except subprocess.TimeoutExpired as e:
  receipt.update(rc=124,error='TRANSPORT_TIMEOUT_NO_RETRY')
  (dest/'stdout.partial').write_bytes(e.stdout or b'');(dest/'stderr.partial').write_bytes(e.stderr or b'')
 receipt['end_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
 (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'target':host,'mode':mode,'rc':receipt['rc'],'path':str(dest)}))
 return receipt['rc']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['edge','control','grafana','boot']);p.add_argument('host',choices=list(HOSTS));p.add_argument('label');a=p.parse_args()
 if a.mode=='edge': assert a.host=='edge01'
 if a.mode in ['control','grafana']: assert a.host=='k8s-control01'
 if a.mode=='boot': assert a.host!='edge01'
 raise SystemExit(collect(a.mode,a.host,a.label))
