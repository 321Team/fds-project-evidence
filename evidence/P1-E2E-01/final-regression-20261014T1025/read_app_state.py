"""Pure GET pre/post collection; no POST, DB writes or remote staging."""
from pathlib import Path
import concurrent.futures,importlib.util,sys
R=Path(__file__).resolve().parent;W=R.parent.parent
phase=sys.argv[1];assert phase in ('before','after')
old=W/'deliverables/phase1-probe-app-20261014-0945'
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
jobs=[(phase+'-app-state','10.1.93.102',(old/'app-state/collector.py').read_bytes(),True),(phase+'-cluster','10.1.93.102',(old/'cluster/collector.py').read_bytes(),True),(phase+'-mon','10.1.93.102',(old/'mon/collector.py').read_bytes(),True),(phase+'-edge','10.1.93.50',(old/'edge/collector.py').read_bytes(),False)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 fs=[pool.submit(t.run,n,ip,src,90,root) for n,ip,src,root in jobs]
 for f in fs:f.result()
