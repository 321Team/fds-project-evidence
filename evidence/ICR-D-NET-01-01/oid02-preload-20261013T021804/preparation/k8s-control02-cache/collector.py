import datetime,hashlib,json,os,pathlib,socket,stat,subprocess,time
assert os.geteuid()==0 and socket.gethostname()=='k8s-control02','HOST_OR_PRIVILEGE'
started=time.monotonic()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
out={'host':socket.gethostname(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'started_at_utc':now(),'scope':'read only OID scheduling/cache/CLI prerequisites; no export/import/retag/pull/unpack/pod/reboot','commands':[]}
def query(argv,limit=8):
 assert time.monotonic()-started<65,'READ_BUDGET'
 row={'argv':argv,'started_at_utc':now()}
 try:
  p=subprocess.run(argv,capture_output=True,timeout=limit,env=dict(os.environ,LC_ALL='C'))
  row.update(rc=p.returncode,stdout_bytes=len(p.stdout),stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_bytes=len(p.stderr),stderr_sha256=hashlib.sha256(p.stderr).hexdigest(),stderr=p.stderr.decode(errors='replace'),finished_at_utc=now())
  assert len(p.stdout)<4*1024*1024 and len(p.stderr)<65536,'OUTPUT_BOUND'
  out['commands'].append(row);return row,p.stdout
 except subprocess.TimeoutExpired:
  row.update(rc=None,error='READ_TIMEOUT_NO_RETRY',finished_at_utc=now());out['commands'].append(row);raise
try:
 ip,raw=query(['/usr/sbin/ip','-j','-4','address','show']);assert ip['rc']==0
 addresses=[x['local'] for y in json.loads(raw) for x in y.get('addr_info',[]) if x.get('family')=='inet'];assert '10.1.93.103' in addresses
 ip['addresses']=addresses
 assert stat.S_ISSOCK(os.stat('/run/containerd/containerd.sock').st_mode)
 ctr=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io']
 needles=['quay.io/calico/kube-controllers','registry.k8s.io/coredns/coredns','df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3','e7e6440cfd1e919280958f5b5a6ab2b184d385bba774c12ad2a9e1e4183f90d9']
 refs=['quay.io/calico/kube-controllers@sha256:'+needles[2],'registry.k8s.io/coredns/coredns:v1.14.2','registry.k8s.io/coredns/coredns@sha256:'+needles[3]]
 for args in [['version'],['images','list']]+[['images','check','name=='+ref] for ref in refs]:
  row,raw=query(ctr+args,10);assert row['rc']==0
  txt=raw.decode(errors='replace')
  row['stdout_selected_lines']='\n'.join(line for i,line in enumerate(txt.splitlines()) if args!=['images','list'] or i==0 or any(s in line for s in needles))
  row['selection']='all output' if args!=['images','list'] else 'header plus fixed image reference/digest rows only'
 for path in ['/usr/bin/ctr']+[p for p in ['/usr/bin/crictl','/usr/local/bin/crictl'] if pathlib.Path(p).is_file()]:
  p=pathlib.Path(path);raw=p.read_bytes();out.setdefault('binaries',[]).append({'path':path,'resolved':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)})
 for path in ['/root','/var/lib/containerd']:
  s=os.statvfs(path);out.setdefault('space',[]).append({'path':path,'free_bytes':s.f_bavail*s.f_frsize,'free_inodes':s.f_favail})
 row,raw=query(['/usr/bin/systemctl','is-active','containerd','kubelet']);row['stdout']=raw.decode();assert row['rc']==0
 row,raw=query(['/usr/sbin/getenforce']);row['stdout']=raw.decode();assert row['rc']==0
 if socket.gethostname()=='k8s-control01':
  for args in [['images','export','--help'],['images','import','--help'],['images','tag','--help'],['images','remove','--help']]:
   row,raw=query(ctr+args);row['stdout']=raw.decode();assert row['rc']==0
 out['status']='COLLECTED_REVIEW_REQUIRED'
except Exception as e:out.update(status='INCOMPLETE',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
