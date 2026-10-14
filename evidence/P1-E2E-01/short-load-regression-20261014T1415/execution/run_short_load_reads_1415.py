from pathlib import Path
import concurrent.futures,importlib.util,json,sys
BASE=Path(__file__).resolve().parent;R=BASE/'phase1-short-load-window-20261014-1415'
phase=sys.argv[1];assert phase in ['preparation','before','after']+['during'+str(i) for i in range(1,13)]
spec=importlib.util.spec_from_file_location('transport',BASE/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=R
assert (R/'CONFIRMED_WINDOW.json').exists()
control=(BASE/'phase1-short-load-readiness-20261014-1300/control-readonly/collector.py').read_bytes()
edge=(BASE/'phase1-short-load-readiness-20261014-1300/edge-correct-route/collector.py').read_bytes()
mon=(R/'mon_collector.py').read_bytes()
for b in [control,edge,mon]:compile(b,'read-only','exec')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    fs=[pool.submit(t.run,phase+'-control','10.1.93.102',control,90),pool.submit(t.run,phase+'-mon','10.1.93.102',mon,110)]
    if phase in ['preparation','before','after']:fs.append(pool.submit(t.run,phase+'-edge','10.1.93.50',edge,70,False))
    receipts=[f.result() for f in fs]
assert all(x['rc']==0 for x in receipts)
print(json.dumps({'phase':phase,'receipts':len(receipts),'all_rc0':True}))
