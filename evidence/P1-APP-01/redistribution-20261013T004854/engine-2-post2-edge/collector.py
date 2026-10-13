import datetime,hashlib,json,os,socket,subprocess,time
assert socket.gethostname()=='edge01','STOP_HOST'
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'scope':'four fixed readyz GETs; no nginx reload/config/policy change; response bodies not retained','requests':[]}
for url in ['http://127.0.0.1/readyz']+['http://'+ip+':30080/readyz' for ip in ['10.1.93.105','10.1.93.107','10.1.93.108']]:
 argv=['/usr/bin/curl','--disable','--noproxy','*','--connect-timeout','2','--max-time','4','--silent','--show-error','--max-filesize','65536','--write-out','\n%{http_code}\n',url]
 start=time.monotonic();p=subprocess.run(argv,capture_output=True,timeout=6)
 parts=p.stdout.rsplit(b'\n',2);code=parts[-2].decode(errors='replace') if len(parts)==3 else None;body=parts[0] if len(parts)==3 else p.stdout
 out['requests'].append({'argv':argv,'url':url,'rc':p.returncode,'http_code':code,'elapsed_ms':round((time.monotonic()-start)*1000),'body_size':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'stderr':p.stderr.decode(errors='replace')})
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(out))
