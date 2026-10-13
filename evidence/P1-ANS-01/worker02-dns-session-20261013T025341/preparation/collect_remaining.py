from pathlib import Path
import sys
from read_transport import run
P=Path(__file__).resolve().parent
kind=sys.argv[1]
if kind=='cluster':
 source=(P.parent/'p1-oid02-supply-20261013/runtime/cluster-final/collector.py').read_text(encoding='utf-8')
 r=run('cluster-before','10.1.93.102',source,timeout=60)
elif kind=='network':
 source='''import datetime,hashlib,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'scope':'read only non-DNS preservation baseline','commands':[]}
queries=[['nmcli','--get-values','connection.uuid,connection.interface-name,ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.routes,ipv4.route-metric,ipv4.never-default,ipv6.method,ipv6.addresses,ipv6.gateway,ipv6.routes','connection','show','fds-k8s-worker02'],['ip','-j','route','show'],['ip','-j','-4','address','show','ens160'],['systemctl','show','NetworkManager','kubelet','containerd','--property=Id,MainPID,ActiveState,ActiveEnterTimestampMonotonic']]
try:
 for argv in queries:
  p=subprocess.run(argv,capture_output=True,timeout=10);out['commands'].append({'argv':argv,'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()});assert p.returncode==0
 out['status']='PRESERVATION_BASELINE_COLLECTED'
except Exception as e:out.update(status='STOP',error=type(e).__name__+':'+str(e))
print(json.dumps(out));raise SystemExit(0 if out['status']=='PRESERVATION_BASELINE_COLLECTED' else 2)
'''
 r=run('worker02-network-before','10.1.93.107',source,timeout=60)
else:raise SystemExit('unknown step')
raise SystemExit(0 if r['rc']==0 else 2)
