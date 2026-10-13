"""Record the explicit user decision once. No server staging or dispatch."""
import datetime,hashlib,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).parent.resolve();AUTH=OUT/'authorization';AUTH.mkdir(exist_ok=False)
sha=lambda x:hashlib.sha256(x).hexdigest()
def rawjson(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def api(endpoint,method='GET',obj=None,label='read'):
 argv=['gh','api',endpoint]
 if obj is not None:
  path=AUTH/(label+'.request.json');path.write_bytes(rawjson(obj));argv+=['--method',method,'--input',str(path)]
 r=subprocess.run(argv,capture_output=True,timeout=30)
 (AUTH/(label+'.response.json')).write_bytes(r.stdout);(AUTH/(label+'.stderr.txt')).write_bytes(r.stderr)
 assert r.returncode==0,'API_UNCONFIRMED_DO_NOT_REPEAT_MUTATION'
 return json.loads(r.stdout)
assert api('user',label='actor')['login']=='GWONUK'
plan_raw=(OUT/'deploy-plan.unapproved.json').read_bytes();plan=json.loads(plan_raw)
assert sha(plan_raw)=='ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4'
proposal=json.loads((OUT/'EXECUTION_PROPOSAL.json').read_bytes())
body='CODEX_ASSISTED · 사용자 “제안 범위 허용·콘솔 대기·비중첩 확보” 수신. PR219의23:15~23:25 실제 시작/00:15 정리, 준비→false1→true Deploy1·TokenRequest1, 지정 이전 image 조건부 복귀를 허용했습니다. 이 댓글을 exact approval JSON 원문으로 결속 중입니다. 독립 입력 검토·직전 조건은 유지하며 아직 배치·발급·Deploy하지 않았습니다.'
comment=api('repos/321Team/infra-cicd/issues/11/comments','POST',{'body':body},'created')
approval={'schema':'P1-CICD-deploy-approval-2','template_only':False,'plan_sha256':sha(plan_raw),'workflow':plan['workflow'],'reference':comment['html_url'],'approved_by':'GWONUK','not_before':proposal['not_before_kst'],'expires_at':proposal['finish_kst'],'allow_rollback':True}
approval_raw=rawjson(approval);(AUTH/'approval.json').write_bytes(approval_raw)
endpoint='repos/321Team/infra-cicd/issues/comments/'+str(comment['id'])
before=api(endpoint,label='before');assert before['body']==body and before['user']['login']=='GWONUK'
api(endpoint,'PATCH',{'body':approval_raw.decode()},'updated')
after=api(endpoint,label='readback');assert after['body'].encode()==approval_raw and after['user']['login']=='GWONUK'
push_raw=(OUT/'push-result.original.json').read_bytes();uid=json.loads((OUT/'PLAN_VALIDATION.json').read_bytes())['sa_uid']
record={'schema':'P1-CICD-deploy-inputs-1','plan':plan_raw.decode(),'approval':approval_raw.decode(),'push_receipt':push_raw.decode(),'sa_uid':uid}
record_raw=rawjson(record);name='deploy-'+plan['request_id']+'.json';(AUTH/name).write_bytes(record_raw)
sys.path.insert(0,str(OUT/'source'));sys.dont_write_bytecode=True
import deploy_plan
binding=deploy_plan.validate(plan_raw,approval_raw,push_raw,sha(plan_raw),sha(approval_raw),dict(plan['workflow'],run_id=1,attempt=1),datetime.datetime.fromisoformat(proposal['not_before_kst']))
assert binding['binding']=='MATCH'
audit={'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision_source':'Current user reply: 제안 범위 허용·콘솔 대기·비중첩 확보','proposal':'https://github.com/321Team/fds-project-evidence/pull/219','comment_url':after['html_url'],'comment_id':after['id'],'author':after['user']['login'],'comment_readback_exact':True,'plan_sha256':sha(plan_raw),'approval_sha256':sha(approval_raw),'record_name':name,'record_sha256':sha(record_raw),'full_pure_byte_validation':'MATCH','static_context':'Run1 / Attempt1 at proposed start; no actual Deploy Run created','source_commit':plan['workflow']['workflow_sha'],'sa_uid':uid,'independent_input_review':'PENDING','not_before_kst':proposal['not_before_kst'],'actual_start_deadline_kst':proposal['actual_start_deadline_kst'],'finish_kst':proposal['finish_kst'],'broker_authorization_expires_utc':proposal['broker_authorization_expires_utc'],'false_runs_allowed':1,'true_runs_allowed':1,'token_requests_allowed':1,'automatic_reruns_allowed':0,'console':'이권욱 confirmed available','nonoverlap':'User confirmed Harbor change/H6/post-observation and other APP/DB/MON changes excluded; entry recheck required','staging':'NOT_PERFORMED','dispatch':'NOT_PERFORMED','token_issued':False,'Deploy':'NOT_EXECUTED','rollback_limit':'Only exact previous images when existing engine confirms applied state and authority/window; business-port /metrics returns; no permanent risk acceptance'}
(AUTH/'AUTHORIZATION_BINDING.json').write_bytes(rawjson(audit));print(json.dumps(audit,ensure_ascii=False))
