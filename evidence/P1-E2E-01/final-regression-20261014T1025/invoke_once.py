"""One native invocation of the existing reviewed rg.py; no automatic rerun."""
from pathlib import Path
import datetime as dt,importlib.util,json
R=Path(__file__).resolve().parent;W=R.parent.parent
entry=json.loads((R/'ENTRY_VALIDATED.json').read_bytes());now=dt.datetime.now(dt.timezone.utc)
assert entry['status']=='ENTRY_CHECKS_PASS'
assert dt.datetime.fromisoformat(entry['window_start'])<=now<=dt.datetime.fromisoformat(entry['latest_start'])
assert dt.timedelta()<=now-dt.datetime.fromisoformat(entry['at_kst'])<=dt.timedelta(minutes=2)
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
cmd=['/usr/bin/python3','-B','-I','/home/svc_ansible/p1-app-20261014-1025/supply/rg.py','run','/home/svc_ansible/p1-app-20261014-1025/results']
source='import os,subprocess,sys\nos.umask(0o077)\np=subprocess.run('+repr(cmd)+')\nsys.exit(p.returncode)\n'
t.run('app-run-once','10.1.93.50',source,360,False)
