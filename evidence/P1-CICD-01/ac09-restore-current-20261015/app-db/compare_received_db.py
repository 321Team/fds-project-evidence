"""Independent new DB/API comparison only. Never rerun SQL or prior metrics checks."""
import base64, datetime as dt, hashlib, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CENTRAL=ROOT/'deliverables/phase1-central-control-20261015'
PREP=ROOT/'deliverables/p1-cicd-ac09-preparation-20261015'
PREVIOUS=HERE.parent/'runtime-1535'
REF=HERE/'references';REF.mkdir(exist_ok=True)
sources=[]

def sha(b):return hashlib.sha256(b).hexdigest()
def preserve(name,b,source):
    p=REF/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==b, f'Existing source differs: {name}'
    else:p.write_bytes(b)
    sources.append(dict(local=name,source=str(source),sha256=sha(b),bytes=len(b)))
    return b
def read(name,path):return preserve(name,path.read_bytes(),path)

raw=read('USER_CONSOLE_OUTPUT.txt',CENTRAL/'db-post-162217/USER_CONSOLE_OUTPUT.txt')
lines=raw.splitlines(keepends=True)
assert lines[0].decode().strip()=='AC09_DB_AFTER_RC=0'
hash_start=next(i for i,line in enumerate(lines) if re.fullmatch(rb'[0-9a-f]{64}  DB_POST_READONLY.sql\r?\n',line))
hash_text=b''.join(lines[hash_start:]).decode()
reported=dict((name,digest) for digest,name in re.findall(r'^([0-9a-f]{64})  (\S+)\s*$',hash_text,re.M))
assert len(reported)==7
data=b''.join(lines[1:hash_start]); data_lines=data.splitlines(keepends=True)
host=b''.join(data_lines[:2]);start=data_lines[2]
remainder=b''.join(data_lines[3:]).decode('utf-8')
decoder=json.JSONDecoder();pos=0;objects=[]
for _ in range(3):
    while remainder[pos].isspace():pos+=1
    obj,pos=decoder.raw_decode(remainder,pos);objects.append(obj)
assert remainder[pos:].startswith(('\n','\r\n'))
pos+=2 if remainder[pos:].startswith('\r\n') else 1
db_raw=remainder[:pos].encode('utf-8');tail=remainder[pos:]
m=re.search(r'(?m)^([0-9]+)(\r?\n)([^\r\n]+)(\r?\n)\Z',tail)
assert m
stderr=tail[:m.start()].encode();rc=(m[1]+m[2]).encode();end=(m[3]+m[4]).encode()
assert host+start+db_raw+stderr+rc+end==data
sql=read('DB_POST_READONLY.sql',PREVIOUS/'DB_POST_READONLY_PREPARED.sql')
files={'DB_POST_READONLY.sql':sql,'host.txt':host,'start.txt':start,'db-after.jsonl':db_raw,
       'db-after.stderr':stderr,'db-after.rc':rc,'end.txt':end}
integrity=[]
for name,value in files.items():
    preserve('literal-files/'+name,value,'Literal slice of user transcript' if name!='DB_POST_READONLY.sql' else 'Previously prepared fixed SQL')
    integrity.append(dict(name=name,bytes=len(value),reported_sha256=reported[name],actual_sha256=sha(value),match=reported[name]==sha(value)))
assert all(x['match'] for x in integrity)
assert host.decode().splitlines()==['db01','server08'] and int(m[1])==0 and stderr==b''
identity=objects[0]
assert identity['kind']=='identity'
assert all(identity[k]==v for k,v in {'database':'fdsdb','user':'postgres','timezone':'Asia/Seoul','transaction_read_only':'on'}.items())
rows={x['phase']:x for x in objects[1:]}
assert set(rows)=={'R1','R2'}
comparisons=[]
expected_keys={'transaction_id','account_id','amount','currency','transaction_type','source_ip','occurred_at','received_at','fds_detected','fds_rules','fds_evaluation_skipped'}
for phase in ['R1','R2']:
    original=read(phase+'-post-one.json',PREVIOUS/'references'/(phase.lower()+'-post-one')/'stdout.json')
    post=json.loads(original);body=base64.b64decode(post['body_b64'],validate=True)
    assert sha(body)==post['body_sha256'] and len(body)==post['body_bytes'] and not post['truncated']
    response=json.loads(body);payload=post['payload'];observed=rows[phase]
    assert observed['kind']=='business_rows' and observed['matched_rows']==1 and len(observed['rows'])==1
    row=observed['rows'][0];assert set(row)==expected_keys
    assert observed['expected_account_id']==payload['account_id'] and observed['expected_transaction_id']==response['transaction_id']
    checks={k:row[k]==payload[k] for k in ['account_id','amount','currency','transaction_type','source_ip']}
    checks.update({k:row[k]==response[k] for k in ['transaction_id','fds_detected','fds_rules','fds_evaluation_skipped']})
    request_time=dt.datetime.fromisoformat(payload['occurred_at']);stored_time=dt.datetime.fromisoformat(row['occurred_at'])
    assert request_time.tzinfo is not None and stored_time.tzinfo is not None
    checks['occurred_at_same_instant']=request_time==stored_time
    assert all(checks.values())
    received=dt.datetime.fromisoformat(row['received_at'])
    assert received.tzinfo is not None
    interval=dt.datetime.fromisoformat(post['started_utc'])<=received<=dt.datetime.fromisoformat(post['finished_utc'])
    comparisons.append(dict(phase=phase,transaction_id=row['transaction_id'],account_id=row['account_id'],matched_rows=1,
        compared_fields=checks,received_at=row['received_at'],received_at_role='DB_ONLY_OBSERVATION_NOT_API_EQUALITY_FIELD',
        received_at_within_http_interval=interval,interval_is_acceptance_or_latency_test=False,
        api_body_sha256=sha(body),result='SAME_ID_DB_ROW_CONTENT_MATCH'))

# Pin which documents the user approved; do not infer a new execution condition.
auth=json.loads(read('AC09_USER_AUTHORIZATION_1535.json',CENTRAL/'AC09_USER_AUTHORIZATION_1535.json'))
card=read('FINAL_DECISION_CARD.md',CENTRAL/auth['card'])
detail=read('FINAL_OPERATOR_CARD.md',PREP/'round5/FINAL_OPERATOR_CARD.md')
assert sha(card)==auth['card_sha256'] and sha(detail)==auth['detail_card_sha256'] and auth['approved'] is True
old=read('EARLIER_UNAPPROVED_EXECUTION_CARD.md',PREP/'EXECUTION_CARD.md')
assert 'RUNTIME_NOT_AUTHORIZED' in old.decode('utf-8-sig')
before_states={}
for phase in ['r1','r2']:
    attempt=json.loads(read(phase+'-post-attempt.json',PREVIOUS/'references'/(phase+'-post-attempt.json')))
    before_states[phase]=attempt['db_before']
result=dict(at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds'),
    provenance='USER_DB_CONSOLE_TEXT_AND_EXISTING_ACTUAL_POST_SNAPSHOTS',
    original_transcript_sha256=sha(raw),literal_slices_rejoin_exactly=True,whitespace_changed=False,
    integrity=integrity,identity=identity,rc=0,stderr_empty=True,phase_comparisons=comparisons,
    approved_card_sha256=sha(card),approved_detail_card_sha256=sha(detail),
    db_pre_zero_history=before_states,
    pre_zero_assessment='HISTORY_LIMIT_NOT_AN_ADOPTED_MANDATORY_ENTRY_CONDITION_IN_PINNED_FINAL_CARDS',
    business_post_rows='VERIFIED_TWO_MINIMUM_SAMPLES',all_rules_or_history_queries='NOT_TESTED_BY_THIS_SAMPLE',
    prior_metrics_checks='REUSED_NOT_RERUN',catalog='REUSED_NOT_REQUERIED',
    new_sql=0,new_post=0,new_remote_connections=0,sealed_evidence_modified=False,
    ac09_acceptance='NOT_DECLARED_SEC_AND_FINAL_REVIEW_SEPARATE')
(HERE/'DB_APP_COMPARISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'SOURCE_INDEX.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['at_kst','original_transcript_sha256','business_post_rows','pre_zero_assessment','ac09_acceptance']},ensure_ascii=False))
print(json.dumps(dict(integrity_matches=sum(x['match'] for x in integrity),phases=[dict(phase=x['phase'],fields_match=all(x['compared_fields'].values()),received_at=x['received_at']) for x in comparisons]),ensure_ascii=False))
