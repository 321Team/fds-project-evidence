import datetime,hashlib,json,os,socket,urllib.request,urllib.error
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
op=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
for ip in ['10.1.93.105','10.1.93.107','10.1.93.108']:
 url='http://'+ip+':30080/readyz';row={'url':url,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with op.open(url,timeout=2) as r:raw=r.read(4096);row.update(code=r.status,body_sha256=hashlib.sha256(raw).hexdigest())
 except urllib.error.HTTPError as e:row.update(code=e.code,error=type(e).__name__)
 except Exception as e:row.update(code=0,error=type(e).__name__)
 row['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();rows.append(row)
print(json.dumps({'host':socket.gethostname(),'uid':os.geteuid(),'scope':'N08_READ_ONLY_GET','http_posts':0,'rows':rows,'all_code_000':all(r['code']==0 for r in rows),'limitation':'No specific firewall rule attribution or path-wide deny proof from timeout alone.'}))
