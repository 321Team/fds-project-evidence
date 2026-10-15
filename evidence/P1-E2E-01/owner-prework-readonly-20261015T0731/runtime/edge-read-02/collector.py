MODE='edge'
EXPECTED='edge01'

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

try:

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

 out['status']='READ_COMPLETE_REVIEW_REQUIRED'

except Exception as e:
 out['status']='READ_FAILED'; out['error_type']=type(e).__name__; out['error']=str(e)
out['ended_at_utc']=now()
print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if out['status']=='READ_COMPLETE_REVIEW_REQUIRED' else 2)
