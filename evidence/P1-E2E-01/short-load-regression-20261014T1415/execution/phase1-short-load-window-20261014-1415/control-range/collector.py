START_EPOCH=1791954912.031
END_EPOCH=1791955332.036
"""START_EPOCH/END_EPOCH are prepended from the actual preserved stages.log."""
import base64,datetime,hashlib,json,os,pathlib,select,socket,subprocess,time,urllib.parse,urllib.request
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
assert 0<END_EPOCH-START_EPOCH<500 and END_EPOCH<=time.time()+2
root=pathlib.Path('/var/tmp/p1-short-load-202610141415');supply=root/'supply';out=root/'results'
assert not any(out.iterdir()),'RANGE_ALREADY_COLLECTED_NO_OVERWRITE'
os.umask(0o077)
hashes={'q_range.py':'5b59d0d5d8205154b350377599645734f801154f1532681453a8cf27b65cfd85','promql.txt':'deccc54929862a137de59ae8f4d32b62b23a4461a2de77249381eb19863d91a1'}
for name,want in hashes.items():assert hashlib.sha256((supply/name).read_bytes()).hexdigest()==want
with (out/'promql.txt').open('xb') as f:f.write((supply/'promql.txt').read_bytes())
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
sock=socket.socket();sock.bind(('127.0.0.1',19091));sock.close()
p=subprocess.Popen(kc+['-n','monitoring-api','port-forward','--address=127.0.0.1','svc/prometheus','19091:9090'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
report={'start':START_EPOCH,'end':END_EPOCH,'step':15,'errors':[]};first=b''
try:
    deadline=time.monotonic()+10;ready=False
    while time.monotonic()<deadline and p.poll() is None:
        if select.select([p.stdout],[],[],.2)[0]:
            first=p.stdout.readline();ready=first.startswith(b'Forwarding from 127.0.0.1:19091 -> 9090');break
    if not ready:raise RuntimeError('OWN_PF_NOT_READY')
    argv=['/usr/bin/python3','-B','-I',str(supply/'q_range.py'),str(START_EPOCH),str(END_EPOCH)]
    q=subprocess.run(argv,cwd=str(out),capture_output=True,timeout=100)
    report['q_range']={'argv':argv,'rc':q.returncode,'stdout':q.stdout.decode(),'stderr':q.stderr.decode()}
    if q.returncode:raise RuntimeError('REVIEWED_RANGE_FAILED')
    fixed={line[:2]:line.split('=',1)[1] for line in (supply/'promql.txt').read_text().splitlines() if line[:3] in ('Q1_','Q2_','Q3_')}
    denom=fixed['Q3'].split(' / ',1)[1]
    url='http://127.0.0.1:19091/api/v1/query_range?'+urllib.parse.urlencode({'query':denom,'start':str(START_EPOCH),'end':str(END_EPOCH),'step':'15'})
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url,timeout=30) as response:raw=response.read(2*1024*1024+1)
    assert len(raw)<=2*1024*1024
    with (out/'q3-denominator.json').open('xb') as f:f.write(raw)
    report['denominator_query']=denom
except Exception as e:report['errors'].append(type(e).__name__+':'+str(e))
finally:
    if p.poll() is None:p.terminate()
    try:stdout,stderr=p.communicate(timeout=3)
    except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate(timeout=2)
    report.update(pf_pid=p.pid,pf_stopped=p.poll() is not None,pf_stdout=(first+stdout).decode(),pf_stderr=stderr.decode())
    s=socket.socket();s.settimeout(1)
    try:report['listener_absent']=s.connect_ex(('127.0.0.1',19091))!=0
    finally:s.close()
report['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (out/'range-receipt.json').open('x') as f:json.dump(report,f,sort_keys=True)
files=[]
for path in sorted(out.iterdir()):
    assert path.is_file() and not path.is_symlink()
    raw=path.read_bytes();assert len(raw)<2*1024*1024
    files.append({'name':path.name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'report':report,'files':files}))
raise SystemExit(0 if not report['errors'] and report['pf_stopped'] and report['listener_absent'] else 2)
