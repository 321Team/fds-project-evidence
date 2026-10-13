"""Bounded installed-binary, RPM-cache and boot-unit metadata; no downloads."""
import datetime, hashlib, json, os, shutil, socket, subprocess, time
from pathlib import Path

host = socket.gethostname()
assert host in ['k8s-'+r+str(n).zfill(2) for r in ('control','worker') for n in (1,2,3)]
assert os.geteuid() == 0
started = time.monotonic()
out = {'schema':'P1-OID03-current-inventory-1', 'host':host,
       'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
       'mutation':False, 'network_fetch':False, 'queries':[], 'binaries':[],
       'limit':'current installation and bounded cache metadata; not original supply provenance or reboot protection proof'}

def run(name, argv):
    remaining = 45-(time.monotonic()-started)
    if remaining <= 0:
        out['queries'].append({'name':name,'status':'BUDGET_EXHAUSTED'}); return None
    at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r = subprocess.run(argv, capture_output=True, timeout=min(8,remaining))
    except subprocess.TimeoutExpired:
        out['queries'].append({'name':name,'at_utc':at,'argv':argv,'status':'TIMEOUT'}); return None
    if len(r.stdout)>262144 or len(r.stderr)>65536:
        out['queries'].append({'name':name,'argv':argv,'status':'OUTPUT_TOO_LARGE','rc':r.returncode}); return None
    q = {'name':name,'at_utc':at,'argv':argv,'rc':r.returncode,
         'stdout':r.stdout.decode('utf-8',errors='replace'),
         'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'stderr_bytes':len(r.stderr)}
    out['queries'].append(q); return r

for name in ('kubeadm','kubelet','kubectl','containerd','ctr','crictl'):
    p = shutil.which(name)
    if not p:
        # Existing approved system paths only; do not search arbitrary user homes.
        p = next((str(x) for parent in ('/usr/local/bin','/usr/local/sbin','/usr/bin','/usr/sbin')
                  if (x:=Path(parent)/name).is_file()),None)
    row={'name':name,'path':p}
    if p:
        real = Path(p).resolve(strict=True); s=real.stat()
        row.update(resolved_path=str(real),uid=s.st_uid,gid=s.st_gid,mode=oct(s.st_mode & 0o7777),size=s.st_size)
        r=run('rpm-owner-'+name,['/usr/bin/rpm','-qf',str(real),'--qf','%{NAME}\t%{VERSION}-%{RELEASE}\t%{ARCH}\t%{SOURCERPM}\n'])
        row['rpm_owner_rc']=None if r is None else r.returncode
    out['binaries'].append(row)

run('boot-units',['/usr/bin/systemctl','show','--no-pager','kubelet.service','containerd.service','firewalld.service',
    '-p','Id','-p','LoadState','-p','UnitFileState','-p','ActiveState','-p','SubState','-p','After','-p','Before',
    '-p','Requires','-p','Wants','-p','ActiveEnterTimestampMonotonic'])
r=run('unit-file-names',['/usr/bin/systemctl','list-unit-files','--no-pager','--no-legend'])
if r is not None:
    out['queries'][-1]['stdout']='\n'.join(line for line in r.stdout.decode().splitlines()
        if any(s in line.lower() for s in ('calico','fds-','guard','kubelet','containerd','firewalld')))+'\n'
    out['queries'][-1]['projection']='matching unit names/state only'

cache=Path('/var/cache/dnf'); rows=[]; count=0; bounded=False
if cache.exists() and not cache.is_symlink():
    for root, dirs, files in os.walk(cache,followlinks=False):
        dirs[:]=[d for d in dirs if not (Path(root)/d).is_symlink()]
        for name in files:
            count+=1
            if count>3000 or time.monotonic()-started>45:
                bounded=True;break
            if name.endswith('.rpm') and name.startswith(('kubeadm-','kubelet-','kubectl-','cri-tools-','containerd','runc-','kubernetes-cni-')):
                p=Path(root)/name;s=p.lstat()
                rows.append({'path':str(p),'size':s.st_size,'mode':oct(s.st_mode & 0o7777),'symlink':p.is_symlink()})
        if bounded:break
out['selected_rpm_cache']={'root':str(cache),'exists':cache.exists(),'symlink':cache.is_symlink(),
    'visited_files':count,'bounded':bounded,'matches':rows,'content_or_signature_verified':False,
    'scope':'only named package filename prefixes; absence here is not absence from all supply stores'}
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(out,ensure_ascii=True,sort_keys=True))
