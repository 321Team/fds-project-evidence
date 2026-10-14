from pathlib import Path
import concurrent.futures, importlib.util, json, datetime
ROOT=Path(__file__).resolve().parent
WS=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('transport',WS/'deliverables/p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=ROOT
old=WS/'deliverables/phase1-probe-app-20261014-0740'
ha=WS/'deliverables/phase1-ha-followup-20261013-2343'
jobs=[('app-state','10.1.93.102',WS/'deliverables/phase1-deploy-preparation-20261013/app_state_read.py',True),('cluster','10.1.93.102',ha/'current-cluster/collector.py',True),('edge','10.1.93.50',ha/'current-edge/collector.py',False),('mon','10.1.93.102',old/'mon/collector.py',True),('process','10.1.93.107',WS/'deliverables/phase1-probe-app-20261014-0221/process_read.py',True),('event-baseline','10.1.93.102',old/'probe_events_read.py',True),('target-http','10.1.93.107',old/'probe_http_read.py',True)]
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
 fs=[pool.submit(t.run,n,ip,p.read_bytes(),90,root) for n,ip,p,root in jobs]
 for f in fs: f.result()
