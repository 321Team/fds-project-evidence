import datetime as dt,hashlib,json,os,pwd,socket,subprocess
assert socket.gethostname()=='k8s-control01' and pwd.getpwuid(os.getuid()).pw_name=='server02'
k=['/usr/bin/kubectl','--kubeconfig=/home/server02/.kube/config','--server=https://10.1.93.109:6443','--certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem','--request-timeout=6s']
out={'queries':[],'pods':[],'mutation':False,'host':socket.gethostname()}
def get(path):
 p=subprocess.run(k+['get','--raw='+path],capture_output=True,timeout=8);assert p.returncode==0
 out['queries'].append({'path':path,'rc':p.returncode,'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'raw_sha256':hashlib.sha256(p.stdout).hexdigest()});return json.loads(p.stdout)
for ns in ['fds-app','monitoring-api']:
 for p in get('/api/v1/namespaces/'+ns+'/pods')['items']:
  if ns=='monitoring-api' and p['metadata'].get('labels',{}).get('app')!='prometheus':continue
  out['pods'].append({'namespace':ns,'name':p['metadata']['name'],'uid':p['metadata']['uid'],'labels':p['metadata'].get('labels',{}),'node':p['spec'].get('nodeName'),'ip':p['status'].get('podIP'),'deletionTimestamp':p['metadata'].get('deletionTimestamp'),'containers':p['status'].get('containerStatuses',[])})
out['services']=[{'name':s['metadata']['name'],'uid':s['metadata']['uid'],'spec':s['spec']} for s in get('/api/v1/namespaces/fds-app/services')['items']]
out['endpointslices']=[{'name':s['metadata']['name'],'labels':s['metadata'].get('labels'),'ports':s.get('ports'),'endpoints':s.get('endpoints')} for s in get('/apis/discovery.k8s.io/v1/namespaces/fds-app/endpointslices')['items']]
print(json.dumps(out,sort_keys=True))
