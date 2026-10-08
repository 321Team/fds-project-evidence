import datetime,hashlib,json,os,pathlib,shutil,socket,subprocess
assert os.geteuid()==0
assert socket.gethostname().split('.')[0] in ('k8s-control01','k8s-worker01','k8s-worker02','k8s-worker03')
def run(argv):
    p=subprocess.run(argv,capture_output=True,timeout=15)
    return {'command':argv,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
r={'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256'],'tools':{n:shutil.which(n) for n in ('crictl','nsenter','python3','iptables-save','tcpdump')},'pods':[]}
p=run(['ctr','-n','k8s.io','tasks','list'])
assert p['rc']==0,p['stderr']
for row in p['stdout'].splitlines()[1:]:
    cid,pid,status=row.split(); pid=int(pid)
    if status!='RUNNING': continue
    v=run(['ctr','-n','k8s.io','containers','info',cid]); assert v['rc']==0
    data=json.loads(v['stdout']); labels=data['Labels']
    if labels.get('io.cri-containerd.kind')!='sandbox': continue
    m={k:labels.get('io.kubernetes.pod.'+k) for k in ('name','namespace','uid')}
    if m['namespace'] not in ('fds-app','monitoring-api','kube-system'): continue
    if m['namespace']=='kube-system' and not m['name'].startswith('coredns-'): continue
    r['pods'].append({'metadata':m,'sandbox_id':cid,'pid':pid,'starttime':pathlib.Path('/proc/%d/stat'%pid).read_text().rsplit(')',1)[1].split()[19],'netns':os.readlink('/proc/%d/ns/net'%pid),'cgroup':pathlib.Path('/proc/%d/cgroup'%pid).read_text(), 'host_netns':os.readlink('/proc/1/ns/net')})
r['iptables']=run(['iptables-save','-c','-t','filter'])
r['routes']=[run(['ip','-j','route','get',ip]) for ip in ('10.244.39.209','10.244.69.237','10.244.79.113')]
print(json.dumps(r,indent=2))
