from pathlib import Path
import concurrent.futures,importlib.util,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
assert json.loads((OUT/'api-recovery/stdout.json').read_bytes())['status']=='READY_MON_STABLE'
tasks=[('final-cluster','102',(ROOT/'current-cluster/collector.py').read_bytes(),True),('final-app-state','102',(ROOT.parent/'phase1-deploy-preparation-20261013/app_state_read.py').read_bytes(),True),('final-edge','50',(ROOT/'current-edge/collector.py').read_bytes(),False),('final-mon','102',(ROOT/'current-mon/collector.py').read_bytes(),True)]
def run(task):
 name,ip,source,root=task;return t.run(name,'10.1.93.'+ip,source,90,root)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,tasks))
assert all(r['rc']==0 for r in results)
