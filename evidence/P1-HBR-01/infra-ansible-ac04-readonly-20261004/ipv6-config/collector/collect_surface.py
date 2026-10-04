"""Read-only persistence configuration evidence, never activates NM or applies sysctl."""
import datetime, hashlib, json, os, pathlib, re, socket, subprocess, sys
UUID=re.compile(r'^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$')
KEY=re.compile(r'^\s*(net[./]ipv6[./]conf[./](?:all|default|ens160)[./]disable_ipv6)\s*=\s*(.*?)\s*$')

def emit(v):print(json.dumps(v,ensure_ascii=False),flush=True)
def command(name,argv):
 v={'name':name,'argv':argv,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=45);v.update(rc=r.returncode,stdout=r.stdout.decode(errors='replace'),stderr=r.stderr.decode(errors='replace'))
 except (OSError,subprocess.TimeoutExpired) as exc:v.update(rc=124 if isinstance(exc,subprocess.TimeoutExpired) else 127,error=type(exc).__name__)
 emit(v);return v

def selected_lines(text):
 result=[]
 for i,line in enumerate(text.splitlines()):
  match=KEY.match(line)
  if match:result.append({'line':i+1,'key':match[1],'value':match[2]})
 return result

def config_record(p):
 v={'name':'sysctl-config','path':str(p)}
 if p.is_symlink():return dict(v,status='SYMLINK_REVIEW_REQUIRED',target=os.readlink(p))
 try:
  with p.open('rb') as f:data=f.read(1048577)
  if len(data)>1048576:raise ValueError('TOO_LARGE')
  v.update(sha256=hashlib.sha256(data).hexdigest(),selected_directives=selected_lines(data.decode(errors='replace')))
 except FileNotFoundError:v['status']='ABSENT'
 except (OSError,ValueError) as exc:v.update(status='READ_FAILED',error=type(exc).__name__)
 return v

def main():
 if socket.gethostname().split('.')[0]!='harbor01' or os.geteuid()!=0:
  emit({'status':'STOP_TARGET_OR_PRIVILEGE_MISMATCH'});return 1
 identity=command('identity-addresses',['ip','-j','address','show'])
 try:
  v=json.loads(identity.get('stdout',''));valid=identity['rc']==0 and isinstance(v,list) and any(isinstance(i,dict) and i.get('ifname')=='ens160' and any(a.get('local')=='10.1.93.54' for a in i.get('addr_info',[])) for i in v)
 except (ValueError,TypeError,AttributeError):valid=False
 if not valid:emit({'status':'STOP_ADDRESS_MISMATCH'});return 1
 records=[identity]
 uuid=command('active-connection-uuid',['nmcli','-g','GENERAL.CON-UUID','device','show','ens160']);records.append(uuid)
 value=uuid.get('stdout','').strip()
 if uuid['rc']!=0 or not UUID.fullmatch(value):emit({'status':'STOP_ACTIVE_CONNECTION_UUID_UNAVAILABLE'});return 1
 for name,argv in [
 ('ipv6-profile',['nmcli','-g','connection.uuid,connection.interface-name,connection.autoconnect,ipv6.method','connection','show','uuid',value]),
 ('networkmanager-unit',['systemctl','show','NetworkManager.service','--property=LoadState,ActiveState,SubState,UnitFileState']),
 ('sysctl-loader-unit',['systemctl','show','systemd-sysctl.service','--property=LoadState,ActiveState,SubState,FragmentPath,DropInPaths,ExecStart'])]:records.append(command(name,argv))
 # In-memory versus persistent profiles are distinguished by file backing evidence.
 # Only matching UUID and IPv6 method/interface/autoconnect directives are exposed.
 dirs=['/etc/NetworkManager/system-connections','/run/NetworkManager/system-connections','/usr/lib/NetworkManager/system-connections']
 profiles=[];read_failures=[]
 for directory in dirs:
  d=pathlib.Path(directory)
  if not d.exists():emit({'name':'nm-profile-directory','path':directory,'status':'ABSENT'});continue
  try:items=sorted(d.iterdir())
  except OSError:read_failures.append(directory);continue
  for p in items:
   if not p.is_file() or p.is_symlink():
    if p.is_symlink():emit({'name':'nm-profile-link','path':str(p),'status':'LINK_REQUIRES_REVIEW'})
    continue
   try:
    with p.open('rb') as f:data=f.read(1048577)
    if len(data)>1048576:raise ValueError('TOO_LARGE')
    text=data.decode(errors='replace');section='';fields={}
    for line in text.splitlines():
     s=line.strip()
     if s.startswith('[') and s.endswith(']'):section=s[1:-1]
     elif '=' in s and not s.startswith(('#',';')):
      k,val=s.split('=',1)
      if (section,k.strip()) in {('connection','uuid'),('connection','interface-name'),('connection','autoconnect'),('ipv6','method')}:fields[section+'.'+k.strip()]=val.strip()
    if fields.get('connection.uuid')==value:
     profile={'name':'matching-nm-profile','path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'selected_fields':fields};profiles.append(profile);emit(profile)
   except (OSError,ValueError):read_failures.append(str(p))
 files=[pathlib.Path('/etc/sysctl.conf')]
 for directory in ['/etc/sysctl.d','/run/sysctl.d','/usr/local/lib/sysctl.d','/usr/lib/sysctl.d']:
  try:files.extend(sorted(pathlib.Path(directory).glob('*.conf')))
  except OSError:read_failures.append(directory)
 for p in files:
  rec=config_record(p);emit(rec)
  if rec.get('status')=='READ_FAILED':read_failures.append(str(p))
 failed=[r['name'] for r in records if r['rc']!=0]
 emit({'verdict':'COLLECTION_FAILED' if failed or read_failures else 'IPV6_CONFIG_CAPTURED_REVIEW_REQUIRED','failed_commands':failed,'read_failures':read_failures,'matching_profile_count':len(profiles),'profile_loader_precedence':'REVIEW_REQUIRED','reboot_reconnect_persistence':'NOT_TESTED','runtime_apply':False,'apply_approval':'NOT_GRANTED'})
 return 1 if failed or read_failures else 0
if __name__=='__main__':sys.exit(main())
