"""Offline verification of the actual stopped run, never an application PASS."""
import datetime as dt,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_bytes())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
index=read('RECEIVED_INDEX.json')
for row in index['files']:
    path=ROOT/row['path']
    assert path.is_file() and len(path.read_bytes())==row['bytes'] and digest(path)==row['sha256'],row['path']
manifest_items=0
for manifest in (ROOT/'received').rglob('SHA256SUMS'):
    for line in manifest.read_text().splitlines():
        sha,name=line.split('  ',1)
        path=manifest.parent/name
        assert path.resolve().is_relative_to(manifest.parent.resolve())
        assert path.is_file() and digest(path)==sha,(str(manifest),name)
        manifest_items+=1
runtime=ROOT/'received/runtime/FDS_D03_202610142110'
result=json.loads((runtime/'result.json').read_bytes())
assert result['result']=='CLEANUP_FAILED' and result['cleanup_confirmed'] is False
assert result['failure']=={'type':'RuntimeError','message':'COMMAND_FAILED 6'}
assert result['production_runtime_claim'] is False
commands=[json.loads(p.read_bytes()) for p in sorted(runtime.glob('*-command.json'))]
assert len(commands)==7
assert sum(x['argv'][0]=='create' for x in commands)==1
assert all(x['argv'][0]!='start' for x in commands)
failed=commands[5]
assert failed['rc']==125 and failed['timed_out'] is False
assert 'unknown mount option "uid=26"' in failed['stderr']
assert commands[6]['argv']==['container','exists','fds-d03-202610142110-db'] and commands[6]['rc']==1
assert not list(runtime.glob('*-post-intent.json')) and not list(runtime.glob('*-result.json'))
assert not (runtime/'verified-cases.json').exists()
assert all(p.name not in ('db.env','api.env') for p in ROOT.rglob('*'))
plan=read('decisions/plan.json');auth=read('decisions/authorization.json')
assert plan['run']=='202610142110' and auth['approved'] and auth['runner_exclusive'] and auth['lab_db_image_accepted']
assert digest(ROOT/'decisions/plan.json')==auth['plan_sha256']=='3f2038b9d90fecf727e24f901703df88d7b5b4f8d9bb2005a2b68aa5f660addf'
assert (runtime/'plan.json').read_bytes()==(ROOT/'decisions/plan.json').read_bytes()
assert json.loads((runtime/'authorization.json').read_bytes())==auth
inv=read('received/runtime/FDS_D03_RuntimeInvocation_202610142110/receipt.json')
assert inv['rc']==1
assert dt.datetime.fromisoformat(auth['start_after'])<=dt.datetime.fromisoformat(inv['started_at_utc'])<=dt.datetime.fromisoformat(auth['start_before'])
assert dt.datetime.fromisoformat(inv['finished_at_utc'])<dt.datetime.fromisoformat(auth['finish_before'])
claim=ROOT/'received/runtime/FDS_D03_Claims/202610142110.json'
absence=read('transport/postfailure-exact-absence-read/stdout.json')
assert absence['runtime_original_result']==result and absence['claim_sha256']==digest(claim)
assert len(absence['exact_names'])==4 and all(x['absent'] and x['rc']==1 for x in absence['exact_names'])
assert absence['credential_files_absent'] and absence['container_count']==absence['post_intent_count']==0
assert dt.datetime.fromisoformat(absence['at_utc'])>dt.datetime.fromisoformat(result['finished_at_utc'])
original_supply=read('received/supply/FDS_D03_Supply_202610142110/result.json')
assert original_supply['status']=='SUPPLY_STOP' and len(original_supply['operations'])==3
assert all(x['rc']==0 for x in original_supply['operations'])
correction=read('received/supply/FDS_D03_SupplyValidation_202610142110/result.json')
assert correction['status']=='SUPPLY_VERIFIED_BY_OCI_DESCRIPTOR' and correction['supply_commands_retried']==0
assert correction['actual_image_id']==correction['config_descriptor_digest']==correction['platform_manifest']['config']['digest']
assert plan['images']['db'] in correction['repo_digests']
for app in correction['apps']:assert app['config_id']==plan['images'][app['role']]
provenance=read('provenance/SOURCE_PROVENANCE.json')
source_hashes={x['path']:x['sha256'] for x in provenance['files']}
assert all(source_hashes[name]==sha for name,sha in plan['files'].items())
assert digest(runtime/'stage/code/d03_lab.py')==plan['files']['tools/regression/d03_lab.py']
assert digest(runtime/'stage/code/d03_fixture.py')==plan['files']['tools/regression/d03_fixture.py']
patterns=[re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),re.compile(rb'github_pat_[A-Za-z0-9_]{20,}'),re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),re.compile(rb'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}')]
for row in index['files']:
    raw=(ROOT/row['path']).read_bytes()
    assert not any(p.search(raw) for p in patterns),'SENSITIVE_PATTERN: '+row['path']
summary={'evidence_verification':'PASS','packaged_inputs':len(index['files']),'direct_server_file_copies':sum(x['path'].startswith('received/') for x in index['files']),'manifest_entries_verified':manifest_items,'actual_runtime_result':'CLEANUP_FAILED','application_cases_executed':0,'post_intents':0,'automatic_retry':False,'postfailure_readback':'4 exact names absent; container0; credential files absent; claim preserved','production_runtime_claim':False}
print(json.dumps(summary,ensure_ascii=False,indent=2))
