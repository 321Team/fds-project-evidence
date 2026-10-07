import datetime,json,pathlib,shlex,subprocess
r=pathlib.Path(__file__).resolve().parent
results=[]
remote="sudo -n python3 -c "+shlex.quote("import json,os,socket,shutil; print(json.dumps({'hostname':socket.gethostname(),'uid':os.geteuid(),'tools':{x:shutil.which(x) for x in ['python3','tcpdump','nsenter','crictl']}}))")
for ip in ('10.1.93.50','10.1.93.105','10.1.93.107','10.1.93.108'):
    inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=6','svc_ansible@'+ip,remote]
    cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=6','fds-ansible01',shlex.join(inner)]
    q={'target':ip,'command':cmd,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        p=subprocess.run(cmd,capture_output=True,timeout=18)
        q.update(rc=p.returncode,stdout=p.stdout.decode(errors='replace'),stderr=p.stderr.decode(errors='replace'))
    except subprocess.TimeoutExpired: q.update(rc=124,error='SSH timeout')
    q['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    results.append(q)
(r/'edge-access.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
for q in results: print(q['target'],q['rc'],q.get('stdout',''),q.get('stderr',''))
