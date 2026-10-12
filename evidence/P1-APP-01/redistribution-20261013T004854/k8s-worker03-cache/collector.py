import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-worker03' and os.geteuid()==0,'STOP_HOST'
refs=['10.1.93.54/fds/transaction-api@sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33','10.1.93.54/fds/fds-engine@sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369']
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'boot':open('/proc/sys/kernel/random/boot_id').read().strip(),'scope':'fixed image local content/unpack metadata and service reads; no pull/import/unpack/start','commands':[]}
for argv in [['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io','images','check','name=='+ref] for ref in refs]+[['/usr/bin/systemctl','is-active','kubelet','containerd'],['/usr/sbin/getenforce']]:
 p=subprocess.run(argv,capture_output=True,text=True,timeout=12,env=dict(os.environ,LC_ALL='C'))
 out['commands'].append({'argv':argv,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
assert os.path.isdir('/var/lib/containerd')
st=os.statvfs('/var/lib/containerd');out['free_bytes']=st.f_bavail*st.f_frsize;out['free_inodes']=st.f_favail
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out['collection_status']='COLLECTED' if all(x['rc']==0 for x in out['commands']) else 'INCOMPLETE'
print(json.dumps(out));raise SystemExit(0 if out['collection_status']=='COLLECTED' else 2)
