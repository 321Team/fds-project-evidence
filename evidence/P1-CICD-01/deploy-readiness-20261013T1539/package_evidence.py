"""Package new read-only evidence, preserving every collected byte."""
import hashlib,json,pathlib,shutil
OUT=pathlib.Path(__file__).parent
REPO=OUT.parent.parent/'phase1-work-20261013/db-policy-evidence'
REL=pathlib.Path('evidence/P1-CICD-01/deploy-readiness-20261013T1539')
DEST=REPO/REL
DEST.mkdir(parents=True,exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
dirs=['cluster','cp1-auth','runner-auth','cache-worker01','cache-worker02','cache-worker03']
plan=json.loads((OUT/'deploy-plan.unapproved.json').read_bytes())
checks=[]
for name in dirs:
    d=OUT/name;r=json.loads((d/'receipt.json').read_bytes());x=json.loads((d/'stdout.json').read_bytes())
    assert r['rc']==0
    assert sha((d/'collector.py').read_bytes())==r['source_sha256']
    assert sha((d/'stdout.json').read_bytes())==r['stdout_sha256']
    assert sha((d/'stderr.txt').read_bytes())==r['stderr_sha256']
    row={'name':name,'receipt_hashes':'MATCH','remote_source_review':'NOT PERFORMED (Pre-check)'}
    if name.startswith('cache-'):
        found={digest for image in x['selected_images'] for digest in image['repoDigests']}
        assert all(t['previous_image'] in found for t in plan['targets'].values())
        row.update(previous_digest_metadata_count=2,inner_stderr_bytes=x['stderr_bytes'],registry_repull='NOT_VERIFIED',layer_bytes='NOT_VERIFIED')
    checks.append(row)
    shutil.copytree(d,DEST/name)
names=['README.md','deploy-plan.unapproved.json','push-result.original.json','PLAN_VALIDATION.json','read_fresh_inputs.py','prepare_plan.py','rollback_cache_read.py','collect_rollback_cache.py','package_evidence.py']
for name in names:shutil.copyfile(OUT/name,DEST/name)
verification={'schema':'P1-deploy-readiness-receipts-1','checks':checks,'approved':False,'runtime_deploy':'NOT_EXECUTED','previous_digests_in_worker_cri_metadata':'6/6','limit':'Metadata and SHA256 checks are not rollout, registry re-pull, independent review or acceptance.'}
(DEST/'RECEIPT_VERIFICATION.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
files=sorted(p for p in DEST.rglob('*') if p.is_file())
(DEST/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(DEST).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
reg=REPO/'REGISTRY_SHA256SUMS'
raw=reg.read_bytes();assert str(REL).replace('\\','/').encode() not in raw
reg.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+(sha((DEST/'SHA256SUMS').read_bytes())+'  '+(REL/'SHA256SUMS').as_posix()+'\n').encode())
print(json.dumps({'new_files':len(files)+1,'path':str(REL),'receipt_checks':len(checks),'cache_presence':'6/6'}))
