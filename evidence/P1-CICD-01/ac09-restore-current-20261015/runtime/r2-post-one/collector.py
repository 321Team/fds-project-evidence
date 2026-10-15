import base64,datetime as dt,hashlib,http.client,json,os,pwd,socket
assert socket.gethostname()=='edge01' and pwd.getpwuid(os.getuid()).pw_name=='svc_ansible'
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat('2026-10-15T16:20:00+09:00')
payload={'account_id': 'SIM_ac09_3451e56c57bc490e8d156cede958229f_P01', 'amount': 10000, 'currency': 'KRW', 'transaction_type': 'deposit', 'source_ip': '198.51.100.10', 'occurred_at': '2026-10-15T06:56:28.439537+00:00'};raw=json.dumps(payload,separators=(',',':')).encode()
out={'host':socket.gethostname(),'user':'svc_ansible','method':'POST','url':'http://10.1.93.50/api/v1/transactions','payload':payload,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'retry':False}
c=http.client.HTTPConnection('10.1.93.50',80,timeout=4)
try:
 c.request('POST','/api/v1/transactions',body=raw,headers={'Content-Type':'application/json','Connection':'close'})
 response=c.getresponse();body=response.read(65537)
 out.update(http=response.status,headers=response.getheaders(),body_b64=base64.b64encode(body).decode(),body_sha256=hashlib.sha256(body).hexdigest(),body_bytes=len(body),truncated=len(body)>65536)
except Exception as e:out.update(error=type(e).__name__,outcome='UNKNOWN_NO_RETRY')
finally:c.close()
out['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();print(json.dumps(out))
