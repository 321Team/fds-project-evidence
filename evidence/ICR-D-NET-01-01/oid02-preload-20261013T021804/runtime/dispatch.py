from pathlib import Path
import datetime,hashlib,json,sys
from read_transport import run
R=Path(__file__).resolve().parent;P=R.parent
action,host,*image=sys.argv[1:];plan=json.loads((P/'EXECUTION_INPUT.json').read_bytes());supply=json.loads((P/'OBSERVED_SUPPLY.json').read_bytes())
addresses={'k8s-control01':'10.1.93.102','k8s-control02':'10.1.93.103','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
assert action in ['precheck','stage','export','import','final'] and host in addresses
cfg={'action':action,'host':host,'plan':plan,'supply':supply,'boot':json.loads((P/(host+'-snapshotter/stdout.json')).read_bytes())['boot'],'effective_sha':json.loads((P/(host+'-effective-config/stdout.json')).read_bytes())['commands'][0]['stdout_sha256']}
names=['kube-controllers','coredns'] if action=='final' or host=='k8s-control01' or 'worker' in host else ['kube-controllers']
if image:assert len(image)==1 and image[0] in names;names=image
cfg['jobs']=[x for x in plan['source_jobs'] if x['image'] in names]
if action=='final':cfg['initial_refs']=json.loads((R/('precheck-'+host)/'stdout.json').read_bytes())['refs_before']
if action=='stage':cfg['files']={n:p.read_text(encoding='utf-8') for n,p in [('OBSERVED_SUPPLY.json',P/'OBSERVED_SUPPLY.json'),('verify_archive.py',P/'verify_archive.py'),('receive.py',R/'receive.py'),('USER_AUTHORIZATION.json',R/'USER_AUTHORIZATION.json')]}
if action in ['stage','export','import']:
 a=json.loads((R/'USER_AUTHORIZATION.json').read_bytes());assert a['current_cache_adopted'] and a['console_target5_including_control02']
 marker=R/'RUNTIME_START.json'
 if not marker.exists():
  assert action=='stage' and host=='k8s-control01'
  marker.write_text(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
 assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(json.loads(marker.read_bytes())['at_utc'])).total_seconds()<1800,'WHOLE_RUNTIME_BUDGET'
if action=='import':cfg['archive_sha256']=json.loads((R/('export-k8s-control01-'+names[0])/'stdout.json').read_bytes())['archive']['archive_sha256']
source='CFG='+repr(cfg)+'\n'+(R/'remote_step.py').read_text(encoding='utf-8');compile(source,'remote_step','exec')
r=run(action+'-'+host+('-'+names[0] if image else ''),addresses[host],source,timeout=280 if action=='import' else 180 if action=='export' else 65)
raise SystemExit(0 if r['rc']==0 else 2)
