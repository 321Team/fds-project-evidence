#!/usr/bin/env python3
import ast
import concurrent.futures
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import prepare_and_run as baseline

def main():
    candidate=BASE/'candidate';proposal=BASE/'proposal'
    changed=[]
    patchtext=''
    for p in sorted(candidate.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(candidate);q=proposal/rel
        if p.read_bytes()!=q.read_bytes():
            changed.append(str(rel))
            ast.parse(q.read_text())
            patchtext+=''.join(difflib.unified_diff(p.read_text().splitlines(True),
                q.read_text().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)))
    assert changed==['tests/test_ci_regression.py','tools/run-ansible-ci.py'],changed
    patchpath=BASE/'results/artifact-export-status.patch'
    patchpath.write_text(patchtext)
    check=subprocess.run(['git','apply','--check',str(patchpath)],cwd=candidate,
        env=baseline.environment(),capture_output=True)
    assert check.returncode==0,check.stderr
    reverse=subprocess.run(['git','apply','--reverse','--check',str(patchpath)],cwd=proposal,
        env=baseline.environment(),capture_output=True)
    assert reverse.returncode==0,reverse.stderr
    # Run the added test against unchanged production code; preserve the expected failing result.
    red=BASE/'red-control'
    shutil.copytree(candidate,red)
    testpath=red/'tests/test_ci_regression.py'
    testpath.write_bytes((proposal/'tests/test_ci_regression.py').read_bytes())
    command=[sys.executable,'-I','-B','-c',
        'import sys,unittest;sys.path.insert(0,'+repr(str(red/'tests'))+');'+
        'suite=unittest.defaultTestLoader.loadTestsFromName('+
        repr('test_ci_regression.CIGateTests.test_artifact_export_failure_marks_writable_results_failed')+');'+
        'r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())']
    redresult=subprocess.run(command,cwd=red,env=baseline.environment(),capture_output=True,timeout=30)
    (BASE/'results/proposal-red-control.stdout.log').write_bytes(redresult.stdout)
    (BASE/'results/proposal-red-control.stderr.log').write_bytes(redresult.stderr)
    assert redresult.returncode==1 and b'SYNTHETIC_STORAGE_FAULT' in redresult.stderr
    baseline.REPO=proposal
    suites=[('proposal-ci-58','DISCOVER',58),('proposal-runner-37','tools/ansible-runner/test-kit.py',37),
        ('proposal-registration-13','tools/ansible-runner/test-registration.py',13),
        ('proposal-ipc-7','tools/ansible-runner/test-ipc.py',7),
        ('proposal-admin-22','tools/ansible-admin-token/test-admin-token.py',22),
        ('proposal-input-20','tools/ansible-runner-input/test_safe_input.py',20)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(baseline.run_one,suites))
    baseline.REPO=candidate
    baseline.verify()
    record={'changed_paths':changed,'git_apply_check':check.returncode,
        'git_reverse_check':reverse.returncode,'red_control_rc':redresult.returncode,
        'red_control_expected_failure':True,'suites':results,
        'source_unchanged':True,'proposal_applied_to_github':False,
        'limitations':'Best effort status repair only. Persistent/all-path storage failure cannot guarantee writing diagnostics; rc and manifest are still mandatory.'}
    (BASE/'results/PROPOSAL_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()

