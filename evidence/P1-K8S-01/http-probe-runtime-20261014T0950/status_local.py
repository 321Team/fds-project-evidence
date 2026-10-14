from pathlib import Path
import json
R=Path(__file__).resolve().parent
for fn in ('observer','worker-http'):
 rows=[json.loads(x) for x in (R/(fn+'.jsonl')).read_bytes().splitlines()]
 if fn=='worker-http':print(json.dumps({'observer':fn,'latest':rows[-1]},ensure_ascii=False));continue
 x=rows[-1];p=[p for p in x['queries']['pods']['items'] if p['uid']=='e349b045-870f-4061-a677-3007efe479e9'];e=[(s['labels'].get('kubernetes.io/service-name'),ep['conditions']) for s in x['queries']['endpoints']['items'] for ep in s['endpoints'] if ep.get('targetRef',{}).get('uid')=='e349b045-870f-4061-a677-3007efe479e9']
 print(json.dumps({'observer':fn,'utc':x['utc'],'samples':len(rows),'observation_errors':sum('error' in r for r in rows),'other_unhealthy':sum(not r.get('other_workloads_healthy') for r in rows),'nodes_unhealthy':sum(not r.get('nodes_healthy') for r in rows),'target':[{'uid':p['uid'],'containers':p['containers']} for p in p],'endpoints':e,'events':[{k:e.get(k) for k in ('reason','message','count','firstTimestamp','lastTimestamp')} for e in x['queries']['events']['items']]},ensure_ascii=False))
