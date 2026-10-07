import datetime,hashlib,json,os,pathlib,shutil,socket,subprocess
assert os.geteuid()==0
assert socket.gethostname().split('.')[0] in ('k8s-control01','k8s-worker01','k8s-worker02','k8s-worker03')
def run(argv):
    p=subprocess.run(argv,capture_output=True,timeout=15)
    return {'command':argv,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
r={'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256'],'tools':{n:shutil.which(n) for n in ('crictl','nsenter','python3','iptables-save','tcpdump')},'pods':[]}
p=run(['crictl','pods','-o','json'])
assert p['rc']==0,p['stderr']
for pod in json.loads(p['stdout'])['items']:
    m=pod['metadata']
    if pod['state']!='SANDBOX_READY' or m['namespace'] not in ('fds-app','monitoring-api','kube-system'): continue
    if m['namespace']=='kube-system' and not m['name'].startswith('coredns-'): continue
    v=run(['crictl','inspectp',pod['id']]); assert v['rc']==0
    data=json.loads(v['stdout']); pid=int(data['info']['pid'])
    r['pods'].append({'metadata':m,'sandbox_id':pod['id'],'pid':pid,'starttime':pathlib.Path('/proc/%d/stat'%pid).read_text().rsplit(')',1)[1].split()[19],'netns':os.readlink('/proc/%d/ns/net'%pid),'network':data['status'].get('network'), 'host_netns':os.readlink('/proc/1/ns/net')})
r['iptables']=run(['iptables-save','-c','-t','filter'])
print(json.dumps(r,indent=2))
