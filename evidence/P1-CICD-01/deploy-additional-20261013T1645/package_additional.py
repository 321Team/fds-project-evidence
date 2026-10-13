"""Package the one authorized additional Run and read-only diagnostics."""
import base64,datetime,difflib,hashlib,json,pathlib,re,shutil,subprocess
O=pathlib.Path(__file__).parent;ROOT=O.parent.parent
R=ROOT/'phase1-work-20261013/db-policy-evidence'
C=ROOT/'deliverables/p1-preapply-until-0930-20261012/other-work/checkouts/infra-cicd'
A=C.parent/'fds-msa'
D=R/'evidence/P1-CICD-01/deploy-additional-20261013T1645';assert not (D/'SHA256SUMS').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda repo,rev:pathlib.Path(repo) and subprocess.check_output(['git','-C',str(repo),'show',rev])
source=git(C,'2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7:tools/delivery/build_scan.py')
assert source==git(C,'c9eff5fb2e50a690818a3e67347ab4a1bfc88f51:tools/delivery/build_scan.py')
old=source.decode();new=old.replace('def unpack_source(archive_path, target):','def unpack_source(archive_path, target, *, for_image=False):',1)
needle='                path.chmod(0o700 if member.mode & 0o111 else 0o600)\n'
assert new.count(needle)==1
new=new.replace(needle,needle+'''
    if for_image:
        # Only image context contents become readable to the non-root image user.
        # The context/evidence root and test copy retain private host permissions.
        for path in target.rglob('*'):
            path.chmod(0o755 if path.is_dir() or path.stat().st_mode & 0o111 else 0o644)
''',1)
assert new.count('unpack_source(snapshot, build_root)')==1
new=new.replace('unpack_source(snapshot, build_root)','unpack_source(snapshot, build_root, for_image=True)',1)
compile(new,'build_scan.py:proposed','exec')
patch=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/tools/delivery/build_scan.py',tofile='b/tools/delivery/build_scan.py'))
(O/'FIX_PROPOSAL.patch').write_text(patch,encoding='utf-8',newline='\n')
subprocess.run(['git','-C',str(C),'apply','--check',str((O/'FIX_PROPOSAL.patch').resolve())],check=True)
dirs=['dispatch-true-additional','fresh-074218','health-074258','app-state-074645','app-state-075127','failure-diagnostics-074807','failure-diagnostics-074833','image-permissions-075224','additional-decision-record']
dirs += [p.name for p in O.glob('app-security-*')]
dirs += ['operations/'+n+'-38364658401' for n in ['binding','broker-local','broker-execute']]
dirs += ['runtime-reads/'+p.name for p in (O/'runtime-reads').iterdir() if p.name>='074218925533']
files=[p for d in dirs for p in (O/d).rglob('*') if p.is_file()]
files += [O/n for n in ['START_CUTOFF_ADJUSTMENT.md','START_CUTOFF_AUTHORIZED.json','FIX_PROPOSAL.patch','dispatch_additional.py','handoff_additional.py','package_additional.py']]
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}']
for p in files:assert not any(re.search(pat,p.read_bytes()) for pat in patterns),('CREDENTIAL_PATTERN',p.name)
checks=[]
for p in files:
    if p.name!='receipt.json':continue
    x=json.loads(p.read_bytes());d=p.parent
    for filename,key in [('collector.py','source_sha256'),('command.txt','command_sha256'),('stdout.json','stdout_sha256'),('stdout.txt','stdout_sha256'),('stderr.txt','stderr_sha256')]:
        if (d/filename).exists() and key in x:assert sha((d/filename).read_bytes())==x[key],(d,filename)
    checks.append({'path':p.relative_to(O).as_posix(),'rc':x['rc'],'hashes':'MATCH'})
runtime=json.loads((O/'runtime-reads/075057810116/stdout.json').read_bytes())
result=runtime['matches'][0]['files']['result.json']['data'];exe=result['execution_receipt']
assert result['error_code']=='READINESS_TIMEOUT' and exe['ROLLBACK']=='READY_HEALTH_NOT_VERIFIED'
assert exe['images']['fds-engine']['deploy']=='NOT_EXECUTED' and len(runtime['claim_files'])==10 and not runtime['socket']['exists']
after=json.loads((O/'app-state-075127/cp1/stdout.json').read_bytes())
deploys=next(q['items'] for q in after['queries'] if q['kind']=='deployments')
pods=next(q['items'] for q in after['queries'] if q['kind']=='pods')
for i in deploys:
    b=exe['images'][i['metadata']['name']]['before']
    assert i['metadata']['uid']==b['uid'] and i['spec_sha256']==b['spec_sha256'] and i['containers'][0]['image']==b['image']
    assert all(i['status'][k]==3 for k in ('availableReplicas','readyReplicas','updatedReplicas'))
assert len(pods)==6 and all(p['phase']=='Running' and all(c['ready'] for c in p['statuses']) for p in pods)
credential=result['credential'];assert (datetime.datetime.fromisoformat(credential['expires_at'])-datetime.datetime.fromisoformat(credential['issued_at'])).total_seconds()==900
images=json.loads((O/'image-permissions-075224/runner/stdout.json').read_bytes())['images']
for v in images.values():
    run=[e for e in v['selected_layer_entries'] if e['path']=='app/run.py'][-1]
    assert (run['mode'],run['uid'],run['gid'],v['config_user'])==('0o600',0,0,'10001:999')
D.mkdir(parents=True,exist_ok=True)
for p in files:
    dest=D/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
readme=(O/'ADDITIONAL_RESULT.md').read_text(encoding='utf-8').replace('16:45:09~16:50:35','16:45:09~16:50:34')
(D/'README.md').write_text(readme,encoding='utf-8',newline='\n')
srcdir=D/'pinned-source';srcdir.mkdir(exist_ok=True);(srcdir/'build_scan.py').write_bytes(source)
for name in ['transaction-api','fds-engine']:(srcdir/(name+'.Dockerfile')).write_bytes(git(A,'affbc69beef9967f7977d09a6fec14f7fb6c0e94:'+name+'/Dockerfile'))
originals=[]
groups=[('workflow',runtime['matches'][0]['files']),('persistent-claim',runtime['claim_files'])]
for group,values in groups:
    for name,v in values.items():
        raw=base64.b64decode(v['raw_b64'],validate=True);assert sha(raw)==v['sha256'] and len(raw)==v['bytes'] and json.loads(raw)==v['data']
        assert not any(re.search(pat,raw) for pat in patterns)
        short_name=('checkpoint-'+name.rsplit('/',1)[-1] if '/' in name else 'claim.json') if group=='persistent-claim' else name
        p=D/'selected-original-receipts'/group/short_name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        originals.append({'path':p.relative_to(D).as_posix(),'remote_relative_name':name,'sha256':sha(raw),'bytes':len(raw)})
log=json.loads((O/'dispatch-true-additional/job-log-receipt.json').read_bytes());assert sha((O/'dispatch-true-additional/job-log.txt').read_bytes())==log['stdout_sha256']
verify={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipt_checks':checks,'originals':originals,'actual_run':38364658401,'attempt':1,'rollout':'FAILED','rollback':'READY_HEALTH_NOT_VERIFIED','post_pods_running_ready':6,'post_previous_spec_images_match':True,'token_lifetime_seconds':900,'proposal_patch':'PARSES_AND_APPLIES_TO_2d8a14c_NOT_APPLIED','posix_regression':'NOT_RUN','image_permission_defect':'BOTH_ARCHIVES_ROOT_0600_RUN_PY_USER_10001','source_comparison_c9eff5f_to_2d8a14c_build_scan':'IDENTICAL','independent_latest_evidence_review':'PENDING'}
(D/'RECEIPT_VERIFICATION.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
sha_files=sorted(p for p in D.rglob('*') if p.is_file());manifest=D/'SHA256SUMS'
manifest.write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(D).as_posix()+'\n' for p in sha_files),encoding='utf-8',newline='\n')
reg=R/'REGISTRY_SHA256SUMS';raw=reg.read_bytes();rel=manifest.relative_to(R).as_posix();assert rel.encode() not in raw
reg.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+(sha(manifest.read_bytes())+'  '+rel+'\n').encode())
print(json.dumps({'path':D.relative_to(R).as_posix(),'files':len(sha_files)+1,'receipts':len(checks),'originals':len(originals),'result_sha256':runtime['matches'][0]['files']['result.json']['sha256']}))
