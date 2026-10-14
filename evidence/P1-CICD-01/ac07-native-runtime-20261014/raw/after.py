import concurrent.futures, importlib.util, json
from pathlib import Path
O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('collect',O.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=O
key='/home/server01_ansible/.ssh/p1_ansible_ed25519';cpkey='/home/server01_ansible/.ssh/id_ed25519'
pre=json.loads((O/'native-preflight.stdout').read_bytes());run=json.loads((O/'native-execute.stdout').read_bytes())
tasks=[('app-after','10.1.93.102','svc_ansible',key,True,O/'app-before/collector.py',[]),('runner-after','10.250.10.20','server01_cicd-runner',key,False,O/'runner-before/collector.py',[]),('rbac-after','10.1.93.102','svc_ansible',key,True,O/'read_rbac.py',[]),('cleanup-cp1','10.1.93.102','server02',cpkey,False,O/'read_cleanup.py',[pre['cp1']['workdir'],run['cp1']['workdir']]),('cleanup-runner','10.250.10.20','server01_cicd-runner',key,False,O/'read_cleanup.py',[pre['runner']['workdir'],run['runner']['workdir']])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(m.remote,tasks))
(O/'AFTER_COLLECTION_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results))
assert all(x['rc']==0 and x['stderr_bytes']==0 for x in results)
