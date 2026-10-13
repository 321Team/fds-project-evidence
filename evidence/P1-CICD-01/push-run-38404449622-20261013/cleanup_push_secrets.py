"""Reclaim only this run's two explicitly authorized Actions Secrets after completion."""
import json, pathlib, subprocess
import push_control as c
E=c.E;P=c.P
required=['HARBOR_CI_ROBOT_USERNAME','HARBOR_CI_ROBOT_TOKEN']
expected={x['name']:x for x in json.loads((P/'SECRET_REGISTRATION_CONFIRMED.json').read_bytes())['secrets']}
final=json.loads((E/'execute-RUN_FINAL.json').read_bytes())
assert final['run']['status']=='completed' and all(j['status']=='completed' for j in final['jobs'])
auth=json.loads((P/'USER_AUTHORIZATION.json').read_bytes())
assert auth['cleanup_two_current_robot_actions_secrets'] and auth['exclusive_secret_use_user_confirmed']
meta=c.api('repos/321Team/infra-cicd/actions/secrets')
active=c.api('repos/321Team/infra-cicd/actions/runs?per_page=100')
assert all(r['status']=='completed' for r in active['workflow_runs']),'ACTIVE_RUN_REQUIRES_HANDOFF'
actual={x['name']:x for x in meta['secrets']}
assert all(actual.get(n)==expected[n] for n in required),'SECRET_CHANGED_NO_DELETE'
assert actual.get('CICD_APP_SOURCE_READ_TOKEN')==expected['CICD_APP_SOURCE_READ_TOKEN']
c.save('SECRET_CLEANUP_PREFLIGHT.json',{'at_utc':c.now().isoformat(),'secrets':meta,'active_runs':0,'execution_run':final['run']['id'],'authorization_reference':json.loads((P/'AUTHORIZATION_COMMENT.json').read_bytes())['html_url']})
deleted=[]
for name in required:
 assert c.api('repos/321Team/infra-cicd/actions/secrets/'+name)==expected[name],'SECRET_CHANGED_NO_DELETE'
 c.save('DELETE_'+name+'_INTENT.json',{'at_utc':c.now().isoformat(),'expected_metadata':expected[name],'scope':'THIS_RUN_REPOSITORY_ACTIONS_SECRET_ONLY'})
 r=subprocess.run(['gh','api','--method','DELETE','repos/321Team/infra-cicd/actions/secrets/'+name],capture_output=True,timeout=35)
 c.save('DELETE_'+name+'_RESPONSE.json',{'at_utc':c.now().isoformat(),'rc':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')})
 assert r.returncode==0,'DELETE_UNCONFIRMED_NO_AUTOMATIC_RETRY'
 check=c.api('repos/321Team/infra-cicd/actions/secrets');assert name not in {x['name'] for x in check['secrets']},'DELETE_READBACK_FAILED';deleted.append(name)
after=c.api('repos/321Team/infra-cicd/actions/secrets');assert {x['name']:x for x in after['secrets']}=={k:v for k,v in actual.items() if k not in required}
c.save('SECRET_CLEANUP.json',{'status':'PASS','at_utc':c.now().isoformat(),'deleted':deleted,'before':meta,'after':after,'other_secrets_unchanged':True,'harbor_robot_changed':False,'secret_values_read':False})
print(json.dumps({'status':'PASS','deleted':deleted,'other_secrets_unchanged':True}))
