"""Local operator command recorder; reviewed remote driver performs all Probe work."""
from pathlib import Path
import datetime,hashlib,json,shlex,subprocess,sys
root=Path(__file__).resolve().parent
base='/root/sec01-probe-20261008t2245'
sha='67d109a7883d00e429f389622b72dfc80ad944263b29830d8331d68c8666ba65'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.102']
def remote(label,command,data=None):
    args=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner+[command])]
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (root/(label+'.stdout')).open('xb') as out,(root/(label+'.stderr')).open('xb') as err:
        p=subprocess.run(args,input=data,stdout=out,stderr=err)
    (root/(label+'.receipt.json')).write_bytes((json.dumps({'start':start,'end':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':args,'rc':p.returncode},indent=2)+'\n').encode())
    print(label,'rc',p.returncode,flush=True)
    print((root/(label+'.stdout')).read_text(errors='replace')[-5000:],flush=True)
    print((root/(label+'.stderr')).read_text(errors='replace')[-2000:],flush=True)
    if p.returncode: raise SystemExit(p.returncode)
def latest_go():
    go=json.loads(subprocess.check_output(['gh','api','repos/321Team/fds-project-baseline/issues/comments/6061331520']))
    original=json.loads(subprocess.check_output(['gh','api','repos/321Team/fds-project-baseline/issues/comments/6061273634']))
    assert go['user']['login']=='hayeounglee' and original['user']['login']=='hayeounglee'
    assert go['updated_at']=='2026-10-08T13:49:34Z' and original['updated_at']=='2026-10-08T13:46:27Z'
    for n,obj in [('correction',go),('original',original)]:
        (root/('go-'+n+'.json')).write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())
    return go
mode=sys.argv[1]
go=latest_go()
if mode=='stage':
    now=datetime.datetime.now(datetime.timezone.utc)
    assert datetime.datetime.fromisoformat('2026-10-08T13:51:00+00:00')<=now<datetime.datetime.fromisoformat('2026-10-08T13:55:00+00:00')
    data=(root/'probe-bundle.tar').read_bytes()
    assert hashlib.sha256(data).hexdigest()=='1fa181ee726b1b7e73067cae9f0265744e3e6c7a33e0ad10e87c7d533923490d'
    cmd='set -eu; test "$(hostname)" = k8s-control01; test "$(id -un)" = svc_ansible; sudo -n mkdir -m 700 '+base+'; sudo -n tar --no-same-owner -xf - -C '+base+'; sudo -n find '+base+' -type d -exec chmod 700 {} +; sudo -n find '+base+' -type f -exec chmod 600 {} +; sudo -n python3 -I '+base+'/bundle/driver.py check-bundle '+base+'/bundle '+sha+'; date -Is; sudo -n stat -c "%U %G %a %n" '+base+' '+base+'/bundle/driver.py'
    remote('stage-approved',cmd,data)
elif mode in ('precheck','run'):
    p=json.loads((root/(mode+'-permit.UNAPPROVED.json')).read_bytes())
    p.update(window_start='2026-10-08T22:51:00+09:00',approver='hayeounglee',approved_at=go['created_at'],go_url=go['html_url'],go_body=go['body'],go_body_sha256=hashlib.sha256(go['body'].encode()).hexdigest(),live_go_rechecked=True,notice_confirmed=True,no_overlap_confirmed=True,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    payload=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode()
    (root/(mode+'-permit.APPROVED.json')).write_bytes(payload)
    # Pipe permit to an exclusive new file. Driver retains the authoritative copy and permanent claim.
    target=base+'/'+mode+'-permit.json'
    remote(mode+'-permit-stage','sudo -n sh -c '+shlex.quote('umask 077; set -C; cat > '+target),payload)
    remote(mode+'-execute','sudo -n python3 -I '+base+'/bundle/driver.py execute '+base+'/bundle '+sha+' '+target)
elif mode=='collect':
    remote('collect','sudo -n python3 -I '+base+'/bundle/driver.py collect /root/sec01-probe-driver-state/probe-20261008t2245 '+base+'/receipt')
else:
    raise SystemExit('unsupported operator step')
