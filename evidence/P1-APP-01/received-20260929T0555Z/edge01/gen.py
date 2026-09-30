import json,time,sys,random,threading,http.client
from concurrent.futures import ThreadPoolExecutor
RUN,OUT=sys.argv[1],sys.argv[2]; random.seed(RUN)
W=['10.1.93.105','10.1.93.107','10.1.93.108']; ST=[('S1',5,90),('S2',20,90),('S3',50,90)]
lk=threading.Lock(); f=open(OUT+'/requests.log','a')
def send(i,st,tp):
    w=W[i%3]; b=json.dumps({"account_id":f"SIM_load_{RUN}_{i}","amount":10000,"currency":"KRW","transaction_type":tp,"source_ip":"198.51.100.10"})
    t0=time.time()
    try:
        c=http.client.HTTPConnection(w,30080,timeout=10); c.request('POST','/api/v1/transactions',b,{'Content-Type':'application/json'}); r=c.getresponse(); r.read(); code=r.status; c.close()
    except Exception: code=-1
    with lk: f.write(f"{t0:.3f} {st} {w} {tp} {code} {(time.time()-t0)*1000:.1f}\n")
with ThreadPoolExecutor(max_workers=64) as ex:
    i=0
    for st,rps,dur in ST:
        print(time.strftime('%H:%M:%S'),'START',st,rps,'rps',flush=True); s=time.time(); k=0
        while time.time()-s<dur:
            tgt=s+k/rps; d=tgt-time.time()
            if d>0: time.sleep(min(d,0.05)); continue
            x=random.random(); ex.submit(send,i,st,'deposit' if x<0.6 else ('withdrawal' if x<0.8 else 'transfer')); i+=1; k+=1
        print(time.strftime('%H:%M:%S'),'END',st,'sent',k,flush=True)
f.close()
