"""Prepared operator-only recovery; no authority until the separate contract is approved.

prepare: GET-only plan for known old/current images, including mixed/not-ready.
apply: ONE explicit target, ONE JSON PATCH attempt, durable no-retry claim.
No Token, sudo, rollout undo/restart, force, or automatic secondary mutation.
"""
import argparse, copy, datetime, hashlib, json, os, socket, stat, subprocess
from pathlib import Path

ROOT=Path('/home/server02/FDS_AC09_ConsoleRestore_20261015')
K=['/usr/bin/kubectl','--kubeconfig=/home/server02/.kube/config','--server=https://10.1.93.109:6443',
   '--certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem','--request-timeout=5s']
TARGETS={
 'transaction-api':('8a2af808-ec33-41f2-80b5-addde4e28910','a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33','338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0','1836153cf3e655d874602dd7deea41ddad1e8bfefe3efbbdf7b4540a9c95f7d5'),
 'fds-engine':('bf825dec-465b-4603-8b71-f768d195531c','5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369','8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d','50d28f2e3abc15d4376cc3046b72bcebc44c567fa9cdf677e829f90c73fe5005')}
def sha(x): return hashlib.sha256(x).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def now(): return datetime.datetime.now(datetime.timezone.utc)
def stamp(): return now().isoformat()
def need(ok,why):
    if not ok: raise RuntimeError(why)
def date(s):
    t=datetime.datetime.fromisoformat(s);need(t.tzinfo is not None,'TIMEZONE_REQUIRED');return t
def write_new(path,obj):
    fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:
        f.write(canon(obj)+b'\n');f.flush();os.fsync(f.fileno())
def contract(path,margin=0,expected_sha256=None):
    s=path.lstat();need(not path.is_symlink() and s.st_uid==os.getuid() and not stat.S_IMODE(s.st_mode)&0o077,'CONTRACT_PERMISSIONS')
    raw=path.read_bytes()
    if expected_sha256 is not None:
        need(sha(raw)==expected_sha256,'CONTRACT_BYTES_DRIFT')
    c=json.loads(raw)
    validate_contract(c,margin)
    return c,sha(raw)
def validate_contract(c,margin=0):
    need(c.get('template_only') is False and c.get('approved') is True,'NO_RUNTIME_AUTHORIZATION')
    need(c['operator']=='이권욱' and c['approved_by']=='GWONUK','OPERATOR_MISMATCH')
    need(c['scope']=='AC09_CURRENT_ONLY_MANUAL_MAX2' and c['max_patch_attempts_per_target']==1,'SCOPE_MISMATCH')
    need(c['source_sha256']==sha(Path(__file__).read_bytes()),'SOURCE_DRIFT')
    need(c['approval_reference'].startswith('https://github.com/321Team/infra-cicd/issues/11#issuecomment-'),'APPROVAL_REFERENCE')
    w=date(c['window_start']);expiry=date(c['expires_at'])
    need(date(c['sec_acceptance_expires_at'])==w+datetime.timedelta(minutes=45),'SEC_EXPIRY_MISMATCH')
    need(expiry<=w+datetime.timedelta(minutes=60),'RECOVERY_EXPIRY_EXCEEDS_FINITE_LIMIT')
    need(c['independent_emergency_recovery_authorized'] is True,'NO_SEPARATE_RECOVERY_AUTHORITY')
    instant=now()
    need(w<=instant<expiry and (expiry-instant).total_seconds()>=margin,'AUTHORITY_NOT_CURRENT')
    return c
def get(name):
    r=subprocess.run(K+['get','--raw=/apis/apps/v1/namespaces/fds-app/deployments/'+name],capture_output=True,timeout=8)
    need(r.returncode==0,'GET_FAILED_NO_PATCH')
    return json.loads(r.stdout)
def inspect(name,d):
    uid,old,current,fence=TARGETS[name]
    need(d['metadata']['name']==name and d['metadata']['namespace']=='fds-app' and d['metadata']['uid']==uid,'TARGET_UID_DRIFT')
    need(not d['metadata'].get('deletionTimestamp'),'TARGET_DELETING')
    spec=copy.deepcopy(d['spec']);cs=spec['template']['spec']['containers']
    indices=[i for i,c in enumerate(cs) if c['name']==name];need(len(indices)==1,'CONTAINER_MISMATCH')
    i=indices[0];image=cs[i]['image'];prefix='10.1.93.54/fds/'+name+'@sha256:'
    need(image in (prefix+old,prefix+current),'UNKNOWN_IMAGE_STOP')
    cs[i]['image']='__AC09_IMAGE_ONLY__';need(sha(canon(spec))==fence,'NON_IMAGE_SPEC_DRIFT')
    before=dict(name=name,uid=uid,resourceVersion=d['metadata']['resourceVersion'],generation=d['metadata']['generation'],image=image,
                spec_sha256=sha(canon(d['spec'])),status={k:d.get('status',{}).get(k) for k in ('observedGeneration','readyReplicas','updatedReplicas','availableReplicas')})
    if image==prefix+current: return before,[]
    base='/spec/template/spec/containers/'+str(i)
    patch=[{'op':'test','path':'/metadata/uid','value':uid},
           {'op':'test','path':'/metadata/resourceVersion','value':d['metadata']['resourceVersion']},
           {'op':'test','path':'/metadata/generation','value':d['metadata']['generation']},
           {'op':'test','path':base+'/name','value':name},
           {'op':'test','path':base+'/image','value':image},
           {'op':'replace','path':base+'/image','value':prefix+current}]
    return before,patch
def main():
    import pwd
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','apply']);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--target',choices=list(TARGETS));p.add_argument('--plan',type=Path);p.add_argument('--plan-sha256')
    p.add_argument('--writers-stopped-at');p.add_argument('--outcome-reconciled-at');a=p.parse_args()
    need(socket.gethostname()=='k8s-control01' and pwd.getpwuid(os.getuid()).pw_name=='server02','WRONG_MANAGEMENT_CONSOLE')
    need(ROOT.is_dir() and not ROOT.is_symlink() and ROOT.stat().st_uid==os.getuid() and not stat.S_IMODE(ROOT.stat().st_mode)&0o077,'PRIVATE_ROOT_REQUIRED')
    # Pin the exact initial document, not merely any later valid authorization.
    c,bound_contract_sha256=contract(a.contract)
    if a.action=='prepare':
        plans={}
        for name in TARGETS:
            before,patch=inspect(name,get(name));plans[name]=dict(before=before,patch=patch)
            contract(a.contract,expected_sha256=bound_contract_sha256)
        path=ROOT/('plan-'+now().strftime('%Y%m%dT%H%M%S%fZ')+'.json')
        write_new(path,dict(created_at=stamp(),contract_sha256=bound_contract_sha256,targets=plans))
        print(json.dumps(dict(plan=str(path),plan_sha256=sha(path.read_bytes()),targets={n:('CURRENT_NO_PATCH' if not v['patch'] else 'OLD_TO_CURRENT_CANDIDATE') for n,v in plans.items()})))
        return
    need(a.target and a.plan and a.plan_sha256 and a.writers_stopped_at and a.outcome_reconciled_at,'EXPLICIT_HANDOFF_REQUIRED')
    need(a.plan.resolve().parent==ROOT and not a.plan.is_symlink(),'PLAN_PATH_INVALID')
    raw=a.plan.read_bytes();need(sha(raw)==a.plan_sha256,'PLAN_HASH_MISMATCH');plan=json.loads(raw)
    need(plan['contract_sha256']==bound_contract_sha256,'CONTRACT_DRIFT')
    # Require writer quiescence, then at least 10s beyond bounded in-flight timeout,
    # then a new GET/plan. These timestamps are the operator's verified handoff, not an automated proof.
    stopped=date(a.writers_stopped_at);reconciled=date(a.outcome_reconciled_at)
    need(stopped+datetime.timedelta(seconds=10)<=reconciled<=date(plan['created_at'])<=now(),'OUTCOME_NOT_RECONCILED')
    need((now()-date(plan['created_at'])).total_seconds()<=60,'PLAN_STALE')
    before,patch=inspect(a.target,get(a.target));item=plan['targets'][a.target]
    contract(a.contract,expected_sha256=bound_contract_sha256)
    need(before['resourceVersion']==item['before']['resourceVersion'] and patch==item['patch'],'FRESH_STATE_DRIFT_NO_PATCH')
    need(bool(patch),'CURRENT_ALREADY_NO_PATCH')
    # 308s per remaining old target (PATCH8 + rollout300), reads20 +
    # health/metrics observation120 + reporting120. No claim of guaranteed recovery.
    required_budget=308*sum(bool(v['patch']) for v in plan['targets'].values())+260
    contract(a.contract,margin=required_budget,expected_sha256=bound_contract_sha256)
    claim=ROOT/('manual-attempt-'+a.target+'.json')
    write_new(claim,dict(state='PATCH_ATTEMPT_CLAIMED_NO_RETRY',target=a.target,at=stamp(),
                        plan_sha256=a.plan_sha256,contract_sha256=bound_contract_sha256,approval_reference=c['approval_reference']))
    # No loop, retry, or compensation. Any non-zero/timeout after claim is a manual stop.
    result=dict(target=a.target,attempted_at=stamp(),state='UNKNOWN_STOP',automatic_retry=False,contract_sha256=bound_contract_sha256)
    try:
        contract(a.contract,margin=required_budget,expected_sha256=bound_contract_sha256)
        r=subprocess.run(K+['-n','fds-app','patch','deployment',a.target,'--type=json','-p',json.dumps(patch),'-o','json'],capture_output=True,timeout=8)
        result.update(rc=r.returncode,stdout_sha256=sha(r.stdout),stderr_sha256=sha(r.stderr))
        if r.returncode==0:
            after,remaining=inspect(a.target,json.loads(r.stdout));need(not remaining and after['generation']==before['generation']+1,'UNEXPECTED_PATCH_RESPONSE')
            result.update(state='PATCH_CONFIRMED_READINESS_NOT_VERIFIED',after=after)
    except Exception as e:
        result['error']=type(e).__name__+': '+str(e)
    write_new(ROOT/('manual-result-'+a.target+'.json'),result)
    print(json.dumps(result,ensure_ascii=False));need(result['state'].startswith('PATCH_CONFIRMED'),'STOP_NO_RETRY')
if __name__=='__main__': main()
