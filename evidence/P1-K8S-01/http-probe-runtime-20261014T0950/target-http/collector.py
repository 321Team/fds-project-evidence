"""Read HTTP only on the selected local Pod; capture metadata, not credentials."""
import datetime,hashlib,json,os,socket,urllib.request,urllib.error
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
rows=[]
for port,path,expected in [(8001,'/readyz',200),(8001,'/livez',200),(8001,'/metrics',404),(9090,'/metrics',200)]:
 url='http://10.244.69.193:'+str(port)+path
 try:
  with opener.open(url,timeout=2) as r:code=r.status;data=r.read(65537)
 except urllib.error.HTTPError as e:code=e.code;data=e.read(65537)
 assert len(data)<=65536
 row={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':code,'expected':expected,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 if port==9090:
  row['selected_metric_lines']=[line for line in data.decode().splitlines() if line.startswith(('# HELP fds_','# TYPE fds_','fds_detected_total','fds_evaluated_total'))]
 rows.append(row)
print(json.dumps({'scope':'READ_ONLY_PRECHECK','http_mutations':0,'rows':rows}))
raise SystemExit(0 if all(x['status']==x['expected'] for x in rows) else 2)
