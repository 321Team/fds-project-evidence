"""Anonymous fixed GitHub transport checks, no credentials or bypasses."""
import datetime,json,os,socket,ssl,subprocess,urllib.request,urllib.error
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'credential_access':False,'configuration_change':False,'requests':[]}
out['dns_addresses']=sorted({row[4][0] for row in socket.getaddrinfo('github.com',443,type=socket.SOCK_STREAM)})
out['git_version']=subprocess.check_output(['/usr/bin/git','--version'],timeout=5).decode().strip()
ctx=ssl.create_default_context()
for url in ('https://github.com/','https://github.com/321Team/fds-msa.git/info/refs?service=git-upload-pack'):
    item={'url':url,'authenticated':False,'tls_verification':True,'method':'GET'}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Phase1-readonly-transport-precheck'})
        with urllib.request.urlopen(req,timeout=10,context=ctx) as response:item['status']=response.status
    except urllib.error.HTTPError as exc:item['status']=exc.code
    except Exception as exc:item['error_class']=type(exc).__name__
    out['requests'].append(item)
print(json.dumps(out))
