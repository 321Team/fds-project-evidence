import hashlib,json,pathlib,shutil,subprocess,tarfile
r=pathlib.Path(__file__).resolve().parent;out=r/'private/consumer-supply-37859961937';out.mkdir(parents=True,exist_ok=False)
b=out/'bundle';b.mkdir();hashes={}
def put(path,raw):
    p=b/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);hashes[path]=hashlib.sha256(raw).hexdigest()
consumer=r/'cicd-handoff';csha='04e49811e46ffcd3f35183c2cfb9493901f84dc5';app=r/'app-metrics-isolation';asha='affbc69beef9967f7977d09a6fec14f7fb6c0e94'
files=['tools/delivery/offline_supply_v3.py','tools/delivery/offline_supply.py','tools/trivy/oci_archive.py','tools/trivy/prepare_db.py','tools/trivy/verify_runner.py']
for name in files:put('consumer/'+name,subprocess.check_output(['git','show',csha+':'+name],cwd=consumer))
m=json.loads((r/'private/app-supply-37859961937/SUPPLY_MANIFEST.json').read_bytes())
paths=list(m['requirements'])+['ci/apko/'+n for n in m['apko_inputs']]+['transaction-api/Dockerfile','fds-engine/Dockerfile']
for name in paths:put('app-source/'+name,subprocess.check_output(['git','show',asha+':'+name],cwd=app))
put('verify_consumer_supply.py',(r/'verify_consumer_supply.py').read_bytes())
(b/'INPUT_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
with tarfile.open(out/'input.tar','w') as t:
    for p in sorted(b.rglob('*')):
        if p.is_file():t.add(p,arcname=p.relative_to(b).as_posix(),recursive=False)
print(out,'source/tool inputs',len(hashes))
