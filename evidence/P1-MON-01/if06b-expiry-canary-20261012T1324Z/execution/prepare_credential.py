"""Approved reviewed RBAC commands, one at a time; no canary or retries."""
import control_runtime as r

body='''ses=Path(SES);tok=Path(TOK);kc=KC
res=ses/'results';aux=ses/'aux';py='/usr/bin/python3.12'
record=['env','IF06B_RESULTS='+str(res),'/bin/sh',str(aux/'tools/record.sh')]
def recorded(name,argv,ok=(0,),stdin=None):
 p=subprocess.run(record+[name]+argv,input=stdin,capture_output=True,text=True,timeout=45)
 out=(res/(name+'.out')).read_text();err=(res/(name+'.err')).read_text()
 if p.returncode not in ok:raise RuntimeError('STOP_AT_'+name+'_rc_'+str(p.returncode))
 return p.returncode,out,err
rows=[('sa','ServiceAccount','serviceaccount',['-n','monitoring-api'],'01-serviceaccount.yaml'),
      ('cr','ClusterRole','clusterrole',[],'02-clusterrole.yaml'),
      ('crb','ClusterRoleBinding','clusterrolebinding',[],'03-clusterrolebinding.yaml')]
namespace=recorded('2-2-ns-runtime',kc+['get','namespace','monitoring-api','-o','json'])[1]
assert json.loads(namespace)['metadata']['uid']=='f7e863e5-9fa6-424d-b3b3-697d697c6066'
for short,kind,resource,ns,file in rows:
 rc,out,err=recorded('2-2-'+short+'-pre-runtime',kc+['get',resource,'p1-mon-if06b-guardian']+ns+['-o','json'],ok=(0,1))
 assert rc==1 and '(NotFound)' in err,'RBAC_NOT_ABSENT_'+short
owners={}
for letter,row in zip('abc',rows):
 short,kind,resource,ns,file=row
 create='2-3'+letter+'-'+short+'-create'
 _,out,_=recorded(create,kc+['create','-o','json','-f',str(aux/'rbac'/file)])
 argv=[py,'-B',str(aux/'tools/objinfo.py'),str(res/(create+'.out')),kind,'p1-mon-if06b-guardian']
 if short=='sa':argv+=['monitoring-api']
 recorded('2-3'+letter+'-'+short+'-receipt',argv)
 obj=json.loads(out);owners[short]={'uid':obj['metadata']['uid'],'kind':kind}
 # Preserve a cumulative receipt after EACH confirmed creation, before next object.
 with (res/('owned-rbac-through-'+short+'.json')).open('x') as f:json.dump(owners,f)
sa='system:serviceaccount:monitoring-api:p1-mon-if06b-guardian'
canary='p1-mon-if06b-worker03-to-monitor01-canary'
yes=[['create','globalnetworkpolicies.crd.projectcalico.org'],
 ['get','globalnetworkpolicies.crd.projectcalico.org/'+canary],['delete','globalnetworkpolicies.crd.projectcalico.org/'+canary],
 ['get','namespaces/kube-system'],['create','selfsubjectaccessreviews.authorization.k8s.io']]
no=[['list','globalnetworkpolicies.crd.projectcalico.org'],['delete','globalnetworkpolicies.crd.projectcalico.org/fds-k8s-host-k8s-worker03'],
 ['patch','globalnetworkpolicies.crd.projectcalico.org/'+canary],['get','secrets','-n','kube-system'],['get','namespaces/default'],['create','clusterrolebindings.rbac.authorization.k8s.io']]
for prefix,items,expected in [('y',yes,0),('n',no,1)]:
 for n,args in enumerate(items,1):
  rc,out,err=recorded('2-4-'+prefix+str(n),kc+['auth','can-i']+args+['--as='+sa],ok=(expected,))
  assert out.strip()==('yes' if expected==0 else 'no'),'UNEXPECTED_ACCESS_RESPONSE'
tok.mkdir(mode=0o700,exist_ok=False)
with (tok/'token').open('xb') as secret, (res/'2-5-token-issue.err').open('xb') as error:
 p=subprocess.run(kc+['create','token','p1-mon-if06b-guardian','-n','monitoring-api','--duration=900s'],stdout=secret,stderr=error,timeout=20)
(res/'2-5-token-issue.rc').write_text(str(p.returncode)+'\\n')
assert p.returncode==0,'TOKEN_ISSUE_FAILED'
recorded('2-5-token-stat',['stat','-c','%n %U:%G %a %s',str(tok/'token')])
_,claims,_=recorded('2-5-token-claims',[py,'-B',str(aux/'tools/tokeninfo.py'),str(tok/'token'),sa,owners['sa']['uid'],'900','210'])
_,validation,_=recorded('3-1-validate',[py,'-B',str(ses/'supply/guardian.py'),'validate','--config',str(ses/'input.json')])
assert json.loads(validation)['passed'] is True
_,preflight,_=recorded('5-1-preflight',[py,'-B',str(ses/'supply/guardian.py'),'preflight','--config',str(ses/'input.json')])
assert json.loads(preflight)['passed'] is True
print(json.dumps({'step':'CREDENTIAL_AND_PREFLIGHT_READY','owners':owners,'permission_checks':11,
 'claims':claims,'validate':json.loads(validation),'preflight':json.loads(preflight),'canary_created':0}))
'''.replace('Path(SES)','Path('+repr(r.SES)+')').replace('Path(TOK)','Path('+repr(r.TOK)+')').replace('kc=KC','kc='+repr(r.KC))
r.run('control01-credential-preflight',body,timeout=180)
