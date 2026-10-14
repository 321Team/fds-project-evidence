from pathlib import Path
import importlib.util,concurrent.futures
R=Path(__file__).resolve().parent;W=R.parent.parent
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
jobs=[('mon-stable','10.1.93.102',R/'mon_stable.py',210,True),('recovery-edge','10.1.93.50',R/'edge/collector.py',90,False)]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 fs=[pool.submit(t.run,n,ip,p.read_bytes(),timeout,root) for n,ip,p,timeout,root in jobs]
 for f in fs:f.result()
