import base64,datetime as dt,hashlib,http.client,json,time
rows=[]
for target in TARGETS:
 host,port,path=target['host'],target['port'],target['path']
 row={**target,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'method':'GET','redirect_followed':False,'retry':False}
 c=http.client.HTTPConnection(host,port,timeout=4)
 try:
  c.request('GET',path,headers={'Connection':'close','User-Agent':'fds-ac09-evidence/20261015'})
  response=c.getresponse();raw=response.read(262145)
  row.update(status=response.status,headers=response.getheaders(),body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest(),body_b64=base64.b64encode(raw).decode(),truncated=len(raw)>262144)
 except Exception as e:row['error']=type(e).__name__
 finally:c.close()
 row['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();rows.append(row)
print(json.dumps({'requests':rows,'mutation':False}))
