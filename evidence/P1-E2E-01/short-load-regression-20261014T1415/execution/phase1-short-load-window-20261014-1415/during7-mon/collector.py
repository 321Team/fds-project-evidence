"""Owned loopback PF; fixed reviewed queries; GET only; always reap own child."""
import datetime,hashlib,json,math,os,pathlib,select,socket,subprocess,time,urllib.parse,urllib.request
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
root=pathlib.Path('/var/tmp/p1-short-load-202610141415')
supply=root/'supply'
hashes={'q_range.py':'5b59d0d5d8205154b350377599645734f801154f1532681453a8cf27b65cfd85','promql.txt':'deccc54929862a137de59ae8f4d32b62b23a4461a2de77249381eb19863d91a1'}
for name,want in hashes.items():assert hashlib.sha256((supply/name).read_bytes()).hexdigest()==want
queries={line[:2]:line.split('=',1)[1] for line in (supply/'promql.txt').read_text().splitlines() if line[:3] in ('Q1_','Q2_','Q3_')}
queries.update(all_up='up',save_success='sum(transaction_save_success_total)',save_failure='sum(transaction_save_failure_total)',evaluated='sum(fds_evaluated_total)',detected='sum by(rule_id)(fds_detected_total)')
queries['Q3_DENOM']=queries['Q3'].split(' / ',1)[1]
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
out={'host':socket.gethostname(),'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':[],'post':0,'own_pf':True,'errors':[]}
s=socket.socket();s.bind(('127.0.0.1',19091));s.close()
p=subprocess.Popen(kc+['-n','monitoring-api','port-forward','--address=127.0.0.1','svc/prometheus','19091:9090'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
first=b''
try:
    deadline=time.monotonic()+10;ready=False
    while time.monotonic()<deadline and p.poll() is None:
        if select.select([p.stdout],[],[],.2)[0]:
            first=p.stdout.readline()
            ready=first.startswith(b'Forwarding from 127.0.0.1:19091 -> 9090');break
    if not ready:raise RuntimeError('OWN_PF_NOT_READY')
    check=subprocess.run(['/usr/bin/python3','-B','-I',str(supply/'q_range.py'),'check'],cwd=str(supply),capture_output=True,timeout=35)
    out['reviewed_q_range_check']={'rc':check.returncode,'stdout':check.stdout.decode(),'stderr':check.stderr.decode()}
    if check.returncode:raise RuntimeError('REVIEWED_Q_CHECK_FAILED')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    query_time=time.time();out['query_time']=query_time
    for name,query in queries.items():
        url='http://127.0.0.1:19091/api/v1/query?'+urllib.parse.urlencode({'query':query,'time':str(query_time)})
        with opener.open(url,timeout=5) as res:raw=res.read(1024*1024+1)
        if len(raw)>1024*1024:raise RuntimeError('QUERY_OUTPUT_LIMIT')
        data=json.loads(raw)
        out['queries'].append({'name':name,'query':query,'raw':raw.decode(),'sha256':hashlib.sha256(raw).hexdigest()})
        if data.get('status')!='success':raise RuntimeError('QUERY_NOT_SUCCESS_'+name)
except Exception as ex:
    out['errors'].append(type(ex).__name__+':'+str(ex))
finally:
    if p.poll() is None:p.terminate()
    try:stdout,stderr=p.communicate(timeout=3)
    except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate(timeout=2)
    out.update(forwarder_pid=p.pid,forwarder_stopped=p.poll() is not None,forward_stdout=(first+stdout).decode(),forward_stderr=stderr.decode())
    probe=socket.socket();probe.settimeout(1)
    try:out['listener_absent']=probe.connect_ex(('127.0.0.1',19091))!=0
    finally:probe.close()
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(out,sort_keys=True))
raise SystemExit(0 if not out['errors'] and out['forwarder_stopped'] and out['listener_absent'] else 2)
