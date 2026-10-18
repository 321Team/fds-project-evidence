"""One bounded OS/DNS read, stdin only; no configuration or temp file writes."""
import datetime as dt, hashlib, ipaddress, json, os, pathlib, re, shlex, socket, stat, subprocess
P=pathlib.Path
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
O={'started_at_kst':now(),'host':socket.gethostname(),'uid':os.getuid(),'euid':os.geteuid(),'commands':[],'files':{},'status':'STARTED','configuration_mutations':0,'retry':False}
def need(value,reason):
 if not value:raise ValueError(reason)
def small(path):
 with open(path,'rb') as f:b=f.read(65537)
 need(len(b)<=65536,'BOUNDED_FILE_LIMIT');return b
def public_file(path,allowed_resolved,projection=None):
 target=P(path);resolved=target.resolve(strict=True)
 need(str(resolved) in allowed_resolved,'UNEXPECTED_PUBLIC_FILE_TARGET')
 st=resolved.lstat();need(stat.S_ISREG(st.st_mode) and st.st_uid==0,'PUBLIC_FILE_METADATA')
 fd=os.open(resolved,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  start=os.fstat(fd);need((start.st_dev,start.st_ino)==(st.st_dev,st.st_ino),'PUBLIC_FILE_RACE')
  data=os.read(fd,65537);end=os.fstat(fd)
 finally:os.close(fd)
 need(len(data)<=65536 and len(data)==st.st_size,'PUBLIC_FILE_SIZE')
 need((st.st_dev,st.st_ino,st.st_mtime_ns,st.st_ctime_ns,st.st_size)==(end.st_dev,end.st_ino,end.st_mtime_ns,end.st_ctime_ns,end.st_size),'PUBLIC_FILE_CHANGED')
 text=data.decode();value=projection(text) if projection else text
 O['files'][path]={'resolved':str(resolved),'sha256':sha(data),'bytes':len(data),'uid':st.st_uid,'gid':st.st_gid,'mode':oct(stat.S_IMODE(st.st_mode)),'content_scope':'selected lines only' if projection else 'public file','observed':value}
 return value
ENV={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C','HOME':'/root','PYTHONDONTWRITEBYTECODE':'1'}
def cmd(name,argv,seconds=5):
 row={'name':name,'argv':argv,'started_at_kst':now(),'max_seconds':seconds,'retry':False}
 try:
  q=subprocess.run(argv,capture_output=True,env=ENV,timeout=seconds)
  out,err,rc=q.stdout,q.stderr,q.returncode;row['timed_out']=False
 except subprocess.TimeoutExpired as e:
  out,err,rc=e.stdout or b'',e.stderr or b'',124;row['timed_out']=True
 row.update(ended_at_kst=now(),rc=rc,stdout=out.decode('utf-8','replace'),stderr=err.decode('utf-8','replace'),stdout_sha256=sha(out),stderr_sha256=sha(err));O['commands'].append(row)
 need(rc==0,'COMMAND_FAILED_'+name)
 need(len(out)<=65536 and len(err)<=65536,'COMMAND_OUTPUT_LIMIT_'+name)
 return row['stdout'].strip()

try:
 O['machine_id']=small('/etc/machine-id').decode().strip();O['boot_id']=small('/proc/sys/kernel/random/boot_id').decode().strip()
 need(O['uid']==O['euid']==0,'EXPECTED_EXISTING_SUDO_ROOT')
 need(all(O[k]==EXPECTED[k] for k in ['host','machine_id','boot_id']),'TARGET_IDENTITY_DRIFT')
 release=public_file('/etc/os-release',{'/etc/os-release','/usr/lib/os-release'})
 parsed={}
 for line in release.splitlines():
  if re.match(r'^[A-Z_]+=',line):
   k,v=line.split('=',1);parts=shlex.split(v);parsed[k]=' '.join(parts)
 O['os']={k:parsed.get(k) for k in ['ID','NAME','VERSION_ID','PRETTY_NAME']}
 need(parsed.get('ID')=='centos' and parsed.get('VERSION_ID')=='10','OS_BASELINE_MISMATCH')
 O['selinux_enforce']=small('/sys/fs/selinux/enforce').decode().strip();need(O['selinux_enforce']=='1','SELINUX_NOT_ENFORCING')
 O['time_properties']=cmd('time_properties',['/usr/bin/timedatectl','show','-p','Timezone','-p','NTPSynchronized'])
 time_values=dict(line.split('=',1) for line in O['time_properties'].splitlines())
 need(time_values.get('Timezone')=='Asia/Seoul' and time_values.get('NTPSynchronized')=='yes','TIME_PRECHECK_MISMATCH')
 swaps=small('/proc/swaps');O['swaps']={'sha256':sha(swaps),'raw':swaps.decode()};need(len(swaps.decode().splitlines())==1,'ACTIVE_SWAP')
 O['modules']={m:P('/sys/module',m).is_dir() for m in ['overlay','br_netfilter']};need(all(O['modules'].values()),'REQUIRED_MODULE_MISSING')
 O['sysctl']={k:small('/proc/sys/'+k.replace('.','/')).decode().strip() for k in ['net.bridge.bridge-nf-call-iptables','net.bridge.bridge-nf-call-ip6tables','net.ipv4.ip_forward']};need(all(v=='1' for v in O['sysctl'].values()),'SYSCTL_PRECHECK_MISMATCH')
 route=json.loads(cmd('management_route',['/usr/sbin/ip','-4','-j','route','get','10.250.10.10']))
 need(len(route)==1 and route[0].get('gateway')=='10.1.93.58','MANAGEMENT_ROUTE_MISMATCH')
 interface=route[0]['dev'];need(bool(re.fullmatch(r'[A-Za-z0-9_.:-]{1,32}',interface)),'INTERFACE_FORMAT')
 O['interface']=interface
 connection=cmd('active_connection',['/usr/bin/nmcli','--get-values','GENERAL.CONNECTION','device','show',interface]);need(connection not in ['','--'] and '\n' not in connection,'ACTIVE_CONNECTION_UNCONFIRMED')
 dns=cmd('profile_dns',['/usr/bin/nmcli','--get-values','ipv4.dns','connection','show',connection]).replace(',',' ').split()
 search=cmd('profile_search',['/usr/bin/nmcli','--get-values','ipv4.dns-search','connection','show',connection]).replace(',',' ').split()
 ignore=cmd('profile_ignore_auto',['/usr/bin/nmcli','--get-values','ipv4.ignore-auto-dns','connection','show',connection]).lower()
 O['dns_profile']={'connection':connection,'servers':dns,'search':search,'ignore_auto':ignore}
 need(dns==['10.1.93.52','10.1.93.53'] and search==['fds.internal'] and ignore in ['yes','true','1'],'PROFILE_DNS_MISMATCH')
 resolver=public_file('/etc/resolv.conf',{'/etc/resolv.conf','/run/NetworkManager/resolv.conf','/run/systemd/resolve/resolv.conf','/run/systemd/resolve/stub-resolv.conf'},lambda text:[line for line in text.splitlines() if re.match(r'^\s*(nameserver|search|domain|options)\s',line)])
 nameservers=[line.split()[1] for line in resolver if line.split()[0]=='nameserver'];domains=[line.split()[1:] for line in resolver if line.split()[0]=='search']
 need(nameservers==dns and domains==[search],'LIVE_RESOLVER_MISMATCH')
 nss=public_file('/etc/nsswitch.conf',{'/etc/nsswitch.conf','/etc/authselect/nsswitch.conf'},lambda text:[line for line in text.splitlines() if re.match(r'^\s*hosts\s*:',line)])
 need(len(nss)==1,'NSS_HOSTS_ENTRY_MISSING_OR_MULTIPLE')
 for server in dns:
  answer=cmd('direct_'+server,['/usr/bin/dig','+time=2','+tries=1','+short','@'+server,'k8s-api.fds.internal','A'],4)
  need('10.1.93.109' in answer.splitlines(),'DIRECT_DNS_ANSWER_MISMATCH_'+server)
 for name in ['k8s-api.fds.internal','k8s-api','github.com']:
  answer=cmd('system_'+name,['/usr/bin/getent','ahostsv4',name],5)
  ips={line.split()[0] for line in answer.splitlines() if line.split()}
  need(bool(ips) and all(ipaddress.ip_address(ip).version==4 for ip in ips),'DNS_IPV4_ANSWER_INVALID')
  if name!='github.com':need('10.1.93.109' in ips,'SYSTEM_DNS_ANSWER_MISMATCH_'+name)
 O['boot_after']=small('/proc/sys/kernel/random/boot_id').decode().strip();need(O['boot_after']==O['boot_id'],'BOOT_CHANGED_DURING_READ')
 O['status']='PASS_SCOPED_CURRENT_OS_DNS_READ'
except Exception as e:
 O['status']='STOP_FIRST_ERROR_NO_RETRY';O['error_type']=type(e).__name__;O['error']=str(e)
O['ended_at_kst']=now()
print(json.dumps(O,ensure_ascii=False),flush=True)
raise SystemExit(0 if O['status']=='PASS_SCOPED_CURRENT_OS_DNS_READ' else 1)
