import datetime,hashlib,json,os,pathlib,pwd,re,socket,ssl,stat,subprocess
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
