
import datetime as dt,hashlib,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
home=pathlib.Path('/home/server01_cicd-runner');run='202610142110';out=home/('FDS_D03_'+run)
checks=[]
for role in ('db','api','engine','fixture'):
    name='fds-d03-'+run+'-'+role
    p=subprocess.run(['podman','container','exists',name],capture_output=True,text=True,timeout=10)
    checks.append({'name':name,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'absent':p.returncode==1})
    assert p.returncode==1,'EXACT_OBJECT_NOT_CONFIRMED_ABSENT'
containers=json.loads(subprocess.check_output(['podman','ps','-a','--format','json'],timeout=10));assert containers==[]
cred=all(not (out/name).exists() for name in ('db.env','api.env'));assert cred
intents=list(out.glob('*-post-intent.json'));assert len(intents)==0
claim=home/'FDS_D03_Claims'/('202610142110.json');assert claim.is_file()
print(json.dumps({'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'hostname':socket.gethostname(),'uid':os.getuid(),'read_only':True,'exact_names':checks,'container_count':len(containers),'credential_files_absent':cred,'post_intent_count':len(intents),'claim_preserved':True,'claim_sha256':hashlib.sha256(claim.read_bytes()).hexdigest(),'runtime_original_result':json.loads((out/'result.json').read_bytes()),'disposition':'OWNED_OBJECTS_AND_CREDENTIAL_FILES_OBSERVED_ABSENT; ORIGINAL_CLEANUP_FAILED_PRESERVED; NO_RETRY'}))
