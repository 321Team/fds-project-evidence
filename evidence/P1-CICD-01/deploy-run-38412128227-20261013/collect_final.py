"""Collect completed run originals and fresh post-state without new mutations."""
import base64,concurrent.futures,hashlib,importlib.util,json,pathlib,subprocess
BASE=pathlib.Path(__file__).parent.resolve()
spec=importlib.util.spec_from_file_location('deploy_reads',BASE/'execution.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
FINAL=e.OUT/'final';FINAL.mkdir(exist_ok=False)
def capture(mode):
 run=json.loads((e.OUT/('dispatch-'+mode)/'run.json').read_bytes())['id']
 d=FINAL/mode;d.mkdir(exist_ok=False)
 r=e.gh(f'repos/321Team/infra-cicd/actions/runs/{run}');e.save(d/'run.json',r)
 assert r['status']=='completed' and r['run_attempt']==1 and r['head_sha']==e.SOURCE
 jobs=e.gh(f'repos/321Team/infra-cicd/actions/runs/{run}/jobs');e.save(d/'jobs.json',jobs);assert len(jobs['jobs'])==1
 j=jobs['jobs'][0]
 p=subprocess.run(['gh','api','--allow-escape-sequences',f'repos/321Team/infra-cicd/actions/jobs/{j["id"]}/logs'],capture_output=True,timeout=35)
 (d/'job.log').write_bytes(p.stdout);(d/'job-log.stderr.txt').write_bytes(p.stderr)
 e.save(d/'job-log-receipt.json',{'at_utc':e.now().isoformat(),'rc':p.returncode,'run_id':run,'job_id':j['id'],'stdout_sha256':e.sha(p.stdout),'stderr_sha256':e.sha(p.stderr),'scope':'Raw log bytes captured locally; not displayed; no workflow retry'})
 assert p.returncode==0
 label,x=e.observe(run,mode);e.save(d/'runner-read-location.json',{'directory':label})
 assert len(x['matches'])==1 and 'result.json' in x['matches'][0]['files']
 originals=d/'originals';originals.mkdir()
 for name,f in x['matches'][0]['files'].items():
  raw=base64.b64decode(f['raw_b64'],validate=True);assert e.sha(raw)==f['sha256'];(originals/name).write_bytes(raw)
 claims=d/'claims'
 if x.get('claim_files'):
  claims.mkdir()
  for name,f in x['claim_files'].items():
   raw=base64.b64decode(f['raw_b64'],validate=True);assert e.sha(raw)==f['sha256'];path=claims/name;path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
 return {'mode':mode,'run_id':run,'job_id':j['id'],'job_started_at':j['started_at'],'job_completed_at':j['completed_at'],'conclusion':r['conclusion'],'result':x['matches'][0]['files']['result.json']['data'],'result_sha256':x['matches'][0]['files']['result.json']['sha256'],'socket':x['socket'],'claim_files':len(x.get('claim_files',{})),'runner_directory':x['matches'][0]['directory']}
results=[capture('false'),capture('true')]
key='/home/server01_ansible/.ssh/p1_ansible_ed25519';old=BASE.parent/'phase1-deploy-preparation-20261013';original=BASE.parent/'p1-delivery-runner-20261013';e.collect.OUT=FINAL
tasks=[('cluster','10.1.93.102','svc_ansible',key,True,original/'cluster_read.py',[]),('app-state','10.1.93.102','svc_ansible',key,True,old/'app_state_read.py',[]),('runner-health','10.250.10.20','server01_cicd-runner',key,False,BASE.parent/'phase1-push-followup-20261013/runner_push_read.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 reads=list(pool.map(e.collect.remote,tasks))
assert all(r['rc']==0 for r in reads)
e.save(FINAL/'RUN_RESULTS.json',results)
print(json.dumps({'runs':[{'mode':r['mode'],'id':r['run_id'],'conclusion':r['conclusion'],'result':r['result'],'claim_files':r['claim_files'],'socket':r['socket']} for r in results],'post_reads':reads},ensure_ascii=False))
