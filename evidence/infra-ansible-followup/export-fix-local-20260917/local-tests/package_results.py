#!/usr/bin/env python3
import ast
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import zipfile

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from prepare_and_run import verify
verify()
results=BASE/'results'
original=json.loads((results/'EXISTING_SUITES.json').read_text())
storage=json.loads((results/'STORAGE_FAILURES.json').read_text())
tamper=json.loads((results/'TAMPER_MATRIX.json').read_text())
timeouts=json.loads((results/'TIMEOUT_MATRIX.json').read_text())
proposal=json.loads((results/'PROPOSAL_VALIDATION.json').read_text())
proposal_storage=json.loads((results/'PROPOSAL_STORAGE_FAILURES.json').read_text())
final=json.loads((results/'FINAL_STATE.json').read_text())
assert sum(r['observed_tests'] for r in original['suites'])==156 and all(r['passed'] for r in original['suites'])
assert len(storage['cases'])==12 and all(r['passed_exit_and_preservation'] for r in storage['cases'])
assert len(tamper['cases'])==60 and all(r['passed'] for r in tamper['cases'])
assert len(timeouts['rows'])==210 and all(r['expected_behavior_confirmed'] for r in timeouts['rows'])
assert sum(r['observed_tests'] for r in proposal['suites'])==157 and all(r['passed'] for r in proposal['suites'])
assert len(proposal_storage['cases'])==12 and all(r['passed_exit_and_preservation'] for r in proposal_storage['cases'])
assert sum(r['standalone_pass_remaining_after_failure'] for r in storage['cases'])==8
assert sum(r['standalone_pass_remaining_after_failure'] for r in proposal_storage['cases'])==1
assert all(p['unchanged'] for p in final['prs'])
environment={'python':sys.version,'platform':platform.platform(),'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),
    'credential_environment_dumped':False,'test_kind':'LOCAL/MOCK'}
(results/'ENVIRONMENT.json').write_text(json.dumps(environment,indent=2)+'\n')
files={}
for p in sorted(BASE.glob('*.py')):
    ast.parse(p.read_text());files[p.name]=p.read_bytes()
for name in ['README.md','source-map.json']:
    files[name]=(BASE/name).read_bytes()
for p in sorted(results.rglob('*')):
    rel=p.relative_to(BASE)
    if p.is_symlink() or not p.is_file():continue
    if 'private' in rel.parts or rel.parts[:2]==('results','tamper'):continue
    files[rel.as_posix()]=p.read_bytes()
index={'purpose':'review-only LOCAL/MOCK evidence, NOT a server runtime kit',
    'source_files':125,'existing_unit_tests':156,'storage_cases':12,
    'existing_tamper_cases':25,'new_binding_model_cases':35,'timeout_repeat_cases':200,
    'legacy_timeout_limitation_reproductions':10,'proposal_unit_tests':157,
    'original_pass_markers_after_failure':8,'proposal_pass_markers_after_failure':1,
    'files':[{'path':k,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in sorted(files.items())],
    'excluded':['Git-backed candidate/proposal/red-control source trees','source-input.json with Git-backed contents',
                'duplicate timeout private logs','mutated tamper fixture objects; reconstruct from tamper_matrix.py'],
    'scope_flags':final}
files['PACKAGE_INDEX.json']=(json.dumps(index,indent=2)+'\n').encode()
manifest=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in sorted(files.items()))
files['SHA256SUMS']=manifest.encode()
out=BASE.parent/'deliverables';out.mkdir(exist_ok=True)
name='FDS_Ansible_Local_Additional_Tests_20260917_v1_0'
archive=out/(name+'.zip')
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for k,v in sorted(files.items()):
        i=zipfile.ZipInfo(name+'/'+k,(2026,9,17,0,0,0))
        i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(i,v)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
sidecar=archive.with_name(archive.name+'.sha256')
with sidecar.open('x') as stream:stream.write(sha+'  '+archive.name+'\n')
patch=out/'FDS_Ansible_Artifact_Export_Status_Proposal_v1_0.patch'
with patch.open('xb') as stream:stream.write((results/'artifact-export-status.patch').read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in manifest.splitlines():
        expected,p=line.split('  ',1)
        assert hashlib.sha256(z.read(name+'/'+p)).hexdigest()==expected
    assert len(z.infolist())==len(files)
    assert len(set(z.namelist()))==len(files)
record={'archive':str(archive),'sha256':sha,'bytes':archive.stat().st_size,
    'manifest_entries':len(files)-1,'zip_members':len(files),'sidecar':str(sidecar),
    'patch':str(patch),'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'verified':True}
(BASE/'PACKAGE_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

