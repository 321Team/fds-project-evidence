from pathlib import Path
import importlib.util,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
name,ip,source,root,timeout=sys.argv[1:]
code=Path(source).read_bytes();compile(code,source,'exec')
r=t.run(name,'10.1.93.'+ip,code,int(timeout),root=='root')
if r['rc']!=0:raise SystemExit(1)
