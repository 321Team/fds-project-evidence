#!/usr/bin/env python3
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
REPO=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'candidate'
FAMILY='proposal-faults' if REPO.name=='proposal' else 'faults'
sys.path.insert(0,str(BASE))
from prepare_and_run import environment,verify
sys.path.insert(0,str(BASE/'candidate/tools/ansible-runner'))
import common

def run(case):
    cp=subprocess.run([sys.executable,'-I','-B',str(BASE/'fault_child.py'),case,str(REPO)],
        env=environment(),capture_output=True,timeout=30)
    folder=BASE/'results'/FAMILY/case
    (folder/'stdout.log').write_bytes(cp.stdout);(folder/'stderr.log').write_bytes(cp.stderr)
    out=folder/'run'
    observed={}
    for name in ['CI_RESULT.json','artifact/CI_RESULT.json']:
        p=out/name
        observed[name]=json.loads(p.read_text())['status'] if p.exists() else None
    try:
        common.manifest(out/'artifact');manifest_ok=True
    except Exception:
        manifest_ok=False
    original=out/'fixtures/unit-tests/stderr.log'
    preserved=original.is_file() and original.read_bytes()==b'SYNTHETIC ORIGINAL DIAGNOSTIC\n'
    hits=json.loads((folder/'INJECTION.json').read_text())['hits']
    control=case.endswith('control')
    injected=bool(hits) if not control else not hits
    expected_rc=0 if case=='success-control' else 1
    expected_manifest=control
    # Acceptance is conjunctive; a standalone CI_RESULT=PASS is not enough.
    accepted=cp.returncode==0 and observed['artifact/CI_RESULT.json']=='PASS' and manifest_ok
    return {'case':case,'injection_observed':injected,'rc':cp.returncode,
        'result_statuses':observed,'manifest_complete':manifest_ok,'raw_log_preserved':preserved,
        'acceptance_allowed':accepted,'standalone_pass_remaining_after_failure':cp.returncode!=0 and 'PASS' in observed.values(),
        'passed_exit_and_preservation':injected and cp.returncode==expected_rc and
            manifest_ok==expected_manifest and preserved and accepted==(case=='success-control')}

if __name__=='__main__':
    cases=['success-control','fixture-fail-control','result-enospc','result-eacces','artifact-mkdir',
        'copy-result','copy-log','read-log','scope-write','manifest-write','manifest-partial','persistent-write-outage']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:
        rows=list(p.map(run,cases))
    verify()
    filename='PROPOSAL_STORAGE_FAILURES.json' if FAMILY=='proposal-faults' else 'STORAGE_FAILURES.json'
    (BASE/'results'/filename).write_text(json.dumps({
        'scope':'SYNTHETIC; real CI entrypoint/artifact export, mocked engines; OSError injection not real disk exhaustion',
        'cases':rows,'source_unchanged':True},indent=2)+'\n')
    print(json.dumps(rows,indent=2))
