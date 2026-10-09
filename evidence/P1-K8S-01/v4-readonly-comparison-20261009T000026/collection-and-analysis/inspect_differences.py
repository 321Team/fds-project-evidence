import base64,hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'local-deps'));import yaml
folder=sorted((R/'private').glob('k8s-readonly-*'))[-1]
data=json.loads((folder/'k8s-control01.stdout.json').read_bytes())
live={}
for q in data['queries']:
    if q['command'][0]=='kubectl' and q['rc']==0:
        for x in json.loads(q['stdout']).get('items',[]):
            if 'kind' in x: live[(x['kind'],x['metadata']['name'])]=x
def diff(a,b,p='spec'):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b:out.append({'path':p+'.'+k,'expected':a.get(k,'<absent>'),'observed':b.get(k,'<absent>')})
            else:out+=diff(a[k],b[k],p+'.'+k)
        return out
    if a!=b:return [{'path':p,'expected':a,'observed':b}]
    return []
result=[]
for f in data['files']:
    if 'content_base64' not in f or '/gnp/' not in f['path']:continue
    x=yaml.safe_load(base64.b64decode(f['content_base64']));key=x['kind'],x['metadata']['name'];d=diff(x['spec'],live[key]['spec']);result.append({'kind':key[0],'name':key[1],'differences':d})
(folder/'POLICY_DIFF.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
for x in result:print(json.dumps(x,ensure_ascii=False))
repo=R.parent/'sec19-code-fix'
ref=subprocess.check_output(['git','-C',str(repo),'rev-parse','origin/main'],text=True).strip()
reference=json.loads((R/'references/approved-v4.json').read_text())
current={'commit':ref,'files':[]}
for row in reference['files']:
    b=subprocess.check_output(['git','-C',str(repo),'show',ref+':'+row['source_path']])
    current['files'].append({'source_path':row['source_path'],'deployed_path':row['deployed_path'],'sha256':hashlib.sha256(b).hexdigest()})
(folder/'CURRENT_SOURCE_HASHES.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
print('current source',ref)
for f in current['files']:print(f['source_path'],f['sha256'])
