import base64,hashlib,json,pathlib,re,sys
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'local-deps'))
import yaml

SENSITIVE=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|(?:postgres(?:ql)?|https?)://[^\s"/]+:[^\s"/@]+@')
def scan(raw,label):
    if SENSITIVE.search(raw): raise ValueError('STOP: sensitive pattern: '+label)
    try: obj=json.loads(raw)
    except (ValueError,UnicodeDecodeError):return
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('name'),str) and re.search(r'password|secret|token|database_url',x['name'],re.I) and x.get('value'):
                raise ValueError('STOP: nonempty sensitive env value: '+label)
            for k,v in x.items():
                if k=='content_base64': scan(base64.b64decode(v,validate=True),label+' decoded payload')
                else: walk(v)
        elif isinstance(x,list):
            for i in x:walk(i)
    walk(obj)

def latest(prefix):
    dirs=sorted((R/'private').glob(prefix+'-*'));assert dirs
    return dirs[-1]

def main():
    app=latest('app-receipt');k8s=latest('k8s-readonly')
    for folder in (app,k8s):
        for p in folder.rglob('*'):
            if p.is_file():scan(p.read_bytes(),str(p.relative_to(folder)))
    ref=json.loads((R/'references/approved-v4.json').read_text())
    expected={f['deployed_path']:f for f in ref['files']}
    report={'source_commit':ref['source_commit'],'scope':'current read-only snapshot, not historical approval or runtime behavior','node_code_comparison':[],'rendered_policy_comparison':[]}
    for file in sorted(k8s.glob('*.stdout.json')):
        data=json.loads(file.read_bytes()); bypath={x['path']:x for x in data['files']}
        rows=[]
        for path,definition in expected.items():
            live=bypath.get(path,{})
            rows.append({'path':path,'expected_sha256':definition['sha256'],'observed_sha256':live.get('sha256'),'status':'MATCH' if live.get('sha256')==definition['sha256'] else 'DIFFERENT' if 'sha256' in live else 'NOT_AVAILABLE','error':live.get('error')})
        report['node_code_comparison'].append({'host':data['host'],'files':rows})
        if data['host']!='k8s-control01':continue
        apis={}
        for q in data['queries']:
            if q['rc']==0 and q['command'][0]=='kubectl':
                content=json.loads(q['stdout'])
                for x in content.get('items',[]):
                    apis[(x.get('kind'),x['metadata']['name'])]=x
        for f in data['files']:
            if 'content_base64' not in f or not f['path'].endswith(('.yaml','.json')) or f['path'].endswith('config.lock.json'):continue
            raw=base64.b64decode(f['content_base64']);assert hashlib.sha256(raw).hexdigest()==f['sha256']
            for definition in yaml.safe_load_all(raw):
                if not isinstance(definition,dict) or 'kind' not in definition:continue
                key=(definition['kind'],definition['metadata']['name']);live=apis.get(key)
                report['rendered_policy_comparison'].append({'rendered_path':f['path'],'kind':key[0],'name':key[1],'rendered_sha256':f['sha256'],'live_uid':live.get('metadata',{}).get('uid') if live else None,'status':'SPEC_EQUAL' if live and live.get('spec')==definition.get('spec') else 'SPEC_DIFFERENT' if live else 'LIVE_NOT_FOUND'})
    (k8s/'COMPARISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for host in report['node_code_comparison']:
        print(host['host'],{v:sum(x['status']==v for x in host['files']) for v in ('MATCH','DIFFERENT','NOT_AVAILABLE')})
    print('rendered_policies',len(report['rendered_policy_comparison']))
    for x in report['rendered_policy_comparison']:print(x['kind'],x['name'],x['status'])
    print('sensitive_pattern_scan=NO_MATCH; heuristic only')

if __name__=='__main__':main()
