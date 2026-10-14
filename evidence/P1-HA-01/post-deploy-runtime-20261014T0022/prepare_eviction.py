"""Bind the approved single native Eviction to fresh post-W Pod identity."""
from pathlib import Path
import sys,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
app,snapshot=sys.argv[1:];assert app in ('fds-engine','transaction-api')
if app=='transaction-api':assert json.loads((OUT/'fds-engine-RECOVERY.json').read_bytes())['status']=='READY_MON_STABLE'
q={x['kind']:x['items'] for x in json.loads((OUT/snapshot/'stdout.json').read_bytes())['queries']}
b=json.loads((ROOT/'READINESS_BINDING.json').read_bytes());b.update(host=b['control_identity']['host'],boot=b['control_identity']['boot'],cluster_uid=b['cluster']['uid'])
for d in b['deployments']:d['images']=[{'image':d['image']}]
b['observed_pods']=[{'metadata':p['metadata']} for p in q['pods']]
rs={d['metadata']['name']:next(r['metadata']['uid'] for r in b['active_replica_sets'] if r['metadata']['ownerReferences'][0]['uid']==d['metadata']['uid']) for d in b['deployments']}
workers=['k8s-worker01','k8s-worker02','k8s-worker03'];counts={}
for name,r in rs.items():counts[name]={w:sum(p['node']==w and p['owners'][0]['uid']==r for p in q['pods']) for w in workers}
assert sorted(counts[app].values())==[0,1,2] and counts[app]['k8s-worker02']==0
if app=='transaction-api':assert list(counts['fds-engine'].values())==[1,1,1]
surplus=next(w for w,n in counts[app].items() if n==2)
original={p['metadata']['uid'] for p in json.loads((OUT/'app-state/stdout.json').read_bytes())['queries'][1]['items']}
candidates=[p for p in q['pods'] if p['node']==surplus and p['owners'][0]['uid']==rs[app]]
assert len(candidates)==2
target=next((p for p in candidates if p['metadata']['uid'] not in original),candidates[0])
template=(ROOT.parent/'p1-redistribution-20261013/evict_one.remote.py').read_text(encoding='utf-8')
template=template.replace('__BINDING__',repr(b)).replace('__APP__',repr(app)).replace('__EXPECTED_COUNTS__',repr(counts))
template=template.replace("choices=[p for p in app_pods[APP] if p['spec']['nodeName']=='k8s-worker02' and p['metadata']['uid'] in allowed]", "choices=[p for p in app_pods[APP] if p['spec']['nodeName']=="+repr(surplus)+" and p['metadata']['uid']=="+repr(target['metadata']['uid'])+" and p['metadata']['uid'] in allowed]")
template=template.replace("require(len(choices)>=2,'NO_BOUNDED_TARGET')", "require(len(choices)==1,'NO_BOUNDED_TARGET')")
guard=""" import pathlib
 path=pathlib.Path('/var/tmp/p1-ha-20261014-0015')
 require(not path.is_symlink() and path.stat().st_uid==0,'CONTROL_DIRECTORY')
 timeline=(path/'timeline.txt').read_text().splitlines()
 require(len(timeline)==5 and timeline[-1].startswith('end '),'W_NOT_ENDED')
 require(datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-13T16:01:00+00:00'),'RECOVERY_BUDGET')
 os.umask(0o077)
 with (path/(APP+'-eviction.json')).open('x') as f:json.dump(eviction,f);f.flush();os.fsync(f.fileno())
"""
template=template.replace(" argv=KC[:-1]+",guard+" argv=KC[:-1]+")
template=template.replace("'-f','-']", "'-f',str(path/(APP+'-eviction.json'))]")
template=template.replace("  p=subprocess.run(argv,input=json.dumps(eviction).encode(),capture_output=True,timeout=12)", "  p=subprocess.run(argv,capture_output=True,timeout=12)")
template=template.replace("out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(out))", "out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()\nwith (path/(APP+'-eviction-result.json')).open('x') as f:json.dump(out,f)\nprint(json.dumps(out))")
compile(template,app,'exec');(OUT/(app+'-evict.remote.py')).write_text(template,encoding='utf-8')
print(json.dumps({'app':app,'target':target['metadata'],'surplus_node':surplus,'counts':counts,'native_eviction_limit':1},indent=2))
