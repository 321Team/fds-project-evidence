from pathlib import Path
import json,sys
from read_transport import run
from controller_transport import run as controller_run
R=Path(__file__).resolve().parent;P=R.parent
kind,label=sys.argv[1:]
assert label in ['before','after-apply','after-reapply','after-rollback','final']
sources={'worker':'worker02-fresh-read','network':'worker02-network-before','cluster':'cluster-before','controller':'controller-fresh-read'}
assert kind in sources
source=(P/sources[kind]/'collector.py').read_text(encoding='utf-8')
name=kind+'-'+label
r=controller_run(name,source,115) if kind=='controller' else run(name,'10.1.93.102' if kind=='cluster' else '10.1.93.107',source,90)
assert r['rc']==0,'READ_FAILED'
d=json.loads((R/name/'stdout.json').read_bytes())
if kind=='worker':
 p=json.loads((P/'EXECUTION_INPUT.json').read_bytes());assert d['success'] and d['boot']==p['boot'] and d['interface']==p['interface'] and d['connection']==p['connection']
 assert d['commands'][2]['stdout']=='10.1.93.52,10.1.93.53\nfds.internal\nyes\n'
 assert d['resolv_conf_selected']==['search fds.internal','nameserver 10.1.93.52','nameserver 10.1.93.53']
 assert d['commands'][4]['stdout']=='active\nactive\nactive\n' and d['commands'][5]['stdout'].strip()=='Enforcing'
elif kind=='cluster':
 assert d['status']=='CLUSTER_BINDING_VERIFIED'
 if label!='before':
  b=json.loads((R/'cluster-before/stdout.json').read_bytes())
  for k in ['nodes','deployments','pods']:assert d[k]==b[k],'CLUSTER_DRIFT:'+k
elif kind=='network':
 assert d['status']=='PRESERVATION_BASELINE_COLLECTED'
 if label!='before':
  b=json.loads((R/'network-before/stdout.json').read_bytes())
  assert [x['stdout'] for x in d['commands']]==[x['stdout'] for x in b['commands']],'NETWORK_OR_SERVICE_DRIFT'
else:assert d['status']=='PRECHECK_VERIFIED'
print('OBSERVATION_VERIFIED '+kind+' '+label)
