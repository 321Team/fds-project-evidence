"""Offline consistency verification of a FAILED run, never Runtime PASS."""
import datetime as dt,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
def load(name):return json.loads((ROOT/name).read_bytes())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
index=load('RECEIVED_INDEX.json')
for row in index['files']:
    path=ROOT/row['path'];assert path.resolve().is_relative_to(ROOT.resolve())
    assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],row['path']
entries=0
for manifest in (ROOT/'received').rglob('SHA256SUMS'):
    for line in manifest.read_text().splitlines():
        sha,name=line.split('  ',1);path=manifest.parent/name
        assert path.resolve().is_relative_to(manifest.parent.resolve()) and digest(path)==sha
        entries+=1
runtime=ROOT/'received/runtime/FDS_D03_202610150000'
result=json.loads((runtime/'result.json').read_bytes())
assert result['result']=='FAILED' and result['cleanup_confirmed'] is True and result['production_runtime_claim'] is False
assert result['failure']=={'type':'RuntimeError','message':'COMMAND_FAILED 11'}
commands=[json.loads(p.read_bytes()) for p in sorted(runtime.glob('*-command.json'))]
assert len(commands)==16
assert sum(x['argv'][0]=='create' for x in commands)==1
assert sum(x['argv'][0]=='start' for x in commands)==1
created=commands[5];assert created['argv'][0]=='create' and created['rc']==0
assert '--tmpfs=/var/lib/pgsql:rw,size=768m,mode=0770' in created['argv']
cid=created['stdout'].strip();assert re.fullmatch('[0-9a-f]{64}',cid)
assert commands[7]['argv']==['start',cid] and commands[7]['rc']==0
assert commands[9]['argv']==['exec',cid,'/usr/libexec/check-container'] and commands[9]['rc']==0
failed=commands[10]
assert failed['rc']==3 and 'relation "alembic_version" does not exist' in failed['stderr']
assert 'SELECT current_database()' in failed['stdin']
logs=commands[13];assert logs['argv']==['logs',cid] and logs['rc']==0
assert "find: '/opt/app-root/src/postgresql-start': Permission denied" in logs['stderr']
assert 'Starting server...' in logs['stdout']
assert commands[14]['argv']==['rm','--force','--time=5',cid] and commands[14]['rc']==0
assert commands[15]['argv']==['container','exists',cid] and commands[15]['rc']==1
assert json.loads((runtime/'cleanup.json').read_bytes())==[{'name':'fds-d03-202610150000-db','absent':True}]
assert not list(runtime.glob('*-post-intent.json')) and not list(runtime.glob('*-result.json')) and not (runtime/'verified-cases.json').exists()
plan=load('decisions/plan.json');auth=load('decisions/authorization.json');decision=load('decisions/USER_DECISION.json')
assert plan['run']=='202610150000' and plan['max_posts']==7 and not plan['production_runtime_claim']
assert digest(ROOT/'decisions/plan.json')==auth['plan_sha256']=='256dbf22a82600ed78212e1f862669b62cf1cea49d79559c3addf31bf7ea6ef6'
assert all(auth[k] is True for k in ('approved','runner_exclusive','lab_db_image_accepted'))
assert decision['direct_user_message']=='실행창 비어있음. 지금 착수' and decision['authorization']==auth
assert load('records/USER_AUTHORIZATION_GITHUB_READBACK.json')['html_url']==auth['user_authorization_reference']
assert (runtime/'plan.json').read_bytes()==(ROOT/'decisions/plan.json').read_bytes()
assert json.loads((runtime/'authorization.json').read_bytes())==auth
receipt=load('received/runtime/FDS_D03_RuntimeInvocation_202610150000/receipt.json')
assert receipt['rc']==1 and receipt['automatic_retry'] is False
assert dt.datetime.fromisoformat(auth['start_after'])<=dt.datetime.fromisoformat(receipt['started_at_utc'])<=dt.datetime.fromisoformat(auth['start_before'])
assert dt.datetime.fromisoformat(receipt['finished_at_utc'])<dt.datetime.fromisoformat(auth['finish_before'])
readback=load('records/POSTFAILURE_READBACK.json')
assert readback['runtime_original_result']==result and not readback['containers'] and readback['credential_files_absent'] and readback['post_intent_count']==0
assert len(readback['exact_names'])==4 and all(x['rc']==1 and x['absent'] for x in readback['exact_names'])
assert readback['claim_sha256']==digest(ROOT/'received/runtime/FDS_D03_Claims/202610150000.json')
assert dt.datetime.fromisoformat(readback['at_utc'])>dt.datetime.fromisoformat(result['finished_at_utc'])
modes={x['path'].split('/FDS_D03_202610150000')[-1]:x for x in readback['modes']}
assert all(modes[name]['mode']=='0o700' for name in ('','/stage','/stage/code','/stage/hooks'))
assert all(modes[name]['mode']=='0o644' for name in ('/stage/code/d03_lab.py','/stage/hooks/10-fds-schema.sh','/stage/hooks/fds-schema.sql','/stage/hooks/20-d03-logging.sh'))
assert 'container_file_t:s0' in readback['ls_context']['stdout']
provenance=load('provenance/SOURCE_PROVENANCE.json')
assert provenance['merge_commit']=='016390855fcec335e941b811123bb11b88015610' and provenance['approved_head']=='cbbdd90424829e9f0062db5be13cd1814d7a2f54'
hashes={x['path']:x['sha256'] for x in provenance['files']}
assert all(hashes[name]==sha for name,sha in plan['files'].items())
for name in ('d03_lab.py','d03_fixture.py'):assert digest(runtime/'stage/code'/name)==plan['files']['tools/regression/'+name]
helper=load('received/helper/result.json');assert helper['status']=='HELPER_PASS_RUNTIME_NOT_RUN' and helper['helper']['rc']==0
assert helper['bundle']['sha256']=='ebc6c6439f29bdffd2b2d5cefade592636ed93e5309cdc607ce2dc0da2807f1d'
fresh=load('transport/runner-read-after-ac07/stdout.json')
assert fresh['container_count']==0 and not fresh['worker_pids'] and fresh['rootless']
assert len(fresh['images'])==3 and all(x['matches'] for x in fresh['images'])
assert next(x['id'] for x in fresh['images'] if x['role']=='db')=='sha256:5f7659016ef769811a0fdc349c9cad11f520dc7e147633bb1025e499002d9cd2'
assert not any(p.name in ('db.env','api.env') for p in ROOT.rglob('*'))
patterns=[rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}']
for row in index['files']:
    raw=(ROOT/row['path']).read_bytes();assert not any(re.search(p,raw) for p in patterns),row['path']
print(json.dumps({'evidence_verification':'PASS','packaged_inputs':len(index['files']),'direct_server_file_copies':sum(x['path'].startswith('received/') for x in index['files']),'server_manifest_entries':entries,'actual_runtime_result':'FAILED','cleanup_confirmed':True,'db_create':1,'db_start':1,'post_intents':0,'cases':0,'automatic_retry':False,'postfailure_names_absent':4,'production_runtime_claim':False},indent=2))
