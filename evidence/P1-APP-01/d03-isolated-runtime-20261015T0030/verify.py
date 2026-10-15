"""Offline byte and raw-command reconciliation; does not start any Runtime."""
import datetime as dt
import hashlib
import json
import pathlib
import re

ROOT=pathlib.Path(__file__).resolve().parent
RUN='202610150030'
CASES=['PRE','READ','READ_POST','HTTP','HTTP_POST','DB','DB_POST']
METRICS=['transaction_save_success_total','transaction_save_failure_total','fds_evaluation_error_total']
def load(name):return json.loads((ROOT/name).read_bytes())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
index=load('RECEIVED_INDEX.json')
for row in index['files']:
    path=ROOT/row['path'];assert path.resolve().is_relative_to(ROOT)
    assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],row['path']
entries=0
for manifest in (ROOT/'received').rglob('SHA256SUMS'):
    for line in manifest.read_text().splitlines():
        expected,name=line.split('  ',1);path=manifest.parent/name
        assert path.resolve().is_relative_to(manifest.parent) and digest(path)==expected
        entries+=1
rt=ROOT/'received/runtime'/('FDS_D03_'+RUN)
result=json.loads((rt/'result.json').read_bytes())
assert result['result']=='LAB_RUNTIME_PASS' and result['failure'] is None
assert result['cleanup_confirmed'] is True and result['production_runtime_claim'] is False
commands={p.name:json.loads(p.read_bytes()) for p in sorted(rt.glob('*-command.json'))}
assert len(commands)==91
def cmd(n):return commands[f'{n:03d}-command.json']
def stdout(n):assert cmd(n)['rc']==0;return cmd(n)['stdout'].strip()
def response(n):return json.loads(stdout(n))
def metrics(n):
    data=response(n);assert data['status']==200
    return {k:float(re.search(r'^'+k+r' ([0-9.eE+-]+)$',data['body'],re.M).group(1)) for k in METRICS}
assert [(n,c['rc']) for n,c in commands.items() if c['rc']!=0]==[
    ('009-command.json',2),('022-command.json',1),('076-command.json',1),
    ('081-command.json',1),('086-command.json',1),('091-command.json',1)]
assert not any(c['timed_out'] for c in commands.values())
identities={r:json.loads((rt/(r+'-identity.json')).read_bytes()) for r in ('db','engine','fixture','api')}
assert len({x['cid'] for x in identities.values()})==4
for role,n in [('db',6),('engine',13),('fixture',16),('api',19)]:
    identity=identities[role];c=cmd(n)
    assert c['argv'][0]=='create' and stdout(n)==identity['cid']
    assert identity['name']=='fds-d03-'+RUN+'-'+role and identity['label']=='fds.d03.run='+RUN
    assert all(x in c['argv'] for x in ('--pull=never','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--timeout=900'))
    assert cmd(n+2)['argv']==['start',identity['cid']] and cmd(n+2)['rc']==0
    isolation=json.loads((rt/(role+'-isolation.json')).read_bytes())
    assert isolation['read_only'] and not isolation['privileged'] and not isolation['port_bindings']
    assert isolation['network_mode']==('none' if role=='db' else 'container:'+identities['db']['cid'])
assert sum(c['argv'][0]=='create' for c in commands.values())==4
assert sum(c['argv'][0]=='start' for c in commands.values())==4
assert stdout(11)=='fds_lab|postgres|0003' and stdout(12).startswith('PostgreSQL 16.8 ')
assert stdout(31)=='0'
net=json.loads((rt/'loopback-namespace.json').read_bytes());assert net['interfaces']==['lo'] and net['ipv4_routes']==[]
assert [response(n)['status'] for n in (27,28,29,30)]==[404,404,200,200]
assert [response(n)['status'] for n in (23,24,25,69,70,71)]==[200]*6
triplets={'PRE':(33,34,35,36),'READ':(37,38,39,40),'READ_POST':(41,42,43,44),
          'HTTP':(45,46,47,48),'HTTP_POST':(49,50,51,52),'DB':(53,55,56,57),'DB_POST':(61,62,63,64)}
case_summary=[]
for case in CASES:
    before,post,after,sql=triplets[case]
    c=json.loads((rt/(case+'-result.json')).read_bytes())
    intent=json.loads((rt/(case+'-post-intent.json')).read_bytes())
    assert c['case']==intent['case']==case and cmd(post)['argv'][-3:]==['_request',RUN,case]
    assert c['response']==response(post) and c['rows']==response(sql)
    assert c['before']==metrics(before) and c['after']==metrics(after)
    assert dt.datetime.fromisoformat(intent['at_utc'])<=dt.datetime.fromisoformat(cmd(post)['started_at_utc'])
    skipped=case in ('READ','HTTP');body=json.loads(c['response']['body'])
    delta=[c['after'][k]-c['before'][k] for k in METRICS]
    assert delta==([0,1,0] if case=='DB' else [1,0,int(skipped)])
    if case=='DB':
        assert c['response']['status']==500 and body=={'detail':'transaction save failed'} and c['rows']==[]
    else:
        assert c['response']['status']==201 and len(c['rows'])==1
        row=c['rows'][0]
        assert row['transaction_id']==body['transaction_id'] and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',body['transaction_id'])
        for field in ('fds_detected','fds_rules','fds_evaluation_skipped'):assert row[field]==body[field]
        assert row['fds_evaluation_skipped'] is skipped
        for field in ('account_id','amount','currency','transaction_type','source_ip'):assert row[field]==intent['payload'][field]
        assert dt.datetime.fromisoformat(row['occurred_at'])==dt.datetime.fromisoformat(intent['payload']['occurred_at'])
        if skipped:assert row['fds_detected'] is None and row['fds_rules'] is None
        else:
            assert row['fds_detected'] is False and len(row['fds_rules'])==4
            assert {r['rule_id'] for r in row['fds_rules']}=={'R01','R02','R04','R07'}
            assert all(r['triggered'] is False for r in row['fds_rules'])
    if case=='READ':assert 1.8<=c['response']['elapsed']<8
    case_summary.append({'case':case,'http':c['response']['status'],'stored':len(c['rows']),'metrics_delta':delta})
assert len(list(rt.glob('*-post-intent.json')))==7
assert len([c for c in commands.values() if '_request' in c['argv']])==7
assert not list(rt.glob('*-errors.json'))
assert 'CREATE TRIGGER d03_insert_fail' in cmd(54)['stdin'] and cmd(54)['rc']==0
assert 'DROP TRIGGER d03_insert_fail' in cmd(58)['stdin'] and cmd(58)['rc']==0 and stdout(59)=='0'
db_log=stdout(68)+cmd(68)['stderr']
markers=list(re.finditer(r'^D03 \[(\d+)\] LOG:  D03_INJECT_'+RUN+r'$',db_log,re.M))
assert len(markers)==1 and markers[0].group(1)=='84'
assert re.search(r'^D03 \[84\] LOG:  statement: ROLLBACK;$',db_log[markers[0].end():],re.M)
assert 'schema 0003 적용 완료' in db_log and '20-d03-logging.sh' in db_log
assert 'Permission denied' not in db_log
events=[json.loads(line) for line in stdout(67).splitlines() if line.startswith('{')]
received=[e for e in events if e['event']=='request_received']
assert [e['case'] for e in received]==CASES
for e in received:
    assert e['run']==RUN and e['mode']=={'READ':'read-timeout','HTTP':'http-500'}.get(e['case'],'real-engine')
    if e['case']!='DB':assert e['transaction_id']==json.loads((rt/(e['case']+'-result.json')).read_bytes())['rows'][0]['transaction_id']
assert len([e for e in events if e['event']=='http500_sent' and e['case']=='HTTP'])==1
rows=response(65);assert len(rows)==6 and len({r['transaction_id'] for r in rows})==6
assert {r['account_id'] for r in rows}=={'SIM_d03_'+RUN+'_'+c for c in CASES if c!='DB'}
assert [metrics(66)[k]-metrics(32)[k] for k in METRICS]==[6,1,2]
verified=json.loads((rt/'verified-cases.json').read_bytes())
assert verified['response_db_transactions']==rows and verified['rollback_pid']==84
assert verified['cases']==CASES and verified['posts']==7 and verified['stored']==6
clean=json.loads((rt/'cleanup.json').read_bytes());assert len(clean)==4 and all(x['absent'] for x in clean)
for role,n in [('api',75),('fixture',80),('engine',85),('db',90)]:
    cid=identities[role]['cid'];assert cmd(n)['argv']==['rm','--force','--time=5',cid] and cmd(n)['rc']==0
    assert cmd(n+1)['argv']==['container','exists',cid] and cmd(n+1)['rc']==1
plan=load('decisions/plan.json');auth=load('decisions/authorization.json');decision=load('decisions/USER_DECISION.json')
assert plan['run']==RUN and plan['max_posts']==7 and not plan['production_runtime_claim']
assert digest(ROOT/'decisions/plan.json')==auth['plan_sha256']=='a051a3f06ab885e258f1a2fa4f7ea0431999f095dd6f5cd369200d4cfe13a265'
assert decision['direct_user_message']=='착수' and decision['authorization']==auth
assert all(auth[k] is True for k in ('approved','runner_exclusive','lab_db_image_accepted'))
assert load('records/USER_AUTHORIZATION_GITHUB_READBACK.json')['html_url']==auth['user_authorization_reference']
assert (rt/'plan.json').read_bytes()==(ROOT/'decisions/plan.json').read_bytes()
assert json.loads((rt/'authorization.json').read_bytes())==auth
receipt=load('received/runtime/FDS_D03_RuntimeInvocation_'+RUN+'/receipt.json')
assert receipt['rc']==0 and receipt['automatic_retry'] is False
assert dt.datetime.fromisoformat(auth['start_after'])<=dt.datetime.fromisoformat(receipt['started_at_utc'])<=dt.datetime.fromisoformat(auth['start_before'])
assert dt.datetime.fromisoformat(receipt['finished_at_utc'])<dt.datetime.fromisoformat(auth['finish_before'])
readback=load('records/POSTRUN_READBACK.json')
assert readback['runtime_original_result']==result and not readback['containers'] and readback['credential_files_absent'] and readback['post_intent_count']==7
assert len(readback['exact_names'])==4 and all(x['rc']==1 and x['absent'] for x in readback['exact_names'])
assert readback['claim_sha256']==digest(ROOT/'received/runtime/FDS_D03_Claims'/f'{RUN}.json')
assert dt.datetime.fromisoformat(result['finished_at_utc'])<dt.datetime.fromisoformat(readback['at_utc'])<dt.datetime.fromisoformat(auth['finish_before'])
modes={x['path'].split('/FDS_D03_'+RUN)[-1]:x for x in readback['modes']}
assert all(modes[n]['mode']=='0o700' for n in ('','/stage'))
assert all(modes[n]['mode']=='0o755' for n in ('/stage/code','/stage/hooks'))
assert all(modes[n]['mode']=='0o644' for n in ('/stage/code/d03_lab.py','/stage/hooks/10-fds-schema.sh','/stage/hooks/fds-schema.sql','/stage/hooks/20-d03-logging.sh'))
assert readback['ls_context']['stdout'].count('container_file_t:s0')==2
provenance=load('provenance/SOURCE_PROVENANCE.json')
assert provenance['merge_commit']=='6531b51c991535794c1f9705dc14f199001d1961' and provenance['approved_head']=='60f463f6ac8096546e71384696606f30aaa17823'
hashes={x['path']:x['sha256'] for x in provenance['files']};assert all(hashes[n]==h for n,h in plan['files'].items())
for n in ('d03_lab.py','d03_fixture.py'):assert digest(rt/'stage/code'/n)==plan['files']['tools/regression/'+n]
helper=load('received/helper/result.json');assert helper['status']=='HELPER_PASS_RUNTIME_NOT_RUN' and helper['helper']['rc']==0
assert helper['bundle']['sha256']=='d05f89052b2d1611ad59f832a381c450482e31c867dd74975b3a8c555e26ceef'
fresh=load('transport/runner-read-after-ac07/stdout.json');assert fresh['container_count']==0 and not fresh['worker_pids'] and fresh['rootless']
assert len(fresh['images'])==3 and all(x['matches'] for x in fresh['images'])
assert not any(p.name in ('db.env','api.env') for p in ROOT.rglob('*'))
patterns=[rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}']
for row in index['files']:
    raw=(ROOT/row['path']).read_bytes();assert not any(re.search(p,raw) for p in patterns),row['path']
print(json.dumps({'evidence_verification':'PASS','packaged_inputs':len(index['files']),'direct_server_file_copies':sum(x['path'].startswith('received/') for x in index['files']),'server_manifest_entries':entries,'actual_runtime_result':'LAB_RUNTIME_PASS','cleanup_confirmed':True,'cases':case_summary,'posts':7,'stored':6,'rollback_pid':84,'automatic_retry':False,'postrun_names_absent':4,'production_runtime_claim':False},indent=2))
