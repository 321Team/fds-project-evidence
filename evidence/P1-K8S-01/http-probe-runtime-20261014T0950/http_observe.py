import concurrent.futures,datetime,json,os,pathlib,socket,time,urllib.request
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(path):
 start=now()
 try:
  with op.open('http://10.244.69.193:8001/'+path,timeout=.8) as r:code=r.status;r.read(1024)
  return path,{'start':start,'end':now(),'code':code}
 except Exception as e:return path,{'start':start,'end':now(),'code':getattr(e,'code',0),'error':type(e).__name__}
end=time.monotonic()+600;tick=0
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 while time.monotonic()<end:
  start=time.monotonic();fs=[pool.submit(read,p) for p in ('readyz','livez')]
  row={'tick':tick,'utc':now(),'host':socket.gethostname(),'scope':'READ_ONLY_HTTP_AND_ORIGINAL_PROC','http':dict(f.result() for f in fs)}
  try:
   raw=pathlib.Path('/proc/1290996/stat').read_text();parts=raw[raw.rfind(')')+2:].split();row['original_pid']={'state':parts[0],'start_ticks':parts[19]}
  except FileNotFoundError:row['original_pid']='ABSENT'
  print(json.dumps(row),flush=True);tick+=1;time.sleep(max(0,2-(time.monotonic()-start)))
