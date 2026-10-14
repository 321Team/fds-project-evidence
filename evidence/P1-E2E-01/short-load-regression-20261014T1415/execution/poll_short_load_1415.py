from pathlib import Path
import importlib.util,json,sys
base=Path(__file__).resolve().parent
r=base/'phase1-short-load-window-20261014-1415'
name=sys.argv[1]
assert name.startswith('progress-') and name[9:].isdigit()
spec=importlib.util.spec_from_file_location('transport',base/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=r
receipt=t.run(name,'10.1.93.50',(r/'edge_progress.py').read_bytes(),70,False)
assert receipt['rc']==0
data=json.loads((r/name/'stdout.json').read_bytes())
print(json.dumps({k:v for k,v in data.items() if k not in ['process.json','regression-attempt.json']},ensure_ascii=False))
