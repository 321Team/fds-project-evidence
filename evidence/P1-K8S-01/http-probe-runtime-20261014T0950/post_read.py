from pathlib import Path
import importlib.util,concurrent.futures
R=Path(__file__).resolve().parent;W=R.parent.parent
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
journal='''import json,subprocess,datetime,socket
cmd=['/usr/bin/journalctl','-u','kubelet','--since','2026-10-14 00:45:00 UTC','--no-pager','-o','short-iso-precise','--grep=e349b045-870f-4061-a677-3007efe479e9|fds-engine-65479b5bf-4gfgq']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=8)
print(json.dumps({'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
'''
jobs=[('http-recovery','10.1.93.107',(R/'http_recovery.py').read_bytes(),90),('final-app-state','10.1.93.102',(R/'app-state/collector.py').read_bytes(),90),('final-target-http','10.1.93.107',(R/'target-http/collector.py').read_bytes(),90),('kubelet-journal-utc','10.1.93.107',journal,90)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 fs=[pool.submit(t.run,n,ip,source,timeout) for n,ip,source,timeout in jobs]
 for f in fs:f.result()
