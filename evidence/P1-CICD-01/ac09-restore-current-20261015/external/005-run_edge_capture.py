"""Post-GO only: one capture per pre/during, original wire bytes retained locally."""
import argparse,base64,datetime,hashlib,importlib.util,json,os
from pathlib import Path
O=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--phase',required=True,choices=['pre','during']);p.add_argument('--authorization',required=True,type=Path)
a=p.parse_args();auth=json.loads(a.authorization.read_bytes())
assert auth['template_only'] is False and auth['runtime_go'] is True
assert auth['approved_by']=='GWONUK' and auth['round_id']=='AC09-20261015-R1-R2'
assert auth['edge_raw_gets']==4 and auth['edge_observer_sha256']==hashlib.sha256((O/'edge_metrics_raw.py').read_bytes()).hexdigest()
w=datetime.datetime.fromisoformat(auth['window_start']);end=datetime.datetime.fromisoformat(auth['expires_at']);now=datetime.datetime.now(datetime.timezone.utc)
assert w.tzinfo and end.tzinfo and w<=now<end<=w+datetime.timedelta(minutes=45)
assert auth['approval_reference'].startswith('https://github.com/321Team/infra-cicd/issues/11#issuecomment-')
if a.phase=='during':
    exposure=json.loads((O/'R1_EXPOSURE_CONFIRMED.json').read_bytes())
    assert exposure['both_previous_ready'] is True and exposure['round_id']==auth['round_id']
    assert datetime.datetime.fromisoformat(exposure['p'])<=now<datetime.datetime.fromisoformat(exposure['p'])+datetime.timedelta(minutes=15)
claim=O/('edge-'+a.phase+'.claim.json')
with claim.open('x',encoding='utf-8') as f:
    json.dump(dict(at=now.isoformat(),authorization_sha256=hashlib.sha256(a.authorization.read_bytes()).hexdigest()),f)
spec=importlib.util.spec_from_file_location('existing_transport',O.parents[1]/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=O
label='edge-'+a.phase
result=m.remote((label,'10.1.93.50','svc_ansible','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,O/'edge_metrics_raw.py',['--phase',a.phase,'--round-id',auth['round_id']]))
print(json.dumps(result))
folder=O/label
if (folder/'stdout.json').stat().st_size:
    data=json.loads((folder/'stdout.json').read_bytes())
    for i,r in enumerate(data['results'],1):
        for src,suffix in [('request_b64','request.http'),('response_wire_b64','response.http')]:
            raw=base64.b64decode(r[src],validate=True);(folder/f'{i}-{suffix}').write_bytes(raw)
        print(json.dumps({k:r.get(k) for k in ('path','status','locations','verdict','rc','wire_bytes','wire_sha256')},ensure_ascii=False))
raise SystemExit(0 if result['rc']==0 else 2)
