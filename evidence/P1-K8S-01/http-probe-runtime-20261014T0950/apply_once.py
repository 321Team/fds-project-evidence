"""Invoke the reviewed controller once through the existing strict SSH route."""
from pathlib import Path
import datetime,json,importlib.util
R=Path(__file__).resolve().parent;W=R.parent.parent
assert json.loads((R/'stage-reviewed-source/receipt.json').read_bytes())['rc']==0
for file in ('observer.jsonl','worker-http.jsonl'):
 x=json.loads((R/file).read_bytes().splitlines()[-1]);assert datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(x['utc'])<datetime.timedelta(seconds=10)
 if file=='observer.jsonl':assert x['other_workloads_healthy'] and x['nodes_healthy'] and 'error' not in x
 else:assert all(r['code']==200 for r in x['http'].values()) and x['original_pid']['start_ticks']=='19229699' and x['original_pid']['state'] not in ('T','t','Z','X')
cmd=['/usr/bin/python3','-B','-I','/var/tmp/p1-http-probe-source-20261014-0945/engine_stop.py','apply','/var/tmp/p1-http-probe-source-20261014-0945/observed-binding.json','--source-sha256','8b9fe37dd0bcdbd09e0c7d5e7fb41eaa9e25d47fb56223bbab6273081251cc32','--start','2026-10-14T09:45:00+09:00','--latest-start','2026-10-14T09:55:00+09:00','--end','2026-10-14T10:20:00+09:00','--output','/var/tmp/p1-http-probe-20261014-0945']
source='import subprocess,sys\np=subprocess.run('+repr(cmd)+')\nsys.exit(p.returncode)\n'
spec=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=R
t.run('apply-once','10.1.93.107',source,230)
