"""Offline AC09 copy/semantic checks. No import or execution of captured tools."""
import argparse,base64,datetime as dt,decimal,hashlib,io,json,pathlib,re,tarfile,zipfile
H=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def need(ok,why):
 if not ok:raise ValueError(why)
def relative(root,name):
 p=root/name;need(not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts,'PATH_ESCAPE');return p
def rules(v):
 need(len(v)==4 and {x['rule_id'] for x in v}=={'R01','R02','R04','R07'},'RULE_IDS')
 return {x['rule_id']:(x['triggered'],x['detail']) for x in v}
def check_db(post,db):
 body=base64.b64decode(post['body_b64']);need(H(body)==post['body_sha256'],'HTTP_BODY_HASH')
 resp=json.loads(body);req=post['payload'];need(post['http']==201,'HTTP_201')
 need(db['matched_rows']==1 and len(db['rows'])==1,'DB_ROW_COUNT');row=db['rows'][0]
 for key in ['account_id','currency','transaction_type','source_ip']:need(row[key]==req[key],'DB_'+key)
 need(decimal.Decimal(str(row['amount']))==decimal.Decimal(str(req['amount'])),'DB_amount')
 need(dt.datetime.fromisoformat(row['occurred_at'])==dt.datetime.fromisoformat(req['occurred_at']),'DB_occurred_at')
 for key in ['transaction_id','fds_detected','fds_evaluation_skipped']:need(row[key]==resp[key],'DB_'+key)
 need(rules(row['fds_rules'])==rules(resp['fds_rules']),'DB_fds_rules')
 need(resp['fds_detected'] is False and resp['fds_evaluation_skipped'] is False,'FDS_NORMAL')
 need(all(v==(False,None) for v in rules(resp['fds_rules']).values()),'FDS_RULE_RESULT')
 dt.datetime.fromisoformat(row['received_at'])
 return resp['transaction_id']
PATTERNS={
 'PRIVATE_KEY_MATERIAL':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{32,}',
 'JWT_VALUE':rb'\beyJ[A-Za-z0-9_-]{16,}\.eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}',
 'GITHUB_TOKEN_VALUE':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
 'AWS_ACCESS_KEY_VALUE':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'BEARER_LITERAL':rb'(?i)authorization["\x27 ]*:["\x27 ]*bearer +[A-Za-z0-9._~-]{20,}',
}
def scan_bytes(raw,label,counts,depth=0):
 need(depth<16,'SCAN_DEPTH_LIMIT');counts['byte_streams']+=1
 for kind,pat in PATTERNS.items():need(re.search(pat,raw) is None,'SECRET_PATTERN '+kind+' '+label)
 try:v=json.loads(raw)
 except (ValueError,UnicodeDecodeError):return
 def walk(x,key=''):
  if isinstance(x,dict):
   for k,z in x.items():walk(z,k)
  elif isinstance(x,list):
   for z in x:walk(z,key)
  elif isinstance(x,str):
   if key.endswith('_b64') or key in ('base64','raw_base64'):
    try:b=base64.b64decode(x,validate=True)
    except ValueError:raise ValueError('INVALID_BASE64 '+label+' '+key)
    counts['decoded_base64']+=1;scan_bytes(b,label+'#'+key,counts,depth+1)
   elif x.lstrip().startswith(('{','[')):
    scan_bytes(x.encode(),label+'#json-string',counts,depth+1)
 walk(v)
def verify(root):
 runtime=root/'runtime';manifest=load(runtime/'EVIDENCE_MANIFEST.json')
 need(H((runtime/'EVIDENCE_MANIFEST.json').read_bytes())=='e5b950818d03ca73adc0bc56d98dc1a083e69853183a2c908fcd7bab516d185a','SEALED_MANIFEST_CHANGED')
 need(len(manifest['files'])==446,'SEALED_COUNT')
 for x in manifest['files']:need(H(relative(runtime,x['path']).read_bytes())==x['sha256'],'SEALED_FILE '+x['path'])
 provenance=load(root/'COPY_PROVENANCE.json')
 for x in provenance['files']:need(H(relative(root,x['copied_path']).read_bytes())==x['sha256'],'COPY_HASH '+x['copied_path'])
 bindings=load(runtime/'AUTHORIZATION_BINDINGS.json');expected={'R1':38693979785,'R2':38694721511}
 for phase,run in expected.items():
  b=bindings[phase];need(H((runtime/phase/'approval.json').read_bytes())==b['approval_sha256'],'APPROVAL_SHA')
  need(H((runtime/phase/b['record_name']).read_bytes())==b['record_sha256'],'RECORD_SHA')
  j=load(runtime/(phase.lower()+'-journal-final')/phase.lower()/'stdout.json');need(len(j['checkpoint_files'])==8 and j['chain_binding']=='MATCHED_CAPTURED_FILES','JOURNAL_CHAIN')
  receipt=j['checkpoint_files'][-1]['data']['receipt'];need(receipt['execution']['run_id']==run and receipt['execution']['attempt']==1,'RUN_BINDING')
  need(receipt['approval_sha256']==b['approval_sha256'] and receipt['plan_sha256']==b['plan_sha256'],'JOURNAL_APPROVAL')
  need(receipt['ROLLOUT']=='READY' and receipt['ROLLBACK']=='NOT_EXECUTED' and receipt['error_code']=='NONE','ROLLOUT_RESULT')
 for item in load(runtime/'github-final/RUN_SUMMARY.json'):
  run=load(runtime/'github-final'/item['label']/'run.json');jobs=load(runtime/'github-final'/item['label']/'jobs.json')['jobs']
  need(run['status']=='completed' and run['conclusion']=='success' and run['run_attempt']==1,'RUN_COMPLETE')
  need(run['head_sha']=='fddc76e1c261cd938f06211b7ed035fdcb32e606' and len(jobs)==1 and jobs[0]['conclusion']=='success','JOB_SOURCE')
 ret=load(runtime/'WINDOW_RETURN.json');need(ret['counts']=={'false_jobs':2,'true_jobs':2,'new_runner':0,'token_requests':2,'deposit_posts':2,'edge_extra_gets':4,'manual_recovery_patch':0},'EXECUTION_COUNTS')
 need(ret['old_pods']==ret['restart_count']==ret['runner_worker']==ret['own_sockets']==0 and ret['current_ready']=={'transaction-api':3,'fds-engine':3},'RETURN_STATE')
 dbrows=[json.loads(x) for x in (root/'db-central/reconstructed-console-files/db-after.jsonl').read_text().splitlines()]
 need(dbrows[0]['transaction_read_only']=='on','READ_ONLY_DB')
 ids=[]
 for phase in ['R1','R2']:
  db=next(x for x in dbrows if x.get('phase')==phase);ids.append(check_db(load(runtime/(phase.lower()+'-post-one')/'stdout.json'),db))
 sec=load(root/'references/sec-post.json')
 need(sec['id']==6187360015 and sec['user']['login']=='hayeounglee' and sec['created_at']=='2026-10-15T07:58:21Z','SEC_ORIGIN')
 need('15/30분 노출 상한을 충족한 것으로 판정' in sec['body'] and '사고 처리 대상이 아닙니다' in sec['body'],'SEC_DISPOSITION')
 need(load(runtime/'TIMING_ASSESSMENT.json')['TIMING_PROOF']=='시한 미입증 / SEC 사후 검토','ORIGINAL_TIMING_PRESERVED')
 counts={'byte_streams':0,'decoded_base64':0,'archive_members':0}
 for p in sorted(root.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  label=p.relative_to(root).as_posix();raw=p.read_bytes();scan_bytes(raw,label,counts)
  if p.name.endswith('.zip'):
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for item in z.infolist():
     if item.is_dir():continue
     need(item.file_size<10*1024*1024,'ARCHIVE_MEMBER_BOUND');scan_bytes(z.read(item),label+'!'+item.filename,counts);counts['archive_members']+=1
  elif p.name.endswith(('.tar','.tar.gz','.tgz','.tar.xz')):
   with tarfile.open(fileobj=io.BytesIO(raw)) as z:
    for item in z.getmembers():
     if item.isdir():continue
     need(item.isfile() and item.size<10*1024*1024,'ARCHIVE_SPECIAL_OR_OVERSIZE');scan_bytes(z.extractfile(item).read(),label+'!'+item.name,counts);counts['archive_members']+=1
 return {'result':'PASS','sealed_files':446,'copied_files':len(provenance['files']),'db_same_id_rows':ids,'sec_disposition':'CONDITIONS_SATISFIED_NOT_INCIDENT_SINGLE_ROUND_CLOSED','mathematical_interval_bound':'UNPROVEN_PRESERVED','counts':ret['counts'],'secret_pattern_scan':counts,'secret_scan_limit':'Bounded recognizable patterns plus JSON/base64/archive decoding; independent human evidence review still required','new_runtime':False,'independent_review':'NOT_PERFORMED_FOR_THIS_CANDIDATE'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();print(json.dumps(verify(a.root),ensure_ascii=False,indent=2))
