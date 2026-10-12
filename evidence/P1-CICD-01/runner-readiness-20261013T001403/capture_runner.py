import datetime,hashlib,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
out={'at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'scope':'GitHub REST read only; no workflow dispatch, registration or credential issuance','queries':[]}
for path in ['repos/321Team/infra-ansible/actions/runs?status=queued&per_page=100','repos/321Team/infra-ansible/actions/runs?status=in_progress&per_page=100','repos/321Team/infra-ansible/actions/runners']:
 p=subprocess.run(['gh','api',path],capture_output=True,timeout=20);row={'path':path,'rc':p.returncode,'sha256':hashlib.sha256(p.stdout).hexdigest()}
 if p.returncode==0:
  d=json.loads(p.stdout);row['total_count']=d['total_count'];row['entries']=[{k:x.get(k) for k in ['id','head_sha','name','event','status','html_url','busy']} for x in d.get('workflow_runs',d.get('runners',[]))]
 else:row['error']='API_READ_FAILED'
 out['queries'].append(row)
out['operations_handover']='NOT_COMPLETE';out['new_job_dispatched']=False
(O/'RUNNER_READINESS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
