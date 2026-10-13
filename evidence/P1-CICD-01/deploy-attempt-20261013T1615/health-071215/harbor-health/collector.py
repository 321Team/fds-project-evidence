"""Two unauthenticated HTTPS GETs with existing system CA; no trust changes."""
import datetime,hashlib,http.client,json,os,socket,ssl
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000
out={'host':socket.gethostname(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authentication':'NONE','trust':'EXISTING_SYSTEM_CA','mutation':False,'requests':[]}
ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
for path in ('/api/v2.0/ping','/api/v2.0/health'):
    row={'path':path};conn=http.client.HTTPSConnection('10.1.93.54',443,timeout=8,context=ctx)
    try:
        conn.connect();row.update(tls_verified=True,tls_version=conn.sock.version(),peer_der_sha256=hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest())
        conn.request('GET',path,headers={'Accept':'application/json'});r=conn.getresponse();raw=r.read(65537);assert len(raw)<=65536
        row.update(http_status=r.status,body_sha256=hashlib.sha256(raw).hexdigest())
        if path.endswith('health') and r.status==200:
            x=json.loads(raw);row['status']=x.get('status');row['components']=[{k:v.get(k) for k in ('name','status')} for v in x.get('components',[])]
    except Exception as e:row['error_type']=type(e).__name__
    finally:conn.close()
    out['requests'].append(row)
print(json.dumps(out,sort_keys=True))
