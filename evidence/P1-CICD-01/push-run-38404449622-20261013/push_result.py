"""Read the actual run/job, collect bounded nonsecret evidence and verify bindings."""
import base64, datetime as dt, hashlib, json, pathlib, re, subprocess, sys
import push_control as control
E=control.E;P=control.P;SHA=control.SHA;HASH=control.HASH
def snapshot(label):
 assert label in ['validate','execute']
 intent=json.loads((E/(label+'-DISPATCH_INTENT.json')).read_bytes())
 runs=control.api('repos/321Team/infra-cicd/actions/workflows/app-push.yml/runs?per_page=100')['workflow_runs']
 matches=[r for r in runs if r['id'] not in intent['prior_run_ids'] and r['event']=='workflow_dispatch' and r['head_sha']==SHA and dt.datetime.fromisoformat(r['created_at'].replace('Z','+00:00'))>=dt.datetime.fromisoformat(intent['at_utc'])-dt.timedelta(seconds=2)]
 assert len(matches)<=1,'AMBIGUOUS_NEW_RUN'
 if not matches:return {'state':'AWAITING_NEW_RUN','mode':label}
 run=matches[0];assert run['run_attempt']==1
 binding=E/(label+'-RUN_BINDING.json')
 if binding.exists():assert json.loads(binding.read_bytes())['run_id']==run['id']
 else:control.save(binding.name,{'run_id':run['id'],'run_attempt':1,'workflow_sha':SHA,'mode':label,'run_url':run['html_url']})
 jobs=control.api(f'repos/321Team/infra-cicd/actions/runs/{run["id"]}/jobs')['jobs'];assert len(jobs)<=1
 folder=E/(label+'-snapshots');folder.mkdir(exist_ok=True)
 stamp=dt.datetime.now(dt.timezone.utc).strftime('%H%M%S%f')
 (folder/(stamp+'.json')).write_text(json.dumps({'run':run,'jobs':jobs},indent=2),encoding='utf-8')
 started=jobs[0]['started_at'] if jobs else None
 if started:
  within=dt.datetime.fromisoformat('2026-10-13T22:20:00+09:00')<=dt.datetime.fromisoformat(started.replace('Z','+00:00'))<dt.datetime.fromisoformat('2026-10-13T22:30:00+09:00')
  if not within:cancel(run['id'],label,'START_OUTSIDE_WINDOW');return {'state':'CANCEL_REQUESTED_START_OUTSIDE_WINDOW','run_id':run['id'],'started_at':started}
 if control.now()>=dt.datetime.fromisoformat('2026-10-13T22:30:00+09:00') and not started and run['status']!='completed':cancel(run['id'],label,'START_DEADLINE');return {'state':'CANCEL_REQUESTED_START_DEADLINE','run_id':run['id']}
 if run['status']=='completed':
  f=E/(label+'-RUN_FINAL.json')
  if not f.exists():control.save(f.name,{'run':run,'jobs':jobs})
 return {'state':run['status'],'conclusion':run['conclusion'],'run_id':run['id'],'url':run['html_url'],'started_at':started,'job_conclusion':jobs[0]['conclusion'] if jobs else None}
def cancel(run_id,label,reason):
 target=label+'-CANCEL_INTENT.json'
 if (E/target).exists():return
 control.save(target,{'run_id':run_id,'reason':reason,'at_utc':control.now().isoformat()})
 p=subprocess.run(['gh','api','--method','POST',f'repos/321Team/infra-cicd/actions/runs/{run_id}/cancel'],capture_output=True,timeout=35)
 control.save(label+'-CANCEL_RESPONSE.json',{'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')})
def collect(label):
 final=json.loads((E/(label+'-RUN_FINAL.json')).read_bytes());run=final['run'];jobs=final['jobs'];assert run['status']=='completed' and len(jobs)==1
 job=jobs[0]
 # Preserve original ANSI bytes only in a captured local file; never render the log to a terminal.
 p=subprocess.run(['gh','api','--allow-escape-sequences',f'repos/321Team/infra-cicd/actions/jobs/{job["id"]}/logs'],capture_output=True,timeout=35);assert p.returncode==0
 (E/(label+'-job.log')).write_bytes(p.stdout)
 roots=set(re.findall(rb'EVIDENCE_DIR=(/home/server01_cicd-runner/FDS_CICD_Push\.[A-Za-z0-9_-]+)',p.stdout));assert len(roots)==1,'EVIDENCE_PATH_NOT_UNIQUE'
 root=next(iter(roots)).decode()
 reader=(P.parent/'p1-push-execution-20261013/execution_result_read.py').read_text(encoding='utf-8').replace('13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89',HASH)
 raw=('FOLDER='+repr(root)+'\n'+reader).encode()
 out=control.transport.remote(label+'-result',raw)
 binding={'run_id':run['id'],'job_id':job['id'],'job_log_sha256':hashlib.sha256(p.stdout).hexdigest(),'folder':root,'result_read_at_utc':out['at_utc']}
 control.save(label+'-EVIDENCE_BINDING.json',binding)
 selected=E/(label+'-originals');selected.mkdir()
 for name,item in out['files'].items():
  raw=base64.b64decode(item['raw_b64'],validate=True);assert hashlib.sha256(raw).hexdigest()==item['sha256']
  dest=selected/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 verdict=verify(label,out,final);control.save('VALIDATION_VERIFIED.json' if label=='validate' else 'PUSH_VERIFIED.before-secret-cleanup.json',verdict);print(json.dumps(verdict,ensure_ascii=False))
def verify(label,out,final):
 run=final['run'];job=final['jobs'][0];files=out['files']
 assert run['conclusion']==job['conclusion']=='success','RUN_FAILED_PRESERVED_NO_RETRY'
 d=files['dispatch.json']['data'];r=files['result.json']['data'];c=d['execution_context']
 assert d['record_sha256']==HASH and d['mode']==('false' if label=='validate' else 'true')
 assert str(c['run_id'])==str(run['id']) and c['attempt']==1 and c['workflow_sha']==SHA and c['host']=='cicd-runner01' and c['uid']==1000
 assert r['error_code']=='NONE' and r['DEPLOY']=='NOT_EXECUTED'
 manifest_entries=0
 for name,item in files.items():
  if not name.endswith('SHA256SUMS'):continue
  for line in item['text'].splitlines():
   digest,target=line.split(None,1);target=str(pathlib.PurePosixPath(name).parent/pathlib.PurePosixPath(target.lstrip('* ')))
   assert '..' not in pathlib.PurePosixPath(target).parts and not target.startswith('/')
   data=files.get(target,out['hash_only'].get(target));assert data and data['sha256']==digest,(name,target)
   manifest_entries+=1
 if label=='validate':
  assert r['VALIDATION']=='PASS' and r['PUSH']=='NOT_EXECUTED' and out['claim'] is None
  return {'VALIDATION':'PASS','PUSH':'NOT_EXECUTED','run_id':run['id'],'job_id':job['id'],'input_sha256':HASH,'folder':out['folder'],'manifest_entries':manifest_entries,'verified_at_utc':control.now().isoformat()}
 summary=files['dispatch-result.json']['data'];cleanup=files['credential-cleanup.json']['data'];scan=files['fresh-scan/result.json']['data'];db=files['fresh-scan/db/result.json']['data'];record=json.loads((E/control.NAME).read_bytes())
 assert not out['missing'] and r['PUSH']==summary['PUSH']==summary['DISPATCH']=='PASS'
 assert r['execution_context']==summary['execution_context']==scan['context']==db['context']==c
 assert summary['record_sha256']==HASH and cleanup['temporary_auth_cleanup']==summary['credential_cleanup']=='PASS'
 assert not out['auth_directory_names_present'] and out['claim']['data']['record_sha256']==HASH and out['claim']['data']['execution_context']==c
 assert scan['IMAGE_SCAN']==db['DB_PREFLIGHT']=='PASS' and db['download_exit_code']==0
 assert scan['source_sha']==record['source']['commit'] and r['build_workflow']==record['workflow']
 assert r['fresh_scan_result_sha256']==files['fresh-scan/result.json']['sha256'] and scan['db_result_sha256']==files['fresh-scan/db/result.json']['sha256']
 assert db['db_sha256']==out['hash_only']['fresh-scan/db/cache/db/trivy.db']['sha256'] and db['metadata_sha256']==files['fresh-scan/db/cache/db/metadata.json']['sha256']
 assert set(r['images'])==set(scan['images'])==set(record['build_scan']['images'])
 for n,i in r['images'].items():
  s=scan['images'][n];expected=record['build_scan']['images'][n]
  assert i['result']=='PASS' and i['registry_repository']=='10.1.93.54/fds/'+n and re.fullmatch('delivery-[0-9a-f]{32}',i['tag'])
  assert i['manifest_digest']==s['manifest_digest']==expected['manifest_digest']
  for k in ['archive_sha256','config_digest']:assert s[k]==expected[k]
  assert s['scan']=='PASS' and s['exit_code']==0 and s['counts']=={'HIGH':0,'CRITICAL':0}
  assert s['report_sha256']==out['hash_only']['fresh-scan/'+n+'/report.json']['sha256'] and files['fresh-scan/'+n+'/exit-code.txt']['text'].strip()=='0'
 return {'PUSH':'PASS','DEPLOY':'NOT_EXECUTED','DELIVERY_GATE':'NOT_VERIFIED','run_id':run['id'],'job_id':job['id'],'job_started_at':job['started_at'],'job_completed_at':job['completed_at'],'input_sha256':HASH,'workflow_sha':SHA,'source_sha':record['source']['commit'],'folder':out['folder'],'images':r['images'],'fresh_scan':'PASS','counts':{n:s['counts'] for n,s in scan['images'].items()},'temporary_credential_cleanup':'PASS','actions_secret_cleanup':'PENDING','manifest_entries':manifest_entries,'verified_at_utc':control.now().isoformat()}
if __name__=='__main__':
 if sys.argv[1]=='snapshot':print(json.dumps(snapshot(sys.argv[2])))
 elif sys.argv[1]=='collect':collect(sys.argv[2])
 else:raise SystemExit('Unsupported mode')
