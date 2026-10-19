"""Existing sudo read route, bounded public certificates only, then at most one root GET."""
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,subprocess
from pathlib import Path
D=Path('\\\\?\\'+str(Path(__file__).resolve().parent));RAW=D/'RAW';RAW.mkdir(exist_ok=True)
B=D.parent.parent;C=B.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone(timedelta(hours=9))).isoformat()
def save(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
transport=B/'Ansible/ntp-normal-series-preparation-20261019-1215/TRANSPORT_BINDING.json'
tr=load(transport);node=next(n for n in tr['nodes'] if n['host']=='k8s-worker03')
outer=tr['outer_argv'];inner=node['inner_argv']
assert inner[-2]=='svc_ansible@10.1.93.108' and inner[-1]=='sudo -n /usr/bin/python3 -B -I -S -'
prev=D.parent/'postboot-worker03-tls-once-20261019-1231'
refs=[transport,prev/'FINAL_BINDING.json',prev/'RAW/WORKER03_TLS.stdout.json',
    C/'remaining-minimum-execution-20261019-1223/GW_USER_CONSOLE_RECEIPT.json',
    C/'remaining-minimum-execution-20261019-1223/NTP_ROUND5.stdout.json']
save(D/'CURRENT_TASK.json',dict(at_kst=now(),task='WORKER03_EXISTING_SUDO_PUBLIC_CA_BOUNDED_READ_THEN_UNCONSUMED_TLS_ROOT_GET',
  references=[dict(path=str(p),sha256=sha(p)) for p in refs],access='Existing svc_ansible -> sudo -n python, root/euid0/SUDO_USER guard',
  cause='Prior nonroot is_file did not distinguish missing paths from parent access restrictions; no HTTP was attempted',
  max_public_certificate_files=64,max_certificate_bytes=131072,max_root_GETs=1,
  private_keys=False,auth_configuration=False,trust_import=False,server_mutations=0,automatic_retry=False))
source=r'''import datetime,hashlib,json,os,pathlib,pwd,re,socket,ssl,stat,subprocess
P=pathlib.Path
PIN='6a75baf4dbe03ef24cce944e616384d318f7ca919cd7bd914624b4cebac06b10'
EXPECTED=('0bb03794b5b04dc4bded6bd75d63f701','2e3c5d9a-b386-4c20-8c0b-f5f7f0e10b0c')
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def identity():return dict(host=socket.gethostname(),uid=os.getuid(),euid=os.geteuid(),account=pwd.getpwuid(os.geteuid()).pw_name,sudo_user=os.environ.get('SUDO_USER'),machine_id=P('/etc/machine-id').read_text().strip(),boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip())
def guarded(v):return v['host']=='k8s-worker03' and v['uid']==v['euid']==0 and v['account']=='root' and v['sudo_user']=='svc_ansible' and (v['machine_id'],v['boot_id'])==EXPECTED
out=dict(task='WORKER03_PUBLIC_CA_ROOT_READ_THEN_TLS_ROOT_ONCE',started_at_kst=now(),queries=[],certificate_results=[],HTTP_attempts=0,mutations=0,credential_reads=0,trust_import=0,retry=False)
def finish(status,rc):out.update(status=status,ended_at_kst=now());print(json.dumps(out));raise SystemExit(rc)
def query(label,argv):
 p=subprocess.run(argv,capture_output=True,timeout=5,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C'})
 row=dict(label=label,argv=argv,rc=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode());out['queries'].append(row)
 if p.returncode:finish('HOLD_PREFLIGHT_COMMAND_FAILED_NO_GET',2)
 return json.loads(row['stdout'])
try:
 out['identity_before']=identity()
 if not guarded(out['identity_before']):finish('HOLD_ROOT_SUDO_OR_IDENTITY_MISMATCH',2)
 addresses=query('current_source_address',['/usr/sbin/ip','-j','-4','addr','show','dev','ens160'])
 if not any(x.get('ifname')=='ens160' and any(a.get('local')=='10.1.93.108' for a in x.get('addr_info',[])) for x in addresses):finish('HOLD_SOURCE_IP_NO_GET',2)
 route=query('current_management_route',['/usr/sbin/ip','-j','-4','route','get','10.250.10.30'])
 if len(route)!=1 or route[0].get('prefsrc')!='10.1.93.108' or route[0].get('gateway')!='10.1.93.58' or route[0].get('dev')!='ens160':finish('HOLD_ROUTE_NO_GET',2)
 candidates=[]
 for registry in ('harbor01:443','10.1.93.54','10.1.93.54:443','10.250.10.30','10.250.10.30:443'):
  for n in ('ca.crt','fds-root-ca.crt'):candidates.append(P('/etc/containerd/certs.d')/registry/n)
 anchor=P('/etc/pki/ca-trust/source/anchors')
 try:
  entries=sorted(p for p in anchor.iterdir() if p.suffix.lower() in ('.crt','.pem'))
  if len(entries)>64:finish('HOLD_ANCHOR_FILE_COUNT_LIMIT',2)
  candidates.extend(entries)
 except FileNotFoundError:out['anchor_directory_state']='FileNotFound'
 except PermissionError:out['anchor_directory_state']='PermissionError';finish('HOLD_PUBLIC_ANCHOR_PERMISSION_NO_GET',2)
 if len(candidates)>64:finish('HOLD_TOTAL_PUBLIC_FILE_COUNT_LIMIT',2)
 out['certificate_candidate_count']=len(candidates);chosen=None
 for p in candidates:
  row=dict(path=str(p))
  try:
   ls=p.lstat();row.update(lstat_mode=oct(stat.S_IMODE(ls.st_mode)),lstat_uid=ls.st_uid,file_type='symlink' if stat.S_ISLNK(ls.st_mode) else 'regular' if stat.S_ISREG(ls.st_mode) else 'other')
   resolved=p.resolve(strict=True);row['resolved_path']=str(resolved)
   if not str(resolved).startswith(('/etc/containerd/certs.d/','/etc/pki/ca-trust/source/anchors/')):row['state']='ExcludedTargetOutsidePublicScope';out['certificate_results'].append(row);continue
   s=p.stat();row.update(mode=oct(stat.S_IMODE(s.st_mode)),uid=s.st_uid,size=s.st_size)
   if not stat.S_ISREG(s.st_mode):row['state']='ExcludedNotRegular';out['certificate_results'].append(row);continue
   if s.st_size>131072:row['state']='ExcludedFileSizeLimit';out['certificate_results'].append(row);continue
   with p.open('rb') as f:raw=f.read(131073)
   if len(raw)>131072:row['state']='ReadSizeLimit';out['certificate_results'].append(row);finish('HOLD_FILE_GREW_NO_GET',2)
   blocks=re.findall(b'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',raw,re.S)
   if len(blocks)!=1:row['state']='NotSinglePublicCertificate';out['certificate_results'].append(row);continue
   der=ssl.PEM_cert_to_DER_cert(blocks[0].decode('ascii'));h=hashlib.sha256(der).hexdigest()
   row.update(state='PublicCertificateRead',DER_sha256=h,PEM_sha256=hashlib.sha256(raw).hexdigest(),pin_match=h==PIN)
   if h==PIN and chosen is None:chosen=(p,row['PEM_sha256'])
  except FileNotFoundError:row['state']='FileNotFound'
  except PermissionError:row['state']='PermissionError';out['certificate_results'].append(row);finish('HOLD_PUBLIC_CA_PERMISSION_NO_GET',2)
  except (OSError,ValueError,UnicodeError) as e:row.update(state='PublicReadOrParseError',error_type=type(e).__name__);out['certificate_results'].append(row);finish('HOLD_CA_READ_ERROR_NO_GET',2)
  out['certificate_results'].append(row)
 if chosen is None:finish('HOLD_PINNED_PUBLIC_CA_NOT_FOUND_NO_GET',2)
 ca,ca_pem_sha=chosen;out['selected_CA']=dict(path=str(ca),DER_sha256=PIN,PEM_sha256=ca_pem_sha)
 out['identity_before_GET']=identity()
 if not guarded(out['identity_before_GET']) or hashlib.sha256(ca.read_bytes()).hexdigest()!=ca_pem_sha:finish('HOLD_IDENTITY_OR_CA_DRIFT_BEFORE_GET',2)
 fmt='{"local_ip":"%{local_ip}","local_port":%{local_port},"remote_ip":"%{remote_ip}","remote_port":%{remote_port},"http_code":"%{http_code}","ssl_verify_result":%{ssl_verify_result},"num_connects":%{num_connects},"url_effective":"%{url_effective}","time_connect":%{time_connect},"time_appconnect":%{time_appconnect},"time_total":%{time_total}}\n'
 argv=['/usr/bin/curl','-q','--silent','--show-error','--request','GET','--proto','=https','--tlsv1.2','--noproxy','*','--proxy','','--interface','10.1.93.108','--connect-to','10.1.93.54:443:10.250.10.30:443','--cacert',str(ca),'--connect-timeout','5','--max-time','10','--retry','0','--max-redirs','0','--output','/dev/null','--write-out',fmt,'https://10.1.93.54/']
 out['HTTP_attempts']=1;out['request']=dict(argv=argv,started_at_kst=now(),method='GET',path='/',authentication=False,redirects=False,body_saved=False)
 p=subprocess.run(argv,capture_output=True,timeout=15,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','LANG':'C','HOME':'/nonexistent'})
 out['request'].update(ended_at_kst=now(),rc=p.returncode,stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
 try:out['request']['observed']=json.loads(out['request']['stdout'])
 except ValueError:pass
 out['identity_after_GET']=identity();out['CA_unchanged_after_GET']=hashlib.sha256(ca.read_bytes()).hexdigest()==ca_pem_sha
 if not guarded(out['identity_after_GET']) or not out['CA_unchanged_after_GET']:finish('OBSERVED_IDENTITY_OR_CA_DRIFT_REVIEW_REQUIRED',2)
 finish('SINGLE_GET_RECORDED_NO_RETRY',0)
except (OSError,ValueError,subprocess.TimeoutExpired) as e:
 out['error_type']=type(e).__name__;finish('HOLD_OR_UNCERTAIN_READ_FAILURE_NO_RETRY',2)
'''
compile(source,'root-public-ca-tls-once','exec')
(D/'PUBLIC_CA_TLS_SOURCE.py').write_text(source,encoding='utf-8',newline='\n')
old=(prev/'WORKER03_TLS.bridge.stdin').read_text(encoding='utf-8-sig');body=old[old.index('import json,subprocess,sys'):]
guard='''import os,pathlib,pwd,socket,sys
if socket.gethostname()!='ansible01' or os.geteuid()!=1000 or pwd.getpwuid(os.geteuid()).pw_name!='server01_ansible' or pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()!='0317c0f8-cdc9-4c5e-a28e-48961c75e62e':
 sys.stderr.write('HOLD_RELAY_IDENTITY_NO_WORKER_CALL\\n');raise SystemExit(2)
'''
bridge=('INNER='+repr(inner)+'\nPAYLOAD='+repr(source.encode())+'\n'+guard+'\n'+body).encode()
compile(bridge,'existing-root-read-relay','exec');(D/'PUBLIC_CA_TLS.bridge.stdin').write_bytes(bridge)
save(RAW/'INTENT.json',dict(at_kst=now(),outer_argv=outer,inner_argv=inner,
    source_sha256=sha(D/'PUBLIC_CA_TLS_SOURCE.py'),bridge_sha256=sha(D/'PUBLIC_CA_TLS.bridge.stdin'),
    max_public_certificates=64,max_bytes_each=131072,max_HTTPS_root_GET=1,
    expected_CA_DER_SHA256='6a75baf4dbe03ef24cce944e616384d318f7ca919cd7bd914624b4cebac06b10',
    no_private_key_or_auth_config_reads=True,no_trust_import=True,retry=False,
    pure_verifier='Existing authorized root read only; no files/settings/permissions modified or deployment input emitted'))
p=subprocess.Popen(outer,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out,err=p.communicate(bridge)
(RAW/'PUBLIC_CA_TLS.stdout.json').write_bytes(out);(RAW/'PUBLIC_CA_TLS.stderr.txt').write_bytes(err)
save(RAW/'RECEIPT.json',dict(at_kst=now(),outer_rc=p.returncode,stdout_bytes=len(out),stderr_bytes=len(err),
    stdout_sha256=sha(RAW/'PUBLIC_CA_TLS.stdout.json'),stderr_sha256=sha(RAW/'PUBLIC_CA_TLS.stderr.txt'),retry=False,mutations=0))
try:v=json.loads(out);print(json.dumps(dict(outer_rc=p.returncode,status=v.get('status'),HTTP_attempts=v.get('HTTP_attempts'),selected_CA=v.get('selected_CA'),request=v.get('request')),ensure_ascii=False))
except ValueError:print(json.dumps(dict(outer_rc=p.returncode,stdout_bytes=len(out),stderr_bytes=len(err))))
