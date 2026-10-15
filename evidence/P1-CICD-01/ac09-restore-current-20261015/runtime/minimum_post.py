"""One approved deposit request per phase; no retry, no database credential access."""
import datetime as dt,json,pathlib,sys
import runtime as r
phase=sys.argv[1];assert phase in ('r1','r2')
r.authorization()
for label in ('edge-api','api','mon'):
 value=r.load(r.O/(phase+'-before-'+label)/'stdout.json');data=json.loads(value['stdout']) if 'stdout' in value else value
 assert all(x.get('status')==200 and not x.get('truncated') and not x.get('error') for x in data['requests'] if x['path']!='/metrics' or label=='mon' or phase=='r1')
payload=r.load(r.B/('r1-restore-previous.payload.TEMPLATE.json' if phase=='r1' else 'r2-return-current.payload.TEMPLATE.json'))['payload']
payload['occurred_at']=r.now().isoformat()
deadline=r.CUT+dt.timedelta(minutes=10) if phase=='r1' else r.END
assert r.now()<deadline
claim=r.O/(phase+'-post-attempt.json')
with claim.open('xb') as f:f.write(r.encode({'at_utc':r.now().isoformat(),'phase':phase,'payload':payload,'max_requests':1,'retry':False,'db_before':'NOT_COLLECTED_NORMAL_DB_CONSOLE_ONLY'}))
source='''import base64,datetime as dt,hashlib,http.client,json,os,pwd,socket
assert socket.gethostname()=='edge01' and pwd.getpwuid(os.getuid()).pw_name=='svc_ansible'
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat(DEADLINE)
payload=PAYLOAD;raw=json.dumps(payload,separators=(',',':')).encode()
out={'host':socket.gethostname(),'user':'svc_ansible','method':'POST','url':'http://10.1.93.50/api/v1/transactions','payload':payload,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'retry':False}
c=http.client.HTTPConnection('10.1.93.50',80,timeout=4)
try:
 c.request('POST','/api/v1/transactions',body=raw,headers={'Content-Type':'application/json','Connection':'close'})
 response=c.getresponse();body=response.read(65537)
 out.update(http=response.status,headers=response.getheaders(),body_b64=base64.b64encode(body).decode(),body_sha256=hashlib.sha256(body).hexdigest(),body_bytes=len(body),truncated=len(body)>65536)
except Exception as e:out.update(error=type(e).__name__,outcome='UNKNOWN_NO_RETRY')
finally:c.close()
out['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();print(json.dumps(out))
'''.replace('DEADLINE',repr(deadline.isoformat())).replace('PAYLOAD',repr(payload))
p=r.O/(phase+'-post-one.py');p.write_bytes(source.encode());compile(source,str(p),'exec')
result=r.collect.remote((phase+'-post-one','10.1.93.50','svc_ansible','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,p,[]))
print(json.dumps(result))
if result['rc']==0:
 value=r.load(r.O/(phase+'-post-one')/'stdout.json');import base64
 print(json.dumps({'phase':phase,'http':value.get('http'),'body':base64.b64decode(value.get('body_b64','')).decode(),'error':value.get('error')},ensure_ascii=False))
