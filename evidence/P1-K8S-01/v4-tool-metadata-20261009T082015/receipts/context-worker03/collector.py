"""Read policy default contexts; never relabel or load policy."""
import datetime,json,os,pathlib,socket,stat,subprocess
EXPECTED_HOST='k8s-worker03'
ROOT=pathlib.Path('/opt/fds/P1-K8S-01-v4')
FILES=('RUNBOOK_FINAL.md','code/audit-window.py','code/cluster-change.py','code/cockpit.sh','code/node-evidence.py','code/prepare-calico.py','code/probe.py','code/regression.py','code/render.py')
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    assert socket.gethostname()==EXPECTED_HOST and os.geteuid()==0,'STOP host/euid'
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00','STOP window'
gate();out={'schema':'fds.k8s-context-expectation.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[], 'boundary':'matchpathcon -n reads local policy defaults; no restorecon/chcon/policy load or tool execution.'}
for name in FILES:
    gate();path=ROOT/name;s=path.lstat();assert stat.S_ISREG(s.st_mode) and path.resolve()==path,'STOP type/path'
    cmd=['matchpathcon','-n',str(path)]
    row={'path':str(path),'command':cmd}
    try:
        p=subprocess.run(cmd,capture_output=True,timeout=3,env={**os.environ,'LC_ALL':'C'})
        row.update(rc=p.returncode,stdout=p.stdout.decode(errors='replace'),stderr=p.stderr.decode(errors='replace'))
    except FileNotFoundError:row.update(rc=127,error='matchpathcon unavailable; no install attempted')
    except subprocess.TimeoutExpired:row.update(rc=124,error='matchpathcon timeout')
    out['queries'].append(row)
out['finished_at_kst']=now();print(json.dumps(out))
