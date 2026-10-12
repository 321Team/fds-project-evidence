import datetime,json,socket,subprocess,time
assert socket.gethostname()=='edge01'
rows=[];start=time.monotonic();deadline=start+90
argv=['/usr/bin/curl','--disable','--noproxy','*','--connect-timeout','2','--max-time','4','--silent','--show-error','--output','/dev/null','--write-out','%{http_code}','http://127.0.0.1/readyz']
while time.monotonic()<deadline:
 t=time.monotonic();at=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  p=subprocess.run(argv,capture_output=True,timeout=5)
  rows.append({'at_utc':at,'offset_s':round(t-start,3),'rc':p.returncode,'http_code':p.stdout.decode(),'elapsed_ms':round((time.monotonic()-t)*1000),'stderr':p.stderr.decode(errors='replace')})
 except subprocess.TimeoutExpired:rows.append({'at_utc':at,'rc':None,'error':'timeout'})
 time.sleep(max(0,min(1-(time.monotonic()-t),deadline-time.monotonic())))
print(json.dumps({'host':socket.gethostname(),'argv':argv,'scope':'bounded GET readyz observation; not business/POST or HA acceptance','duration_seconds':90,'requests':rows,'status':'ALL_200' if all(x.get('rc')==0 and x.get('http_code')=='200' for x in rows) else 'FAILURES_OBSERVED'}))
