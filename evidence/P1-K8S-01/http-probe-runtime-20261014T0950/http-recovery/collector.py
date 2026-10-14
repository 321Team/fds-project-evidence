"""Read-only recovery supplement; original proc sampler ended on process exit."""
import concurrent.futures,datetime,json,os,socket,time,urllib.request
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def get(path):
 try:
  with op.open('http://10.244.69.193:8001/'+path,timeout=.8) as r:code=r.status;r.read(1024)
  return {'path':path,'code':code,'utc':now()}
 except Exception as e:return {'path':path,'code':getattr(e,'code',0),'error':type(e).__name__,'utc':now()}
rows=[];start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 while True:
  tick=time.monotonic();fs=[pool.submit(get,p) for p in ('readyz','livez')];rows.append({'utc':now(),'elapsed':tick-start,'http':[f.result() for f in fs]})
  if tick-start>=60:break
  time.sleep(max(0,2-(time.monotonic()-tick)))
ok=all(x['code']==200 for row in rows for x in row['http'])
print(json.dumps({'scope':'READ_ONLY_RECOVERY_SUPPLEMENT','signals':0,'stable60_pass':ok,'rows':rows}))
raise SystemExit(0 if ok else 2)
