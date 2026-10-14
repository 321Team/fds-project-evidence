from pathlib import Path
import subprocess,json,datetime
R=Path(__file__).resolve().parent
records={}
for repo,num,sha in [('fds-project-evidence',221,'fb931f5a59032607bd051206c192a77168c5752c'),('infra-kubernetes',86,'d53ce00f318785b97577d41c07d8309ff581c2a8')]:
 def api(path):return json.loads(subprocess.check_output(['gh','api','repos/321Team/'+repo+'/'+path]))
 p=api('pulls/'+str(num));reviews=api('pulls/'+str(num)+'/reviews');checks=api('commits/'+sha+'/check-runs')
 assert p['merged'] and p['head']['sha']==sha
 assert any(r['state']=='APPROVED' and r['commit_id']==sha and r['user']['login']=='supreme33-kr' for r in reviews)
 records[repo+'#'+str(num)]={'head':sha,'merged':p['merged'],'merged_at':p['merged_at'],'merge_commit_sha':p['merge_commit_sha'],'reviews':[{k:r[k] for k in ('id','state','commit_id','submitted_at','body','html_url')}|{'user':r['user']['login']} for r in reviews],'checks':[{k:c[k] for k in ('name','status','conclusion','head_sha','html_url')} for c in checks['check_runs']]}
(R/'GITHUB_MERGE_REVIEW_RECEIPT.json').write_text(json.dumps({'read_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
