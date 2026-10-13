"""Package collected attempt receipts without invoking any runtime operation."""
import base64,datetime,hashlib,json,pathlib,re,shutil
O=pathlib.Path(__file__).parent
R=O.parent.parent/'phase1-work-20261013/db-policy-evidence'
D=R/'evidence/P1-CICD-01/deploy-attempt-20261013T1615'
assert not D.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
dirs=['operations','runtime-reads','dispatch-false','dispatch-true','fresh-071215','fresh-072150','health-071215','preissue-diagnosis','app-post-attempt']
files=[p for d in dirs for p in (O/d).rglob('*') if p.is_file()]
names=['EXECUTION_ENTRY_CHECK.json','BROKER_TIME_DIAGNOSIS.json','FALSE_PREFLIGHT_VERIFIED.json','WORKFLOW_RUNS_AT_CLOSEOUT.json','package_attempt.py']
files += [O/n for n in names]
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}']
for p in files:
    raw=p.read_bytes()
    assert not any(re.search(pat,raw) for pat in patterns),('CREDENTIAL_PATTERN',p.name)
checks=[]
for p in files:
    if p.name=='receipt.json':
        x=json.loads(p.read_bytes());d=p.parent;row={'receipt':p.relative_to(O).as_posix(),'rc':x['rc'],'hashes':'MATCH'}
        for filename,key in [('collector.py','source_sha256'),('command.txt','command_sha256'),('stdout.json','stdout_sha256'),('stdout.txt','stdout_sha256'),('stderr.txt','stderr_sha256')]:
            if (d/filename).exists() and key in x:
                assert sha((d/filename).read_bytes())==x[key],(d,filename)
        checks.append(row)
for d in ['dispatch-false','dispatch-true']:
    x=json.loads((O/d/'job-log-receipt.json').read_bytes())
    assert sha((O/d/'job-log.txt').read_bytes())==x['stdout_sha256']
    assert sha((O/d/'job-log.stderr.txt').read_bytes())==x['stderr_sha256']
before=json.loads((O/'fresh-071215/cluster/stdout.json').read_bytes())
after=json.loads((O/'fresh-072150/cluster/stdout.json').read_bytes())
assert before['ca_sha256']==after['ca_sha256']
assert [(x['kind'],x['items']) for x in before['queries']]==[(x['kind'],x['items']) for x in after['queries']]
assert all(x['rc']==0 for x in after['queries'])
app=json.loads((O/'app-post-attempt/cp1/stdout.json').read_bytes())
pods=next(q['items'] for q in app['queries'] if q['kind']=='pods')
assert len(pods)==6 and all(p['phase']=='Running' and all(c['ready'] for c in p['statuses']) for p in pods)
assert not (O/'dispatch-true-additional').exists()
runs=json.loads((O/'WORKFLOW_RUNS_AT_CLOSEOUT.json').read_bytes())['workflow_runs']
assert {r['id'] for r in runs}=={38361678189,38361855044}
D.mkdir(parents=True)
for p in files:
    dest=D/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
shutil.copyfile(O/'ATTEMPT_CLOSEOUT.md',D/'README.md')
decoded=[]
for stamp,kind in [('071718421863','false'),('072149980833','true')]:
    x=json.loads((O/'runtime-reads'/stamp/'stdout.json').read_bytes())
    assert len(x['matches'])==1 and not x['socket']['exists']
    if kind=='true':assert x['claim_files']=={}
    for name,v in x['matches'][0]['files'].items():
        raw=base64.b64decode(v['raw_b64'],validate=True)
        assert sha(raw)==v['sha256'] and len(raw)==v['bytes'] and json.loads(raw)==v['data']
        assert not any(re.search(pat,raw) for pat in patterns)
        dest=D/'selected-original-receipts'/kind/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        decoded.append({'path':dest.relative_to(D).as_posix(),'source':'runtime-reads/'+stamp+'/stdout.json','sha256':sha(raw),'bytes':len(raw)})
decision={'schema':'P1-deploy-cutoff-decision-1','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'user_answer':'새 Run 추가 1회 허용','answer_timestamp':'NOT_AVAILABLE','clock_after_answer_processing_utc':'2026-10-13T07:30:14Z','clock_recheck_utc':'2026-10-13T07:35:32Z','latest_start_kst':'2026-10-13T16:30:00+09:00','original_end_kst':'2026-10-13T17:00:00+09:00','additional_run':'NOT_DISPATCHED','reason':'START_CUTOFF_PASSED','window_extended':False,'original_approval_changed':False,'runtime_state':'FAILURE_BEFORE_CONFIRMED_DEPLOY','ai_usage':'CODEX_ASSISTED'}
(D/'CUTOFF_DECISION.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'selected_originals':decoded,'job_log_hashes':'2/2 MATCH','pre_post_cluster_items_and_ca':'MATCH','pods_current_running_ready':6,'credential_pattern_matches':0,'scope_limit':'Selected credential patterns only; hash equality is integrity, not acceptance. Raw broker TOKEN_ISSUANCE remains NOT_CONFIRMED.'}
(D/'RECEIPT_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
allfiles=sorted(p for p in D.rglob('*') if p.is_file())
(D/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(D).as_posix()+'\n' for p in allfiles),encoding='utf-8',newline='\n')
reg=R/'REGISTRY_SHA256SUMS';raw=reg.read_bytes();rel=(D/'SHA256SUMS').relative_to(R).as_posix();assert rel.encode() not in raw
reg.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+(sha((D/'SHA256SUMS').read_bytes())+'  '+rel+'\n').encode())
print(json.dumps({'new_files':len(allfiles)+1,'receipt_checks':len(checks),'decoded_originals':len(decoded),'path':D.relative_to(R).as_posix(),'additional_run':'NOT_DISPATCHED'}))
