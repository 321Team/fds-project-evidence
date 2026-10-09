"""Read known controller inputs only; no Ansible, wrapper, inventory or worker calls."""
import datetime,hashlib,json,os,pathlib,pwd,socket,stat,subprocess,sys
HOME=pathlib.Path('/home/server01_ansible')
PREP=HOME/'worker02-dns-stage.yJfHG0vS/source'
OLD=HOME/'p1-ans-01'
VENV=HOME/'ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3'
INPUTS=['ansible.cfg','inventory/hosts.yml','inventory/group_vars/all.yml',
        'scripts/cr-p1-ans-01-01-run.sh','scripts/cr-p1-mon-01-01-run.sh',
        'scripts/cr-p1-ntp-01-01-run.sh','scripts/p1-k8s-01-gate0-run.sh',
        'scripts/lib/ansible-engine.sh','playbooks/cr-p1-ans-01-01-verify-worker02.yml',
        'roles/dns_resolver/tasks/main.yml','roles/dns_resolver/tasks/verify.yml',
        'playbooks/cr-p1-ans-01-01-apply-workers.yml']
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    if socket.gethostname()!='ansible01' or pwd.getpwuid(os.getuid()).pw_name!='server01_ansible' or os.getuid()!=1000:
        raise ValueError('HOST_ACCOUNT')
    if not '2026-10-09T09:10:00+09:00'<=now()<'2026-10-09T12:00:00+09:00':raise ValueError('WINDOW')
def metadata(s):return dict(uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),size=s.st_size,dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def read(path):
    gate()
    if path.resolve()!=path:raise ValueError('LINK_PATH')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>1048576 or a.st_nlink!=1:raise ValueError('FILE_BOUNDARY')
        raw=f.read(a.st_size+1);b=os.fstat(f.fileno())
    if len(raw)!=a.st_size or metadata(a)!=metadata(b) or metadata(a)!=metadata(path.lstat()):raise ValueError('READ_DRIFT')
    return raw,dict(path=str(path),metadata=metadata(a),sha256=hashlib.sha256(raw).hexdigest(),stable=True)
def git(root,args):
    gate();cmd=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null','-C',str(root),*args]
    p=subprocess.run(cmd,capture_output=True,timeout=12,env={'PATH':'/usr/bin:/bin','HOME':str(HOME),'LANG':'C','GIT_OPTIONAL_LOCKS':'0','GIT_NO_REPLACE_OBJECTS':'1'})
    if len(p.stdout)>2097152 or len(p.stderr)>16384:raise ValueError('QUERY_SIZE')
    return p,cmd
def main():
    gate();out=dict(schema='fds.ansible-controller-preparation.v1',host=socket.gethostname(),user=pwd.getpwuid(os.getuid()).pw_name,
                   started_at_kst=now(),checkouts=[],engine_metadata=[],access_metadata=[],remote_write=False,
                   cli_execution='NOT_RUN',managed_host_connections=0,role_apply='NOT_RUN',engine_switch='NOT_RUN',status='INCOMPLETE')
    try:
        for root in (OLD,PREP):
            entry=dict(path=str(root),queries=[],inputs=[]);out['checkouts'].append(entry)
            for args in (['rev-parse','HEAD'],['status','--porcelain','--untracked-files=no'],['rev-parse','--is-shallow-repository'],['merge-base','--is-ancestor','98cf3f826ac0805bcc771ad760a15d931c1bd414','HEAD']):
                p,cmd=git(root,args);entry['queries'].append(dict(command=cmd,rc=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
            head=entry['queries'][0]['stdout'].strip()
            for name in INPUTS:
                path=root/name
                if not path.exists():entry['inputs'].append(dict(relative_path=name,status='ABSENT'));continue
                raw,row=read(path);p,cmd=git(root,['show',head+':'+name])
                row.update(relative_path=name,status='COLLECTED',git_blob_rc=p.returncode,
                           git_blob_sha256=hashlib.sha256(p.stdout).hexdigest() if p.returncode==0 else None,
                           matches_checkout_commit=p.returncode==0 and p.stdout==raw)
                entry['inputs'].append(row)
            p,cmd=git(root,['rev-parse','HEAD']);entry['head_after']=p.stdout.decode().strip()
            if p.returncode or entry['head_after']!=head:raise ValueError('CHECKOUT_HEAD_DRIFT')
        for name in ('ansible','ansible-playbook','ansible-inventory','ansible-config'):
            raw,row=read(VENV/'bin'/name);row['first_line']=raw.splitlines()[0].decode('ascii');out['engine_metadata'].append(row)
        # Read installation declarations only; do not import the candidate package.
        for suffix in ('pyvenv.cfg','lib/python3.12/site-packages/ansible_core-2.21.3.dist-info/METADATA'):
            path=VENV/suffix
            if not path.exists():out['engine_metadata'].append(dict(path=str(path),status='ABSENT'));continue
            raw,row=read(path)
            row['declarations']=[line for line in raw.decode('utf-8').splitlines() if line.startswith(('Name: ','Version: ','version = '))]
            out['engine_metadata'].append(row)
        for path in (HOME/'.ssh/p1_ansible_ed25519',HOME/'.ssh/known_hosts',VENV/'bin/python',HOME/'.ssh'):
            gate();s=path.lstat()
            out['access_metadata'].append(dict(path=str(path),metadata=metadata(s),is_symlink=stat.S_ISLNK(s.st_mode),resolved_path=str(path.resolve())))
        gate();out['status']='COLLECTED'
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        out['error_type']=type(exc).__name__;out['error_code']=str(exc) if isinstance(exc,ValueError) else 'READ_OR_QUERY_FAILED'
    out['finished_at_kst']=now();print(json.dumps(out,sort_keys=True));return 0 if out['status']=='COLLECTED' else 2
if __name__=='__main__':sys.exit(main())
