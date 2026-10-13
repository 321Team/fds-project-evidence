"""Fixed host/phase dispatcher, no automatic retries or advance to next host."""
from pathlib import Path
import base64,hashlib,json,sys
from read_transport import run
P=Path(__file__).resolve().parent;OLD=P.parent/'p1-redistribution-20261013'
phase,host=sys.argv[1:];assert phase in ['prepare','apply']
addresses={'k8s-control01':'10.1.93.102','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
assert host in addresses
raw=(P/'INPUT.json').read_bytes();plan=json.loads(raw)
assert plan['approved_source']=='b4303f2df512a8791d2421203cf159567d076b2a'
assert plan['replacement_count']==17 and plan['preserve_count']==28
request={'phase':phase,'host':host,'input_sha256':hashlib.sha256(raw).hexdigest(),'files':[r for r in plan['files'] if r['host']==host],'supply':{}}
for row in plan['supply']:
 content=(OLD/'k8s-supply'/row['file']).read_bytes();assert hashlib.sha256(content).hexdigest()==row['sha256'] and len(content)==row['size']
 compile(content,row['file'],'exec')
 request['supply'][row['file']]={'content':base64.b64encode(content).decode(),'sha256':row['sha256']}
if phase=='apply':
 ready=json.loads((P/(host+'-prepare')/'stdout.json').read_bytes())
 assert ready['status']=='BACKUP_RESTORE_AND_CANDIDATE_VERIFIED'
 request['prepared_sha256']=ready['prepared_sha256']
 if host!='k8s-control01':
  first=json.loads((P/'k8s-control01-apply/stdout.json').read_bytes());assert first['status']=='APPLIED_AND_VERIFIED'
source=(P/'file_step.remote.py').read_text(encoding='utf-8').replace('__REQUEST__',repr(request))
compile(source,'fixed_file_step','exec');receipt=run(host+'-'+phase,addresses[host],source,timeout=100)
raise SystemExit(0 if receipt['rc']==0 else 2)
