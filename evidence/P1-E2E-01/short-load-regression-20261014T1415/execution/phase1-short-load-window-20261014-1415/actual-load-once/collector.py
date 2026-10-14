"""Execute the unchanged reviewed generator once in the confirmed time window."""
import datetime,hashlib,json,os,pathlib,signal,socket,subprocess,time
assert socket.gethostname()=='edge01' and os.geteuid()==1003
root=pathlib.Path('/home/svc_ansible/p1-short-load-202610141415');out=root/'results';src=root/'supply/gen3.py'
assert root.stat().st_uid==1003 and root.stat().st_mode&0o777==0o700
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e5942646ba2544275b7664bbbc296d841920a0d1dac23421f96f1cc20e766b29'
now=datetime.datetime.now(datetime.timezone.utc)
start=datetime.datetime(2026,10,14,5,15,tzinfo=datetime.timezone.utc)
latest=datetime.datetime(2026,10,14,5,25,tzinfo=datetime.timezone.utc)
assert start<=now<=latest,'OUTSIDE_APPROVED_START_WINDOW'
assert not any(out.iterdir()),'RESULTS_NOT_EMPTY_NO_REPEAT'
os.umask(0o077)
def write_new(path,obj):
    with path.open('x') as f:json.dump(obj,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
argv=['/usr/bin/python3','-B','-I',str(src),'202610141415',str(out),'--profile','regression']
write_new(out/'launch-attempt.json',{'run':'202610141415','utc':now.isoformat(),'argv':argv,'merge':'654d7762c3e6f4cc195c4628b42d0b47c3f8e17e','automatic_retry':False})
with (out/'stages.log').open('xb') as log:
    p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    stat=pathlib.Path('/proc/'+str(p.pid)+'/stat').read_text()
    identity={'pid':p.pid,'start_ticks':stat[stat.rfind(')')+2:].split()[19],'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'argv':argv}
    write_new(out/'process.json',identity)
    timeout=False
    try:rc=p.wait(timeout=450)
    except subprocess.TimeoutExpired:
        timeout=True
        if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
        rc=p.wait(timeout=15)
    log.flush();os.fsync(log.fileno())
result={'run':'202610141415','finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generator_rc':rc,'supervisor_timeout':timeout,'pid':p.pid,'process_reaped':p.poll() is not None,'stages_sha256':hashlib.sha256((out/'stages.log').read_bytes()).hexdigest(),'requests_sha256':hashlib.sha256((out/'requests.log').read_bytes()).hexdigest() if (out/'requests.log').exists() else None}
write_new(out/'completion.json',result)
print(json.dumps(result))
raise SystemExit(0 if rc==0 and not timeout else 2)
