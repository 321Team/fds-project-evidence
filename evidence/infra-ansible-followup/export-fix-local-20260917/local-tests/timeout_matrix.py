#!/usr/bin/env python3
"""Test-only readiness instrumentation. Production Controller is unchanged."""
import concurrent.futures
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from offline_guard import install
from prepare_and_run import verify

def run(item):
    mode,index=item
    install()
    sys.path.insert(0,str(BASE/'candidate/tools/ansible-runner'))
    import runner
    folder=BASE/'results/timeouts'/f'{mode}-{index:03}'
    (folder/'private').mkdir(parents=True)
    (folder/'evidence').mkdir()
    controller=runner.Controller(folder,'prepare','SYNTHETIC_TIMEOUT_TEST')
    delay=(index%5)*0.1 if mode=='readiness' else 0.4 if mode=='legacy-delayed' else 0
    silent=mode=='silent'
    source=f'import sys,time; time.sleep({delay}); '+(
        '' if silent else 'print("before timeout",file=sys.stderr,flush=True); ')+ 'time.sleep(10)'
    real_popen=runner.subprocess.Popen
    spawn_start=time.monotonic()
    observed_ready=[]
    def ready_popen(*args,**kwargs):
        process=real_popen(*args,**kwargs)
        expiry=time.monotonic()+5
        path=folder/'private/podman-info.stderr.log'
        while time.monotonic()<expiry:
            if path.exists() and b'before timeout' in path.read_bytes():
                observed_ready.append(round(time.monotonic()-spawn_start,6))
                return process
            if process.poll() is not None:
                break
            time.sleep(0.002)
        if process.poll() is None:
            process.terminate();process.wait(timeout=5)
        raise RuntimeError('TEST_CHILD_READINESS_NOT_OBSERVED')
    raised=None
    with redirect_stdout(io.StringIO()):
        try:
            if mode=='readiness':
                with patch.object(runner.subprocess,'Popen',ready_popen):
                    controller.command('podman-info',[sys.executable,'-I','-B','-c',source],0.03)
            else:
                controller.command('podman-info',[sys.executable,'-I','-B','-c',source],
                    0.3 if mode=='legacy-delayed' else 0.03)
        except RuntimeError as exc:
            raised=str(exc)
    record=json.loads((folder/'evidence/podman-info.prepare.json').read_text())
    stderr=(folder/'evidence/podman-info.prepare.stderr.log').read_bytes()
    timed=record['timed_out'] is True and type(record['rc']) is int and record['rc']!=0
    marker=b'before timeout' in stderr
    passed=timed and (marker if mode=='readiness' else not marker)
    return {'case':mode,'iteration':index,'synthetic_start_delay_seconds':delay,
        'readiness_seconds':observed_ready[0] if observed_ready else None,
        'seconds':round(time.monotonic()-spawn_start,6),'timed_out':record['timed_out'],
        'rc':record['rc'],'marker_observed':marker,'exception':raised,
        'expected_behavior_confirmed':passed,
        'legacy_log_assertion_would_pass':marker if mode=='legacy-delayed' else None}

if __name__=='__main__':
    work=[('readiness',i) for i in range(100)]+[('silent',i) for i in range(100)]+[
        ('legacy-delayed',i) for i in range(10)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(run,work))
    summary={kind:{'count':sum(r['case']==kind for r in rows),
        'expected_behavior_confirmed':sum(r['case']==kind and r['expected_behavior_confirmed'] for r in rows)}
        for kind in ['readiness','silent','legacy-delayed']}
    verify()
    (BASE/'results/TIMEOUT_MATRIX.json').write_text(json.dumps({
        'scope':'real local Python children; no Podman/VM; readiness wrapper modifies test clock boundary only',
        'summary':summary,'rows':rows,'source_unchanged':True},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

