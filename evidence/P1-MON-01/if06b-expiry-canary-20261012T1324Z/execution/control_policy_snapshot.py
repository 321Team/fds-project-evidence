import sys
import control_runtime as r
phase=sys.argv[1];assert phase in ['pre','post']
body='''import hashlib
ses=Path(SES);kc=KC;phase=PHASE
res=ses/'results';aux=ses/'aux';py='/usr/bin/python3.12'
record=['env','IF06B_RESULTS='+str(res),'/bin/sh',str(aux/'tools/record.sh')]
def rec(name,argv):
 p=subprocess.run(record+[name]+argv,capture_output=True,text=True,timeout=20)
 assert p.returncode==0,'FAILED_'+name
 return (res/(name+'.out')).read_text()
base='/apis/crd.projectcalico.org/v1/'
objects={}
for key,kind,path,name in [('hep','HostEndpoint','hostendpoints','fds-k8s-k8s-worker03'),
                         ('hostgnp','GlobalNetworkPolicy','globalnetworkpolicies','fds-k8s-host-k8s-worker03')]:
 label='6-'+phase+'-'+key+'-get'
 raw=rec(label,kc+['get','--raw='+base+path+'/'+name])
 info=rec('6-'+phase+'-'+key+'-info',[py,'-B',str(aux/'tools/objinfo.py'),str(res/(label+'.out')),kind,name])
 objects[key]={'object':json.loads(raw),'info':info}
raw=rec('6-'+phase+'-gnp-all',kc+['get','--raw='+base+'globalnetworkpolicies'])
items=json.loads(raw)['items']
listing=[{'name':i['metadata']['name'],'uid':i['metadata']['uid'],'rv':i['metadata']['resourceVersion'],
          'order':i['spec'].get('order'),'selector':i['spec'].get('selector'),'spec':i['spec']} for i in sorted(items,key=lambda i:i['metadata']['name'])]
assert all(i['name']!='p1-mon-if06b-worker03-to-monitor01-canary' and i['order']!=90 for i in listing),'GNP_COLLISION'
assert objects['hostgnp']['object']['spec']['order']==100
print(json.dumps({'phase':phase,'objects':objects,'all_gnp':listing,'canary_present':False}))
'''.replace('Path(SES)','Path('+repr(r.SES)+')').replace('kc=KC','kc='+repr(r.KC)).replace('phase=PHASE','phase='+repr(phase))
r.run('control01-policy-'+phase,body)
