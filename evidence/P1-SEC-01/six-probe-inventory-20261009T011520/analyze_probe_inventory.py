import hashlib,json,pathlib,sys
source=pathlib.Path(sys.argv[1]); data=json.loads(source.read_bytes())
qs=data['queries']; assert len(qs)==18 and all(q['rc']==0 for q in qs)
pods=[p for q in qs if q['path'].endswith('/pods') for p in q['items']]
slices=[p for q in qs if q['path'].endswith('/endpointslices') for p in q['items']]
controllers=[(q['path'].rsplit('/',1)[-1],p) for q in qs if q['path'].rsplit('/',1)[-1] in ('deployments','daemonsets','statefulsets') for p in q['items']]
rows=[]
for kind,c in controllers:
    ns=c['metadata']['namespace']; name=c['metadata']['name']; selector=c['spec']['selector']
    assert not selector.get('matchExpressions'), 'selector expressions require explicit analysis'
    labels=selector.get('matchLabels',{}); assert labels
    matched=[p for p in pods if p['metadata']['namespace']==ns and all(p['metadata']['labels'].get(k)==v for k,v in labels.items())]
    containers=c['spec']['template']['spec']['containers']
    pod_results=[]
    for p in matched:
        probes_match=all(all(pc.get(k)==tc.get(k) for k in ('startupProbe','readinessProbe','livenessProbe')) for tc in containers for pc in p['spec']['containers'] if pc['name']==tc['name'])
        assert {v['name'] for v in containers}=={v['name'] for v in p['spec']['containers']}
        endpoints=[{'slice':s['metadata']['name'],'service':s['metadata']['labels'].get('kubernetes.io/service-name'),'conditions':e['conditions']} for s in slices for e in s['endpoints'] if (e.get('targetRef') or {}).get('uid')==p['metadata']['uid']]
        pod_results.append({'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec']['nodeName'],'ready':[x.get('status') for x in p['status']['conditions'] if x['type']=='Ready'],'containers':p['status']['containers'],'probes_equal_controller':probes_match,'endpoints':endpoints})
    rows.append({'namespace':ns,'name':name,'kind':kind,'controller_uid':c['metadata']['uid'],'generation':c['metadata']['generation'],'observedGeneration':c['status']['observedGeneration'],'hostNetwork':c['spec']['template']['spec']['hostNetwork'],'containers':containers,'pods':pod_results})
result={'schema':'fds.six-probe-analysis.v1','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'started_at_kst':data['started_at_kst'],'finished_at_kst':data['finished_at_kst'],'query_count':len(qs),'workload_count':len(rows),'pod_count':len(pods),'workloads':rows,'interpretation':'API projection snapshot only. No new fault/recovery, direct health request or AC acceptance.'}
print(json.dumps(result,ensure_ascii=False,indent=2))
