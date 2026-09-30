import json,sys,urllib.request,urllib.parse,time
k,q=sys.argv[1],sys.argv[2]
r=json.load(urllib.request.urlopen('http://127.0.0.1:19090/api/v1/query?'+urllib.parse.urlencode({'query':q}),timeout=5))['data']['result']
print(time.strftime('%H:%M:%S'),k,' '.join(f"{x['metric'].get('pod','-')}={float(x['value'][1]):.4g}" for x in sorted(r,key=lambda x:x['metric'].get('pod',''))),flush=True)
