#!/usr/bin/env python3
"""Inject one storage error into the real CI entrypoint with engine calls mocked."""
from contextlib import ExitStack
import errno
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from offline_guard import install
install()
REPO=Path(sys.argv[2]) if len(sys.argv)>2 else BASE/'candidate'
CASE=sys.argv[1]
FAMILY='proposal-faults' if REPO.name=='proposal' else 'faults'
OUT=BASE/'results'/FAMILY/CASE/'run'
OUT.parent.mkdir(parents=True,exist_ok=False)
SHA='9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6'
spec=importlib.util.spec_from_file_location('tested_ci',REPO/'tools/run-ansible-ci.py')
ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)
real_wb,real_wt,real_mkdir,real_rb=Path.write_bytes,Path.write_text,Path.mkdir,Path.read_bytes
targets={
 'result-enospc':('wb','CI_RESULT.json',errno.ENOSPC),
 'result-eacces':('wb','CI_RESULT.json',errno.EACCES),
 'artifact-mkdir':('mkdir','artifact',errno.EACCES),
 'copy-result':('wb','artifact/CI_RESULT.json',errno.ENOSPC),
 'copy-log':('wb','artifact/fixtures/unit-tests/stderr.log',errno.ENOSPC),
 'read-log':('rb','fixtures/unit-tests/stderr.log',errno.EIO),
 'scope-write':('wb','artifact/ARTIFACT_SCOPE.json',errno.ENOSPC),
 'manifest-write':('wt','artifact/SHA256SUMS',errno.ENOSPC),
 'manifest-partial':('wt','artifact/SHA256SUMS',errno.ENOSPC),
 'persistent-write-outage':('wb','artifact/ARTIFACT_SCOPE.json',errno.ENOSPC),
}
hit=[]
def fail(kind,path,value=None):
    if CASE=='persistent-write-outage' and hit and kind in ('wb','wt'):
        hit.append({'operation':kind,'path':str(path.relative_to(OUT)),'errno':errno.ENOSPC})
        raise OSError(errno.ENOSPC,'SYNTHETIC_PERSISTENT_STORAGE_FAULT')
    if CASE in targets:
        operation,relative,code=targets[CASE]
        if kind==operation and path==OUT/relative:
            hit.append({'operation':kind,'path':relative,'errno':code})
            if CASE=='manifest-partial':
                real_wt(path,value.splitlines(keepends=True)[0])
            raise OSError(code,'SYNTHETIC_STORAGE_FAULT')
def wb(path,data,*a,**kw):
    fail('wb',path,data);return real_wb(path,data,*a,**kw)
def wt(path,data,*a,**kw):
    fail('wt',path,data);return real_wt(path,data,*a,**kw)
def mkdir(path,*a,**kw):
    fail('mkdir',path);return real_mkdir(path,*a,**kw)
def rb(path,*a,**kw):
    fail('rb',path);return real_rb(path,*a,**kw)
def prepare(*a):
    (OUT/'runtime').mkdir()
    (OUT/'runtime/RUNTIME.json').write_text(json.dumps({'source_commit':SHA,'status':'PREPARED'}))
    return {'source_commit':SHA,'status':'PREPARED'}
def syntax(runtime,output,paths,engines,evidence):
    (OUT/'syntax-ansible.cfg').write_text('# SYNTHETIC TEST ONLY\n')
    evidence.extend({'engine':e,'playbook':p,'rc':0} for e in engines for p in paths)
def fixture(*a):
    d=OUT/'fixtures/unit-tests';d.mkdir(parents=True)
    (d/'stderr.log').write_text('SYNTHETIC ORIGINAL DIAGNOSTIC\n')
    status='FAIL' if CASE=='fixture-fail-control' else 'PASS_FRESH_OFFLINE_FIXTURES'
    record={'source_commit':SHA,'status':status}
    (OUT/'fixtures/KIT_RUN.json').write_text(json.dumps(record))
    return record
try:
    with ExitStack() as stack:
        for name,value in {
            'clean_source':lambda *a:None,'target_host':lambda:None,
            'build':lambda *a:{'source_commit':SHA,'archive':'/synthetic-kit','sha256':'b'*64},
            'prepare':prepare,'run':fixture
        }.items():
            stack.enter_context(patch.object(ci.kit,name,value))
        stack.enter_context(patch.object(ci,'syntax_gate',syntax))
        for name,value in [('write_bytes',wb),('write_text',wt),('mkdir',mkdir),('read_bytes',rb)]:
            stack.enter_context(patch.object(Path,name,value))
        stack.enter_context(patch.object(sys,'argv',['run-ansible-ci.py','--repo',str(REPO),
            '--commit',SHA,'--output',str(OUT),'--wheels','/synthetic-preloaded-wheels']))
        raise SystemExit(ci.main())
finally:
    real_wt(OUT.parent/'INJECTION.json',json.dumps({'case':CASE,'hits':hit},indent=2)+'\n')
