"""Bind the actual dispatch and invoke the existing reviewed broker once."""
import datetime,hashlib,json,pathlib,shlex,sys

decision=json.loads((pathlib.Path(__file__).parent/'START_CUTOFF_AUTHORIZED.json').read_bytes())
assert decision['user_decision']=='시작 마감 16:45로 변경·17:00 종료 유지'
assert decision['additional_true_runs_allowed']==1 and decision['end_kst']=='2026-10-13T17:00:00+09:00'

import remote_ops
OUT=pathlib.Path(__file__).parent
run=int(sys.argv[1]);read=pathlib.Path(sys.argv[2]);assert run>0
now=datetime.datetime.now(datetime.timezone.utc)
assert datetime.datetime.fromisoformat('2026-10-13T16:15:00+09:00')<=now<datetime.datetime.fromisoformat('2026-10-13T16:47:00+09:00')
x=json.loads((read/'stdout.json').read_bytes());assert x['requested_run']==run and x['mode']=='true' and len(x['matches'])==1 and x['socket']['exists'] and x['socket']['is_socket'] and x['socket']['uid']==1000 and x['socket']['mode']=='0o600'
scope=x['matches'][0]['files']['dispatch.json']['data']['binding']
assert scope=={'execution':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':'2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7','run_id':run,'attempt':1},'record_sha256':'11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50','plan_sha256':'5c2d8367f5b81875693165055234a30e5c69944e345c8ad8c5277ef30ebd8387','sa_uid':'8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'}
raw=(json.dumps(scope,sort_keys=True,separators=(',',':'))+'\n').encode();digest=hashlib.sha256(raw).hexdigest()
path=remote_ops.ROOT+'/binding-'+str(run)+'.json';(OUT/('binding-'+str(run)+'.json')).write_bytes(raw)
script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = ansible01','test "$(id -un)" = server01_ansible','test ! -e '+path,'test ! -L '+path,'set -C','cat > '+path,'sha256sum '+path,'stat -c "%n|%u|%a|%F|%h" '+path])
result=remote_ops.run('binding-'+str(run),script,raw);assert result.decode().split()[0]==digest
root=remote_ops.ROOT+'/deploy-controller-2d8a14c'
args=['/usr/bin/python3','-I','-B','-c','import sys; sys.path.insert(0,"tools/delivery"); import transfer_deploy_credential as t; raise SystemExit(t.main())','--bundle',root+'/native-source-2d8a14c.json','--bundle-sha256','8cfdcce5e4b5eb95001d27e35606e5121edf77d8c2c1f5f481016c79933baa5c','--source-sha','2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7','--binding',path,'--binding-sha256',digest]
script='cd '+shlex.quote(root)+' && '+shlex.join(args)
local=json.loads(remote_ops.run('broker-local-'+str(run),script,timeout=40));assert local=={'HANDOFF':'LOCAL_INPUTS_VALIDATED','TOKEN_ISSUED':False,'DEPLOY':'NOT_EXECUTED'}
args+=['--execute','--authorization-expires','2026-10-13T08:00:00+00:00','--cp1-key','/home/server01_ansible/.ssh/id_ed25519','--runner-key','/home/server01_ansible/.ssh/p1_ansible_ed25519']
remote_ops.run('broker-execute-'+str(run),'cd '+shlex.quote(root)+' && '+shlex.join(args),timeout=90)
