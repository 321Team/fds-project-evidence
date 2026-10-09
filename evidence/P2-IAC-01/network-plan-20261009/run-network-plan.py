from pathlib import Path
import os,subprocess,json,hashlib,datetime,tempfile,tarfile
P=Path('/home/cloudshell-user/fds-network-plan-6eqg8ux6')
S=P/'source-network'; E=P/'evidence'; TF=P/'bin/terraform'
os.umask(0o077)
(E/'run-network-plan.py').write_bytes(Path(__file__).read_bytes())
records=[]; base=dict(os.environ); roleenv=None
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
summary={'started_utc':now(),'source_head':'5fb64bdf186645b64664080bd09f9c5babb78fcd','main_equivalent':'81162467bb2f99a099cb7067fbc3f63e1c0dbed8','apply':'NOT_RUN','infrastructure_creation':'NOT_RUN','fixture_lock':'NOT_RUN','status':'STARTED'}
def call(name,args,env=None,allowed=(0,),timeout=60,redact=False):
 t=now(); print('RUN',name,flush=True)
 try:r=subprocess.run(args,env=env or base,capture_output=True,timeout=timeout)
 except subprocess.TimeoutExpired:
  records.append({'name':name,'argv':args,'started_utc':t,'finished_utc':now(),'rc':None,'result':'TIMEOUT'})
  raise RuntimeError(name+' timeout; inspect own lock before any further operation')
 out=r.stdout
 if redact and r.returncode==0:
  obj=json.loads(out); creds=obj.pop('Credentials'); obj['Credentials']={'redacted':True,'Expiration':creds['Expiration']};out=json.dumps(obj,indent=2).encode()
 (E/(name+'.stdout')).write_bytes(out);(E/(name+'.stderr')).write_bytes(r.stderr)
 records.append({'name':name,'argv':args,'started_utc':t,'finished_utc':now(),'rc':r.returncode,'stdout_sha256':hashlib.sha256(out).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()})
 print('RC',name,r.returncode,flush=True)
 if r.returncode not in allowed:raise RuntimeError(name+' rc='+str(r.returncode))
 return r
def aws(name,args,env=None,allowed=(0,),redact=False):
 return call(name,['aws',*args,'--region','ap-northeast-2','--output','json','--no-cli-pager','--cli-connect-timeout','10','--cli-read-timeout','20'],env,allowed,45,redact)
def listing(name,env):
 r=aws(name,['s3api','list-objects-v2','--bucket','fds-tfstate-774055931866-ap-northeast-2','--prefix','phase2/network/terraform.tfstate','--max-keys','10','--no-paginate'],env)
 d=json.loads(r.stdout);assert not d.get('IsTruncated');return [o['Key'] for o in d.get('Contents',[])]
try:
 assert not [k for k in base if k.startswith(('TF_','AWS_ENDPOINT_URL')) or k in ('AWS_CA_BUNDLE','AWS_PROFILE','AWS_DEFAULT_PROFILE','AWS_DATA_PATH')]
 assert not (Path.home()/'.terraformrc').exists()
 assert not (S/'terraform/network/terraform.tfvars').exists()
 assert not list((S/'terraform/network').glob('*.auto.tfvars*'))
 assert json.loads((E/'source-receipt.json').read_text())['git_status']=='clean'
 manifest=json.loads((E/'source-manifest.json').read_text())
 for n,h in manifest.items():assert hashlib.sha256((S/n).read_bytes()).hexdigest()==h,n
 assert not call('pre-git-status',['git','-C',str(S),'status','--porcelain','--untracked-files=all']).stdout.strip()
 me=json.loads(aws('pre-caller',['sts','get-caller-identity']).stdout)
 assert me['Arn']=='arn:aws:iam::774055931866:user/321team-gwonuk'
 tr=json.loads(aws('pre-trust',['iam','get-role','--role-name','FDS-IaC-Operator']).stdout)['Role']
 assert tr['RoleId']=='AROA3IOKUF7NEM6P7ZKPK'
 st=tr['AssumeRolePolicyDocument']['Statement']
 assert len(st)==2
 assert tr['MaxSessionDuration']==3600
 assert {x['Principal']['AWS'] for x in st}=={'arn:aws:iam::774055931866:user/321team-gwonuk','arn:aws:iam::774055931866:user/321team-hayeoung'}
 for x in st:
  assert x['Effect']=='Allow' and x['Action']=='sts:AssumeRole' and x['Condition']['Bool']['aws:MultiFactorAuthPresent']=='true'
  assert x['Condition']['StringEquals']['sts:RoleSessionName']==x['Principal']['AWS'].split('/')[-1]
 c=json.loads(aws('assume-role',['sts','assume-role','--role-arn','arn:aws:iam::774055931866:role/FDS-IaC-Operator','--role-session-name','321team-gwonuk','--duration-seconds','1800'],redact=True).stdout)['Credentials']
 roleenv=dict(base);roleenv.update(AWS_ACCESS_KEY_ID=c['AccessKeyId'],AWS_SECRET_ACCESS_KEY=c['SecretAccessKey'],AWS_SESSION_TOKEN=c['SessionToken'],AWS_MAX_ATTEMPTS='1',TF_IN_AUTOMATION='1',CHECKPOINT_DISABLE='1',TF_DATA_DIR=tempfile.mkdtemp(prefix='fds-network-tfdata-',dir='/tmp'))
 summary['session_expiration']=c['Expiration'];c=None
 ident=json.loads(aws('role-caller',['sts','get-caller-identity'],roleenv).stdout)
 assert ident['Arn']=='arn:aws:sts::774055931866:assumed-role/FDS-IaC-Operator/321team-gwonuk'
 summary['role_arn']=ident['Arn']
 summary['before_keys']=listing('before-keys',roleenv)
 assert summary['before_keys']==[],'state or lock already exists; stop and review'
 aws('before-lock-versions',['s3api','list-object-versions','--bucket','fds-tfstate-774055931866-ap-northeast-2','--prefix','phase2/network/terraform.tfstate.tflock','--max-keys','20','--no-paginate'],base,allowed=(0,254))
 cmd=[str(TF),'-chdir='+str(S/'terraform/network')]
 call('fmt',cmd+['fmt','-check','-recursive'],roleenv)
 call('init',cmd+['init','-input=false','-lockfile=readonly','-backend-config=backend.hcl.example'],roleenv,timeout=240)
 assert call('workspace',cmd+['workspace','show'],roleenv).stdout.decode().strip()=='default'
 v=json.loads(call('validate',cmd+['validate','-json'],roleenv).stdout);assert v['valid']
 call('plan',cmd+['plan','-input=false','-lock-timeout=60s','-detailed-exitcode','-var=execution_enabled=true','-out='+str(E/'network.tfplan')],roleenv,allowed=(0,2),timeout=180)
 plan=json.loads(call('plan-json',cmd+['show','-json',str(E/'network.tfplan')],roleenv).stdout)
 managed=[r for r in plan.get('resource_changes',[]) if r['mode']=='managed']
 counts={}
 for r in managed:
  k='/'.join(r['change']['actions']);counts[k]=counts.get(k,0)+1
 summary['managed_actions']=counts
 assert counts=={'create':20},'unexpected planned changes'
 summary['plan_sha256']=hashlib.sha256((E/'network.tfplan').read_bytes()).hexdigest()
 summary['status']='PLAN_CAPTURED_REVIEW_REQUIRED'
except Exception as exc:
 summary.update(status='STOP',error=str(exc));print('STOP',str(exc),flush=True)
finally:
 if roleenv:
  try:
   summary['after_keys']=listing('after-keys',roleenv)
   summary['lock_current_absent']='phase2/network/terraform.tfstate.tflock' not in summary['after_keys']
   aws('after-lock-versions',['s3api','list-object-versions','--bucket','fds-tfstate-774055931866-ap-northeast-2','--prefix','phase2/network/terraform.tfstate.tflock','--max-keys','20','--no-paginate'],base,allowed=(0,254))
  except Exception as exc:summary['after_check_error']=str(exc)
 roleenv=None
 summary.update(finished_utc=now(),records=records,credentials_saved=False)
 (E/'execution-summary.json').write_text(json.dumps(summary,indent=2))
 m={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in E.iterdir() if f.is_file() and f.name!='manifest.json'}
 (E/'manifest.json').write_text(json.dumps(m,indent=2))
 arc=P/'network-evidence.tar.gz'
 with tarfile.open(arc,'w:gz') as t:t.add(E,arcname='network-evidence')
 print('NETWORK_FINAL',json.dumps({k:v for k,v in summary.items() if k!='records'}),flush=True)
 print('ARCHIVE',str(arc),'SIZE',arc.stat().st_size,'SHA256',hashlib.sha256(arc.read_bytes()).hexdigest(),flush=True)

