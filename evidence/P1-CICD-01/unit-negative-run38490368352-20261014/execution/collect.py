"""Bounded read-only remote collection; new receipts only on the workstation."""
import importlib.util, json, sys
from pathlib import Path
OUT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('readonly', OUT.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.OUT = OUT
key = '/home/server01_ansible/.ssh/p1_ansible_ed25519'
mode = sys.argv[1]
tasks = []
if mode in ('pre', 'post'):
    tasks = [(mode+'-app', '10.1.93.102', 'svc_ansible', key, True, OUT.parent/'phase1-deploy-preparation-20261013/app_state_read.py', []),
             (mode+'-runner', '10.250.10.20', 'server01_cicd-runner', key, False, OUT.parent/'phase1-push-followup-20261013/runner_push_read.py', [])]
elif mode == 'builder':
    tasks = [('builder-read', '10.250.10.20', 'server01_cicd-runner', key, False, OUT/'builder_read.py', [])]
elif mode == 'fresh':
    tasks = [(sys.argv[2], '10.250.10.20', 'server01_cicd-runner', key, False, OUT.parent/'phase1-tbs-id-fix-20261013-2110/runner_preflight.py', [])]
elif mode == 'custom':
    tasks = [(sys.argv[2], '10.250.10.20', 'server01_cicd-runner', key, False, OUT/sys.argv[3], sys.argv[4:])]
else: raise SystemExit('Unsupported mode')
with m.concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for result in pool.map(m.remote, tasks):
        print(json.dumps(result), flush=True)
