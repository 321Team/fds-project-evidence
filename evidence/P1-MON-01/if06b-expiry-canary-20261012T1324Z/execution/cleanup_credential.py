"""Reviewed UID-bound cleanup of owned temporary RBAC; requires no live guardian/canary."""
import control_runtime as r

body='''import fcntl
ses=Path(SES);tok=Path(TOK);kc=KC
res=ses/'results';aux=ses/'aux';py='/usr/bin/python3.12'
record=['env','IF06B_RESULTS='+str(res),'/bin/sh',str(aux/'tools/record.sh')]
def recorded(name,argv,ok=(0,),stdin=None):
 p=subprocess.run(record+[name]+argv,input=stdin,capture_output=True,text=True,timeout=30)
 out=(res/(name+'.out')).read_text();err=(res/(name+'.err')).read_text()
 if p.returncode not in ok:raise RuntimeError('STOP_AT_'+name+'_rc_'+str(p.returncode))
 return p.returncode,out,err
if list((ses/'journal').iterdir()):
 p=subprocess.run([py,'-B',str(aux/'tools/ident.py'),str(ses/'input.json'),str(ses/'evidence/supervisor.jsonl')],capture_output=True,text=True)
 assert p.returncode==4 and p.stdout.startswith('GUARDIAN_GONE'),'GUARDIAN_NOT_CONFIRMED_GONE'
 with (ses/'journal/writer.lock').open('r+') as lock:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
rc,out,err=recorded('cleanup-canary-absent',kc+['get','--raw=/apis/crd.projectcalico.org/v1/globalnetworkpolicies/p1-mon-if06b-worker03-to-monitor01-canary'],ok=(1,))
assert '(NotFound)' in err,'CANARY_NOT_CONFIRMED_ABSENT'
owners={}
for key in ['sa','cr','crb']:
 p=res/('owned-rbac-through-'+key+'.json')
 if p.exists():owners.update(json.loads(p.read_text()))
rows=[('crb','ClusterRoleBinding','clusterrolebinding',[], '/apis/rbac.authorization.k8s.io/v1/clusterrolebindings/'),
 ('cr','ClusterRole','clusterrole',[],'/apis/rbac.authorization.k8s.io/v1/clusterroles/'),
 ('sa','ServiceAccount','serviceaccount',['-n','monitoring-api'],'/api/v1/namespaces/monitoring-api/serviceaccounts/')]
deleted=[]
for key,kind,resource,ns,path in rows:
 if key not in owners:continue
 prefix='cleanup-'+key
 rc,out,err=recorded(prefix+'-now',kc+['get',resource,'p1-mon-if06b-guardian']+ns+['-o','json'],ok=(0,1))
 if rc==1:
  assert '(NotFound)' in err,'LOOKUP_NOT_DEFINITE'
  deleted.append({'object':key,'already_absent':True});continue
 argv=[py,'-B',str(aux/'tools/objinfo.py'),str(res/(prefix+'-now.out')),kind,'p1-mon-if06b-guardian']
 if key=='sa':argv+=['monitoring-api']
 recorded(prefix+'-info',argv)
 assert json.loads(out)['metadata']['uid']==owners[key]['uid'],'OWNERSHIP_CHANGED'
 options=json.dumps({'apiVersion':'v1','kind':'DeleteOptions','preconditions':{'uid':owners[key]['uid']}})
 recorded(prefix+'-delete',kc+['delete','--raw='+path+'p1-mon-if06b-guardian','-f','-'],stdin=options)
 rc,out,err=recorded(prefix+'-after',kc+['get',resource,'p1-mon-if06b-guardian']+ns+['-o','json'],ok=(1,))
 assert '(NotFound)' in err,'DELETE_NOT_CONFIRMED'
 deleted.append({'object':key,'deleted_uid':owners[key]['uid'],'readback':'NotFound'})
if tok.exists():
 assert 'sa' in owners and any(x['object']=='sa' for x in deleted),'TOKEN_REVOCATION_NOT_CONFIRMED'
 assert tok.resolve()==tok and {p.name for p in tok.iterdir()} <= {'token'}
 token=tok/'token'
 if token.exists():token.unlink()
 tok.rmdir()
print(json.dumps({'step':'TEMPORARY_CREDENTIAL_CLEANUP','objects':deleted,'token_path_absent':not tok.exists(),'unknown_objects_not_deleted':True}))
'''.replace('Path(SES)','Path('+repr(r.SES)+')').replace('Path(TOK)','Path('+repr(r.TOK)+')').replace('kc=KC','kc='+repr(r.KC))
r.run('control01-credential-cleanup',body,timeout=120)
