MODE='boot'
EXPECTED='k8s-control01'

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

 out['status']='READ_COMPLETE_REVIEW_REQUIRED'

except Exception as e:
 out['status']='READ_FAILED'; out['error_type']=type(e).__name__; out['error']=str(e)
out['ended_at_utc']=now()
print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if out['status']=='READ_COMPLETE_REVIEW_REQUIRED' else 2)
