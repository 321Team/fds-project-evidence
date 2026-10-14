"""Use only if a real stop condition is observed; targets the recorded generator only."""
import datetime,json,os,pathlib,signal,socket
assert socket.gethostname()=='edge01' and os.geteuid()==1003
root=pathlib.Path('/home/svc_ansible/p1-short-load-202610141415/results')
identity=json.loads((root/'process.json').read_bytes());pid=identity['pid']
assert isinstance(pid,int) and pid>1
proc=pathlib.Path('/proc')/str(pid)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':pid,'signal_sent':False}
if proc.exists():
    assert proc.stat().st_uid==1003
    stat=proc.joinpath('stat').read_text()
    assert stat[stat.rfind(')')+2:].split()[19]==identity['start_ticks']
    assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==identity['boot']
    argv=[v.decode() for v in proc.joinpath('cmdline').read_bytes().split(b'\0') if v]
    assert argv==identity['argv'] and os.getpgid(pid)==pid
    os.killpg(pid,signal.SIGTERM);out['signal_sent']=True
else:out['already_exited']=True
print(json.dumps(out))
