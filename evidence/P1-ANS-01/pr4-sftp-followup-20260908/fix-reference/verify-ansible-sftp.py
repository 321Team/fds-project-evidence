#!/usr/bin/env python3
"""Verify corrected SSH argument separation using SFTP-only Ansible ping."""
from pathlib import Path
import contextlib, hashlib, importlib.util, io, json, os, pwd, re, shlex, tempfile
from datetime import datetime, timezone
HELPER_SHA='19ded0e766aafda36fe9227664dabd171fdb688656cf6d4b30b2f4ff78321874'
BASE=Path(__file__).resolve().parent

def load_helper():
    f=BASE/'collect-sftp-followup.py'
    if not f.is_file() or f.is_symlink() or hashlib.sha256(f.read_bytes()).hexdigest()!=HELPER_SHA:
        raise RuntimeError('Required original collect-sftp-followup.py missing or changed')
    spec=importlib.util.spec_from_file_location('sftp_read_helper',f)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    return h

def transport_vars(home):
    common=['-F','/dev/null','-i',str(home/'.ssh/p1_ansible_ed25519')]
    for option in ['BatchMode=yes','PreferredAuthentications=publickey','PasswordAuthentication=no',
        'KbdInteractiveAuthentication=no','StrictHostKeyChecking=yes','UserKnownHostsFile='+str(home/'.ssh/known_hosts'),
        'IdentitiesOnly=yes','IdentityAgent=none','ControlMaster=no','ControlPersist=no','ControlPath=none',
        'ConnectTimeout=10','ConnectionAttempts=1','ServerAliveInterval=10','ServerAliveCountMax=2']:
        common+=['-o',option]
    return dict(ansible_ssh_common_args=shlex.join(common),ansible_ssh_extra_args='-T',
        ansible_connection='ssh',ansible_user='svc_ansible',ansible_become=False,
        ansible_python_interpreter='/usr/bin/python3',ansible_pipelining=False,
        ansible_ssh_use_tty=False,ansible_ssh_transfer_method='sftp',ansible_sftp_batch_mode=True)

def valid_ping(host,result):
    if result['rc']!=0 or '[WARNING]' in result['stderr']+result['stdout']:
        return False
    rows=re.findall(r'^([^\s]+) \| SUCCESS => (\{.*\})\s*$',result['stdout'],re.M)
    if len(rows)!=1 or rows[0][0]!=host:
        return False
    try:r=json.loads(rows[0][1])
    except json.JSONDecodeError:return False
    if r.get('ping')!='pong' or r.get('changed') is not False or any(r.get(k) for k in ['failed','unreachable','skipped','warnings','exception']):
        return False
    # Verbose CLI receipt must show a real SFTP command with a put operation.
    text=result['stdout']+'\n'+result['stderr']
    return 'SSH: EXEC sftp' in text and 'put ' in text

def main():
    h=load_helper();os.umask(0o077);home=Path.home();repo=home/'p1-ans-01'
    if os.geteuid()==0 or pwd.getpwuid(os.geteuid()).pw_name!='server01_ansible':raise RuntimeError('Run as server01_ansible without sudo')
    check=h.run(['/usr/bin/hostnamectl','--static'])
    if check['rc']!=0 or check['stdout'].strip()!='ansible01':raise RuntimeError('Run on ansible01')
    h.verify_repo(repo)
    for p in [home/'.ssh/p1_ansible_ed25519',home/'.ssh/known_hosts']:
        if not p.is_file() or p.is_symlink():raise RuntimeError('Existing SSH input missing or symlink')
    known=home/'.ssh/known_hosts';known_before=(h.digest(known),known.stat().st_mtime_ns)
    out=Path(tempfile.mkdtemp(prefix='FDS_Ansible_SFTP_Verify.',dir=home))
    report=dict(status='REVIEW_REQUIRED',schema_version=1,scope='ANSIBLE_PING_ONLY_WITH_SFTP_UPLOAD_AND_TEMP_MODULE_CLEANUP',
        code_commit=h.APPROVED,started_at=datetime.now(timezone.utc).isoformat(),nodes=[],
        runtime_upgrade='NOT_PERFORMED',bootstrap='HOLD',original_fallback='NOT_RECONSTRUCTED')
    def save(name,result):
        (out/(name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
    env={k:v for k,v in os.environ.items() if not k.startswith(('ANSIBLE_','PR3_REVIEW_','PYTHON'))}
    env.update(PATH='/usr/bin:/bin',HOME=str(home),LANG='C.UTF-8',ANSIBLE_NOCOLOR='1',ANSIBLE_HOST_KEY_CHECKING='True',
        ANSIBLE_CONFIG=str(repo/'ansible.cfg'),ANSIBLE_SSH_ARGS='-F /dev/null -o ControlMaster=no -o ControlPersist=no -o ControlPath=none',
        ANSIBLE_SSH_USETTY='False',ANSIBLE_LOCAL_TEMP=str(out/'ansible-local'),PYTHONDONTWRITEBYTECODE='1')
    try:
        version=save('engine',h.run(['/usr/bin/ansible','--version'],cwd=repo,env=env))
        if version['rc']!=0 or '[core 2.16.19]' not in version['stdout']:raise RuntimeError('Expected 2.16.19 engine')
        negative=save('local_invalid_sftp_option',h.run(['/usr/bin/sftp','-T'],env=env))
        report['invalid_T_reproduced']=negative['rc']!=0 and bool(re.search(r'(?:unknown|illegal|invalid) option[^\n]*T',negative['stderr']+negative['stdout'],re.I))
        if not report['invalid_T_reproduced']:raise RuntimeError('Expected local invalid -T behavior not reproduced')
        vars_file=out/'execution-vars.json';vars_file.write_text(json.dumps(transport_vars(home),indent=2)+'\n')
        for host,ip in h.NODES.items():
            before=save(host+'_before',h.remote_snapshot(home,host,ip))
            if before['rc']!=0:raise RuntimeError(host+': SSH/context precheck failed')
            cmd=['/usr/bin/ansible',host,'-i',str(repo/'inventory/hosts.yml'),'--private-key',str(home/'.ssh/p1_ansible_ed25519'),
                '-e','@'+str(vars_file),'-m','ansible.builtin.ping','--one-line','-vvv']
            result=save(host+'_ansible_sftp_ping',h.run(cmd,cwd=repo,env=env,timeout=45))
            after=save(host+'_after',h.remote_snapshot(home,host,ip))
            state_ok=after['rc']==0 and before.get('parsed')==after.get('parsed')
            ok=valid_ping(host,result) and state_ok
            report['nodes'].append(dict(host=host,ip=ip,status='PASS' if ok else 'REVIEW_REQUIRED',rc=result['rc'],state_unchanged=state_ok))
            print(host+'='+report['nodes'][-1]['status'],flush=True)
            if not ok:raise RuntimeError(host+': SFTP-only Ansible ping/receipt/state check failed; next node not started')
        h.verify_repo(repo)
        if (h.digest(known),known.stat().st_mtime_ns)!=known_before:raise RuntimeError('known_hosts changed')
        report['status']='SFTP_ONLY_ANSIBLE_VERIFIED_REVIEW_REQUIRED'
        report['source_and_known_hosts_preserved']=True
    except Exception as e:report['error']=h.scrub(str(e))
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    # Use the established exporter, then rename this receipt to a distinct artifact.
    with contextlib.redirect_stdout(io.StringIO()):
        h.export(out,report)
    old=out/'FDS_SFTP_Followup_Result.tar.gz';old_side=out/(old.name+'.sha256')
    archive=out/'FDS_Ansible_SFTP_Verify_Result.tar.gz';old.rename(archive);old_side.unlink()
    side=out/(archive.name+'.sha256');side.write_text(h.digest(archive)+'  '+archive.name+'\n')
    print('STATUS='+report['status']);print('ARCHIVE='+str(archive));print('SIDECAR='+str(side))

if __name__=='__main__':
    try:main()
    except Exception as e:print('STOP='+str(e));raise SystemExit(1)
