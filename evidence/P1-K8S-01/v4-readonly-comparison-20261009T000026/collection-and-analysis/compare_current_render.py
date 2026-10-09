import base64,difflib,hashlib,json,pathlib,runpy,sys
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'local-deps'))
folder=sorted((R/'private').glob('k8s-readonly-*'))[-1]
data=json.loads((folder/'k8s-control01.stdout.json').read_bytes())
config=next(f for f in data['files'] if f['path']=='/root/generated-gate2-attempt01/config.lock.json')
raw=base64.b64decode(config['content_base64']);assert hashlib.sha256(raw).hexdigest()==config['sha256']
c=json.loads(raw)
ns=runpy.run_path(str(R/'references/approved-v4/code/render.py'),run_name='readonly_local_comparison')
resources={}
for q in data['queries']:
    if q['command'][0]=='kubectl' and q['rc']==0:
        for x in json.loads(q['stdout']).get('items',[]):
            if 'kind' in x:resources[x['kind'],x['metadata']['name']]=x
report={'source_commit':'b4303f2df512a8791d2421203cf159567d076b2a','config_sha256':config['sha256'],'method':'local pure policies(config,node); no validate/render CLI, no live changes','results':[]}
def normalize_nets(x):
    if isinstance(x,dict):
        return {k: sorted(v) if k in ('nets','notNets') and isinstance(v,list) else normalize_nets(v) for k,v in x.items()}
    if isinstance(x,list):return [normalize_nets(v) for v in x]
    return x
for name in ns['ORDER']:
    g,h,f=ns['policies'](c,name)
    for definition in (g,h):
        key=definition['kind'],definition['metadata']['name'];observed=resources[key]['spec'].copy()
        # Record, rather than silently discard, API default tier.
        normalized=[]
        if 'tier' not in definition['spec'] and observed.get('tier')=='default':observed.pop('tier');normalized.append('observed spec.tier=default omitted for comparison')
        diff=''.join(difflib.unified_diff(json.dumps(definition['spec'],sort_keys=True,indent=2).splitlines(True),json.dumps(observed,sort_keys=True,indent=2).splitlines(True),fromfile='approved-source-reconstruction',tofile='current-live'))
        report['results'].append({'node':name,'kind':key[0],'name':key[1],'normalization':normalized,'equal':definition['spec']==observed,'equal_ignoring_nets_member_order':normalize_nets(definition['spec'])==normalize_nets(observed),'diff':diff})
    key='FelixConfiguration','node.'+name
    observed=resources.get(key,{}).get('spec',{})
    keys=list(f['spec'])
    projection={k:observed[k] for k in keys if k in observed}
    report['results'].append({'node':name,'kind':'FelixConfiguration','name':key[1],'compared_fields':keys,'equal':projection==f['spec'],'expected':f['spec'],'observed_projection':projection})
(folder/'APPROVED_RENDER_COMPARISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for x in report['results']:
    print(x['kind'],x['name'],'EQUAL' if x['equal'] else 'DIFFERENT')
    if not x['equal'] and 'diff' in x:print(x['diff'])
diffs=[]
for p in sorted((folder/'differing-sources').glob('*.py')):
    if p.name=='collector.py':continue
    good=R/'references/approved-v4/code'/p.name
    d=''.join(difflib.unified_diff(good.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='approved/'+p.name,tofile='deployed/'+p.name))
    diffs.append(d)
(folder/'DEPLOYED_SOURCE.diff').write_text('\n'.join(diffs),encoding='utf-8')
print('source_diff_lines',sum(len(d.splitlines()) for d in diffs))
