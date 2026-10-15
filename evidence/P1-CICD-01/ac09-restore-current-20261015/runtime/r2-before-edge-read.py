import os,socket,datetime as dt
assert socket.gethostname()=="edge01" and os.geteuid()!=0
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat("2026-10-15T16:20:00+09:00")
import base64,datetime as dt,hashlib,http.client,json,time
rows=[]
for target in [{'host': '10.1.93.105', 'port': 30080, 'path': '/livez', 'pod_uid': 'ad73fee3-5e0c-4cc9-bed4-7ada5d4a6cd4', 'pod_ip': '10.244.79.127', 'service_local_endpoint_basis': True}, {'host': '10.1.93.105', 'port': 30080, 'path': '/readyz', 'pod_uid': 'ad73fee3-5e0c-4cc9-bed4-7ada5d4a6cd4', 'pod_ip': '10.244.79.127', 'service_local_endpoint_basis': True}, {'host': '10.1.93.105', 'port': 30080, 'path': '/metrics', 'pod_uid': 'ad73fee3-5e0c-4cc9-bed4-7ada5d4a6cd4', 'pod_ip': '10.244.79.127', 'service_local_endpoint_basis': True}, {'host': '10.1.93.107', 'port': 30080, 'path': '/livez', 'pod_uid': '4296ab4b-ad5d-4c69-a372-c910092edf84', 'pod_ip': '10.244.69.197', 'service_local_endpoint_basis': True}, {'host': '10.1.93.107', 'port': 30080, 'path': '/readyz', 'pod_uid': '4296ab4b-ad5d-4c69-a372-c910092edf84', 'pod_ip': '10.244.69.197', 'service_local_endpoint_basis': True}, {'host': '10.1.93.107', 'port': 30080, 'path': '/metrics', 'pod_uid': '4296ab4b-ad5d-4c69-a372-c910092edf84', 'pod_ip': '10.244.69.197', 'service_local_endpoint_basis': True}, {'host': '10.1.93.108', 'port': 30080, 'path': '/livez', 'pod_uid': 'd448512c-6e60-49c4-b78f-f1b7ddb17088', 'pod_ip': '10.244.39.223', 'service_local_endpoint_basis': True}, {'host': '10.1.93.108', 'port': 30080, 'path': '/readyz', 'pod_uid': 'd448512c-6e60-49c4-b78f-f1b7ddb17088', 'pod_ip': '10.244.39.223', 'service_local_endpoint_basis': True}, {'host': '10.1.93.108', 'port': 30080, 'path': '/metrics', 'pod_uid': 'd448512c-6e60-49c4-b78f-f1b7ddb17088', 'pod_ip': '10.244.39.223', 'service_local_endpoint_basis': True}]:
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
