"""Read-only receipt verification. No remote mutations or collected commands run."""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parent
UPLOAD=ROOT.parent/'upload'
PREVIOUS=ROOT.parent/'ansible-export-receipt.9Rp9iWjz'
SOURCE='31895081e30e27481e7c17407047c9454e3b247a'
REPO='321Team/infra-ansible'
RUN,ATTEMPT,JOB,RUNNER=35195838409,1,105118736321,26
NAME='ansible-ci-a6b75591ba3d4d38b5a3c3797afd8d37'
BRANCH='test/issue-5-export-fix-positive-20260917'
sha=lambda b:hashlib.sha256(b).hexdigest()
parse=lambda x:dt.datetime.fromisoformat(x.replace('Z','+00:00'))

def unique(pairs):
    d={}
    for k,v in pairs:
        assert k not in d, 'duplicate JSON key'
        d[k]=v
    return d

def read(raw):
    return json.loads(raw,object_pairs_hook=unique)

def safe(name):
    p=PurePosixPath(name)
    assert not p.is_absolute() and p.as_posix()==name
    assert all(x not in ('','.','..') for x in name.split('/'))

source=UPLOAD/'ansible-export-fix-receipt.tar.gz'
if not source.exists():source=ROOT/'originals/ansible-export-fix-receipt.tar.gz'
raw=source.read_bytes();side=Path(str(source)+'.sha256').read_bytes()
assert side.decode().split()==[sha(raw),'ansible-export-fix-receipt.tar.gz']
assert sha(raw)=='40410f2eca8da7ed4c7c509a499443663a202bf56210588912f6a5abb3246c15'
files={};seen=set();expanded=0
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
    for m in t:
        safe(m.name);assert m.name not in seen;seen.add(m.name)
        assert m.isfile() or m.isdir()
        expanded+=m.size;assert expanded<8*1024**2 and len(seen)<100
        if m.isfile():files[m.name]=t.extractfile(m).read()
manifest=files['evidence/SHA256SUMS'].decode().splitlines();listed=set()
for line in manifest:
    digest,name=line.split('  ',1);safe(name)
    assert re.fullmatch('[0-9a-f]{64}',digest) and name not in listed
    listed.add(name);assert sha(files['evidence/'+name])==digest
assert len(listed)==7 and {'evidence/'+n for n in listed}|{'evidence/SHA256SUMS'}==set(files)
assert listed=={'RESULT.json','check.json','execution.rc','jobs-attempt1.json','pr.json','run-attempt1.json','runner-pages.json'}
result=read(files['evidence/RESULT.json']);run=read(files['evidence/run-attempt1.json'])
jobs=read(files['evidence/jobs-attempt1.json']);check=read(files['evidence/check.json'])
pr=read(files['evidence/pr.json']);pages=read(files['evidence/runner-pages.json'])
assert files['evidence/execution.rc']==b'0\n'
assert result['status']=='COLLECTED_BOUND_REVIEW_REQUIRED' and result['errors']==[]
assert result['hostname']=='ansible01' and result['uid']==1000
assert result['source']==SOURCE and result['run_id']==RUN and result['attempt']==ATTEMPT and result['job_id']==JOB
assert result['token_issuance'] is False and result['server_changes'] is False and result['rerun'] is False
assert result['artifact_download'] is False and result['independent_approval']=='NOT_GRANTED'
assert run['id']==RUN and run['run_attempt']==ATTEMPT and run['head_sha']==SOURCE
assert run['repository']['full_name']==REPO and run['event']=='pull_request'
assert run['status']=='completed' and run['conclusion']=='success' and run['head_branch']==BRANCH
assert jobs['total_count']==len(jobs['jobs'])==1
job=jobs['jobs'][0]
assert (job['id'],job['run_id'],job['run_attempt'],job['head_sha'])==(JOB,RUN,ATTEMPT,SOURCE)
assert (job['name'],job['status'],job['conclusion'])==('regression','completed','success')
assert job['runner_id']==RUNNER and job['runner_name']==NAME
assert set(job['labels'])=={'self-hosted','Linux','X64','fds-ci','ansible-isolated'}
assert check['id']==JOB and check['head_sha']==SOURCE and check['name']=='regression'
assert check['status']=='completed' and check['conclusion']=='success'
assert check['check_suite']['id']==run['check_suite_id']==95316041498
assert check['app']['slug']=='github-actions' and check['app']['id']==15368
assert check['html_url']==job['html_url'] and check['started_at']==job['started_at'] and check['completed_at']==job['completed_at']
assert len(check['pull_requests'])==1 and check['pull_requests'][0]['number']==22
assert check['pull_requests'][0]['head']['sha']==SOURCE and check['pull_requests'][0]['head']['ref']==BRANCH
assert pr['number']==22 and pr['state']=='open' and pr['draft'] is True
assert pr['head']['sha']==SOURCE and pr['head']['ref']==BRANCH and pr['head']['repo']['full_name']==REPO
assert pr['base']['ref']=='main' and pr['base']['repo']['full_name']==REPO
assert isinstance(pages,list) and pages
assert all(type(p.get('total_count')) is int and p['total_count']>=0 and isinstance(p.get('runners'),list) for p in pages)
rows=[r for p in pages for r in p['runners']]
assert all(type(r.get('id')) is int and r['id']>0 and isinstance(r.get('name'),str) and r['name'] for r in rows)
assert len({r['id'] for r in rows})==len(rows) and all(p['total_count']==len(rows) for p in pages)
assert all(r['id']!=RUNNER and r['name']!=NAME for r in rows)
assert result['runner_absence']==dict(absent=True,complete_query=True,deletion_performed=False,matching_count=0,runner_id=RUNNER,runner_name=NAME)

expected=[f'pulls/22',f'actions/runs/{RUN}/attempts/1',f'actions/runs/{RUN}/attempts/1/jobs?per_page=100',
          f'check-runs/{JOB}','actions/runners?per_page=100']
assert len(result['commands'])==5
last=parse(result['started_at_utc'])
for index,(command,endpoint) in enumerate(zip(result['commands'],expected)):
    argv=['/usr/bin/gh','api','--hostname','github.com','--method','GET','-H','Accept: application/vnd.github+json',
          '-H','X-GitHub-Api-Version: 2022-11-28','repos/'+REPO+'/'+endpoint]
    if index==4:argv+=['--paginate','--slurp']
    assert command['command']==argv and command['rc']==0 and command['timed_out'] is False
    assert last<=parse(command['started_at_utc'])<=parse(command['ended_at_utc'])
    last=parse(command['ended_at_utc'])
assert last<=parse(result['ended_at_utc'])

previous_path=PREVIOUS/'VALIDATION.json'
if not previous_path.exists():previous_path=ROOT/'prior/VALIDATION.json'
previous=read(previous_path.read_bytes())
assert previous['source']==SOURCE and previous['run_id']==RUN and previous['attempt']==ATTEMPT
assert previous['runner_id']==RUNNER and previous['runner_name']==NAME
assert previous['runtime_pass'] is True and previous['local_cleanup_pass'] is True and previous['isolation_pass']==18
assert previous['artifact_internal_verification']=='PASS' and previous['unit_tests']==58
assert previous['session_end']==result['session_ended_at_utc']
assert parse(previous['session_start'])<=parse(job['started_at'])<=parse(job['completed_at'])<=parse(previous['session_end'])<parse(result['started_at_utc'])
assert result['execution_bound'] is True and result['current_pr_bound'] is True and result['query_after_session'] is True

kit=ROOT.parent/'deliverables/FDS_Ansible_Export_Fix_Receipt_v1_0.zip'
if kit.exists():
    assert sha(kit.read_bytes())=='78b537c8a5b7a2ca17328525f30ef2ebe4930484314c69d140e126fc1dc1c0da'
    with zipfile.ZipFile(kit) as z:script=z.read('FDS_Ansible_Export_Fix_Receipt_v1_0/collect.py')
else:script=(ROOT/'prior/collect.py').read_bytes()
assert sha(script)==result['script_sha256']=='7510ef8f68fc69d68f7357f28fdd4a4f41fcab6aa3e0ccc61b4da94b6375eff8'

for name,data in files.items():
    dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'originals').mkdir(exist_ok=True)
(ROOT/'originals/ansible-export-fix-receipt.tar.gz').write_bytes(raw)
(ROOT/'originals/ansible-export-fix-receipt.tar.gz.sha256').write_bytes(side)
(ROOT/'prior').mkdir(exist_ok=True)
(ROOT/'prior/VALIDATION.json').write_bytes(previous_path.read_bytes())
(ROOT/'prior/collect.py').write_bytes(script)
verdict=dict(status='PASS_POSITIVE_EXECUTION_EVIDENCE_VERIFIED',receipt_sha256=sha(raw),receipt_bytes=len(raw),manifest='7/7',
             source=SOURCE,run_id=RUN,attempt=ATTEMPT,job_id=JOB,check_suite_id=95316041498,check='success',
             runner_id=RUNNER,runner_name=NAME,runner_query_pages=len(pages),runner_total_count=len(rows),runner_target_absent=True,
             receipt_start_utc=result['started_at_utc'],receipt_end_utc=result['ended_at_utc'],query_after_session=True,
             collector_script_sha256=sha(script),read_only_commands=5,prior_runtime_artifact_binding=True,
             normal_execution_remaining_receipt_items=0,independent_review='PENDING',merge='NOT_RUN',production_apply=False,engine_transition=False)
(ROOT/'VALIDATION.json').write_text(json.dumps(verdict,indent=2)+'\n')
print(json.dumps(verdict,indent=2))
