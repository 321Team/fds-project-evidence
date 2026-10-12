import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
import hashlib
ses=Path('/var/lib/fds-change/if06b-20261012T2220-mon02');kc=['/usr/bin/kubectl', '--kubeconfig=/etc/kubernetes/admin.conf', '--request-timeout=10s'];phase='post'
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
