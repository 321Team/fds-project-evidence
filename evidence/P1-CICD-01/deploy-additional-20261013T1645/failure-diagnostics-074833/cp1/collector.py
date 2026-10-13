"""Read one observed failing Pod and selected diagnostic facts; no raw log export."""
import datetime,hashlib,json,os,re,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
name='transaction-api-85fc54b98f-q7lxv'
base='/api/v1/namespaces/fds-app/pods/'+name
def get(path):
    args=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
    r=subprocess.run(args,capture_output=True,timeout=15)
    return r,{'argv':args,'rc':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stdout_bytes':len(r.stdout),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()}
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'mutation':False,'raw_logs_exported':False,'pod_name':name,'queries':[]}
r,row=get(base)
if r.returncode==0:
    x=json.loads(r.stdout);row['metadata']={k:x['metadata'].get(k) for k in ('name','uid','resourceVersion','deletionTimestamp')}
    row['phase']=x.get('status',{}).get('phase')
    row['containers']=[]
    for c in x.get('status',{}).get('containerStatuses',[]):
        item={k:c.get(k) for k in ('name','ready','started','restartCount','imageID')}
        for field in ('state','lastState'):
            item[field]={s:{k:v for k,v in facts.items() if k in ('reason','exitCode','signal','startedAt','finishedAt')} for s,facts in c.get(field,{}).items()}
        row['containers'].append(item)
out['queries'].append(row)
for previous in ('false','true'):
    r,row=get(base+'/log?container=transaction-api&timestamps=true&tailLines=160&limitBytes=60000&previous='+previous)
    row['previous']=previous;facts=[]
    if r.returncode==0:
        for line in r.stdout.decode(errors='replace').splitlines():
            # Preserve only fixed error categories, code identifiers, and source locations.
            m=re.search(r'File "([A-Za-z0-9_./-]{1,220})", line ([0-9]+), in ([A-Za-z0-9_<>]+)',line)
            if m:facts.append({'file':m[1],'line':int(m[2]),'function':m[3]})
            for err in ('ModuleNotFoundError','ImportError','PermissionError','FileNotFoundError','ValueError','RuntimeError','TypeError','AttributeError','OSError','ValidationError','ConnectionRefusedError'):
                if err in line:facts.append({'exception_type':err})
            m=re.search(r"No module named ['\"]([A-Za-z0-9_.-]+)['\"]",line)
            if m:facts.append({'missing_module':m[1]})
            m=re.search(r"cannot import name ['\"]([A-Za-z0-9_]+)['\"] from ['\"]([A-Za-z0-9_.]+)['\"]",line)
            if m:facts.append({'missing_import':m[1],'from_module':m[2]})
            m=re.search(r"(Permission denied|No such file or directory): ['\"](/[A-Za-z0-9_./-]{1,220})['\"]",line)
            if m:facts.append({'filesystem_error':m[1],'path':m[2]})
            if 'Application startup failed' in line:facts.append({'fixed_diagnostic':'Application startup failed'})
            if 'Error loading ASGI app' in line:facts.append({'fixed_diagnostic':'Error loading ASGI app'})
            for text in ("can't open file",'cannot open','No such file or directory','not found','unrecognized arguments','invalid option','Permission denied'):
                if text in line:
                    facts.append({'fixed_diagnostic':text,'quoted_paths':re.findall(r"['\"](/[A-Za-z0-9_./-]{1,220})['\"]",line)})
    row['selected_diagnostic_facts']=facts;out['queries'].append(row)
print(json.dumps(out,sort_keys=True))
