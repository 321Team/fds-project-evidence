import hashlib,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'deps'))
import yaml
r=pathlib.Path(__file__).resolve().parent
repo=r.parent/'sec19-backup-evidence'
current=json.loads((r/'mon-config.json').read_text(encoding='utf8'))
wanted={q['name']:q['data'] for q in current['queries'] if 'name' in q}
out=[]
for p in (repo/'evidence/P1-MON-01').rglob('*'):
    if p.suffix not in ('.yaml','.yml') or p.stat().st_size>800000: continue
    try:
        for d in yaml.safe_load_all(p.read_text(encoding='utf8')):
            if not isinstance(d,dict): continue
            name=d.get('metadata',{}).get('name')
            if name not in wanted or d.get('kind')!='ConfigMap': continue
            for key,value in d.get('data',{}).items():
                if key not in wanted[name]: continue
                sha=hashlib.sha256(value.encode()).hexdigest()
                entry={'path':p.relative_to(repo).as_posix(),'name':name,'key':key,'historical_data_sha256':sha,
                       'current_data_sha256':wanted[name][key]['sha256'],'equal':sha==wanted[name][key]['sha256']}
                parsed=yaml.safe_load(value)
                if isinstance(parsed,dict) and 'groups' in parsed:
                    entry['historical_rules']=[{k:v for k,v in rule.items() if k in ('alert','record','expr','for')} for group in parsed['groups'] for rule in group['rules']]
                out.append(entry)
    except (ValueError,yaml.YAMLError,UnicodeError): pass
(r/'historical-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
