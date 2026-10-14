from pathlib import Path
import base64,hashlib,importlib.util,json,re
BASE=Path(__file__).resolve().parent;R=BASE/'phase1-short-load-window-20261014-1415'
spec=importlib.util.spec_from_file_location('transport',BASE/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=R
assert t.run('edge-results','10.1.93.50',(R/'edge_collect_results.py').read_bytes(),90,False)['rc']==0
data=json.loads((R/'edge-results/stdout.json').read_bytes());dest=R/'edge-originals';dest.mkdir(exist_ok=False)
for f in data['files']:
    rel=Path(f['relative']);assert not rel.is_absolute() and '..' not in rel.parts
    raw=base64.b64decode(f['base64']);assert hashlib.sha256(raw).hexdigest()==f['sha256'] and len(raw)==f['size']
    target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
stages=(dest/'results/stages.log').read_text()
b=re.findall(r'^\S+ START B 20 rps 120 s ([0-9.]+)$',stages,re.M)
end=re.findall(r'^\S+ IDLE END ([0-9.]+) codes ',stages,re.M)
assert len(b)==1 and len(end)==1,'Incomplete run; preserve raw, do not claim complete observation range'
start=float(b[0])-60;finish=float(end[0])
source='START_EPOCH='+repr(start)+'\nEND_EPOCH='+repr(finish)+'\n'+(R/'control_collect_range.py').read_text()
compile(source,'post-range','exec')
assert t.run('control-range','10.1.93.102',source,160)['rc']==0
data=json.loads((R/'control-range/stdout.json').read_bytes());dest=R/'control-originals';dest.mkdir(exist_ok=False)
for f in data['files']:
    name=f['name'];assert Path(name).name==name
    raw=base64.b64decode(f['base64']);assert hashlib.sha256(raw).hexdigest()==f['sha256'] and len(raw)==f['size']
    (dest/name).write_bytes(raw)
print(json.dumps({'edge_files':len(list((R/'edge-originals').rglob('*'))),'range_start':start,'range_end':finish,'range_files':len(data['files']),'integrity':'verified'}))
