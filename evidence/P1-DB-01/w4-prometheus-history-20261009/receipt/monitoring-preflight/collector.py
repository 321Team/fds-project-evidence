import datetime,hashlib,json,os,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'
out={'schema':'fds.monitoring-store-preflight.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[]}
for kind in ('services','pods'):
    path='/api/v1/namespaces/monitoring-api/'+kind
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
    p=subprocess.run(cmd,capture_output=True,timeout=15)
    row={'path':path,'rc':p.returncode,'body_sha256':hashlib.sha256(p.stdout).hexdigest(),'items':[]}
    if p.returncode==0:
        for item in json.loads(p.stdout).get('items',[]):
            m=item['metadata'];s=item.get('spec',{})
            if not any(n in m['name'] for n in ('prometheus','loki','elastic','fluent','vector')):continue
            row['items'].append({'name':m['name'],'uid':m['uid'],'nodeName':s.get('nodeName'),'clusterIP':s.get('clusterIP'),'ports':s.get('ports'),'containers':[{'name':c['name'],'image':c['image']} for c in s.get('containers',[])]})
    out['queries'].append(row)
out['finished_at_kst']=now();print(json.dumps(out))
