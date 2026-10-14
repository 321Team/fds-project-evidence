"""Fresh read-only entry checks. REVIEW=NOT PERFORMED (Pre-check)."""
from pathlib import Path
import importlib.util, concurrent.futures, json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
tasks=[('current-cluster','102',True),('current-edge','50',False),('current-mon','102',True),('current-capacity','102',True),('edge-identity','50',False),('cache-worker01','105',True),('cache-worker02','107',True),('cache-worker03','108',True)]
def collect(task):
 name,ip,root=task
 source=(ROOT/name/'collector.py').read_bytes()
 compile(source,name,'exec')
 return t.run(name,'10.1.93.'+ip,source,timeout=90,as_root=root)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(collect,tasks))
(OUT/'ENTRY_RECEIPTS.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
assert all(r['rc']==0 for r in results)
