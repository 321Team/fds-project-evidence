"""Local transport of reviewed public source and one native probe invocation."""
import datetime as dt
import hashlib
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
SSH = ['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes',
       '-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01']
SCP = ['C:/Windows/System32/OpenSSH/scp.exe','-o','BatchMode=yes',
       '-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes']
MERGE = '9fb2e2dcac8682a89c4b7c267c833ae8d9aaeb18'
KST = dt.timezone(dt.timedelta(hours=9))

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save(name,obj):
    (OUT/name).write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())

def run(name,args,timeout=60):
    assert not (OUT/(name+'.receipt.json')).exists(), 'Repeated local step'
    start=now()
    try:
        p=subprocess.run(args,capture_output=True,timeout=timeout)
        a,b,rc=p.stdout,p.stderr,p.returncode
    except subprocess.TimeoutExpired as exc:
        a,b,rc=exc.stdout or b'',exc.stderr or b'',None
    (OUT/(name+'.stdout')).write_bytes(a)
    (OUT/(name+'.stderr')).write_bytes(b)
    save(name+'.receipt.json',{'started_at_utc':start,'finished_at_utc':now(),'argv':args,
        'rc':rc,'stdout_sha256':hashlib.sha256(a).hexdigest(),
        'stderr_sha256':hashlib.sha256(b).hexdigest()})
    assert rc==0, (name,rc,'Inspect saved sanitized result; do not retry issuance')
    return a

def command(remote,execute=False):
    binding=json.loads((OUT/'SOURCE_BINDING.json').read_bytes())
    args=['/usr/bin/python3','-I','-B',remote+'/transfer_native_probe.py',
          '--bundle',remote+'/native-source.json','--bundle-sha256',binding['bundle_sha256'],
          '--source-sha',MERGE,'--cp1-key','/home/server01_ansible/.ssh/id_ed25519',
          '--runner-key','/home/server01_ansible/.ssh/p1_ansible_ed25519']
    if execute:
        args+=['--execute','--authorization-expires','2026-10-14T13:10:00+00:00']
    return SSH+[shlex.join(args)]

def main():
    mode=sys.argv[1]
    if mode=='stage':
        identity=run('ansible-identity',SSH+['/usr/bin/id -un && /usr/bin/hostname'])
        assert identity.splitlines()==[b'server01_ansible',b'ansible01']
        remote=run('mkdir-public',SSH+['umask 077 && mktemp -d /home/server01_ansible/FDS_AC07_20261014.XXXXXXXX']).decode().strip()
        assert re.fullmatch(r'/home/server01_ansible/FDS_AC07_20261014\.[A-Za-z0-9]{8}',remote)
        save('PUBLIC_STAGING.json',{'remote_directory':remote,'only_public_source':True,
                                  'source_sha':MERGE,'token_issued':False})
        run('copy-public',SCP+[str(OUT/'source/transfer_native_probe.py'),str(OUT/'native-source.json'),
                              'fds-ansible01:'+remote+'/'])
        paths=[remote+'/transfer_native_probe.py',remote+'/native-source.json']
        result=run('public-hashes',SSH+['chmod 600 '+shlex.join(paths)+' && sha256sum '+shlex.join(paths)]).decode()
        expected={hashlib.sha256((OUT/'source/transfer_native_probe.py').read_bytes()).hexdigest():paths[0],
                  hashlib.sha256((OUT/'native-source.json').read_bytes()).hexdigest():paths[1]}
        assert dict(line.split('  ',1) for line in result.splitlines()) == expected
        print('PUBLIC_SOURCE_STAGED_HASHES_MATCH')
    elif mode=='preflight':
        remote=json.loads((OUT/'PUBLIC_STAGING.json').read_bytes())['remote_directory']
        obj=json.loads(run('native-preflight',command(remote),240))
        assert obj['PREFLIGHT']=='PASS' and obj['TOKEN_ISSUED'] is False and obj['source_sha']==MERGE
        print('NATIVE_PREFLIGHT_PASS_TOKEN_NOT_ISSUED')
    elif mode=='execute':
        instant=dt.datetime.now(KST)
        assert dt.datetime(2026,10,14,21,50,tzinfo=KST)<=instant<dt.datetime(2026,10,14,22,0,tzinfo=KST)
        authority=json.loads((OUT/'EXECUTION_AUTHORITY.json').read_bytes())
        assert authority['maximum_token_request_commands']==1 and authority['source_sha']==MERGE
        assert authority['runtime']=='GO' and authority['fresh_prechecks']=='PASS'
        assert (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(authority['checked_at_utc'])).total_seconds()<120
        assert json.loads((OUT/'native-preflight.stdout').read_bytes())['TOKEN_ISSUED'] is False
        remote=json.loads((OUT/'PUBLIC_STAGING.json').read_bytes())['remote_directory']
        with (OUT/'EXECUTE_INTENT.json').open('x',encoding='utf-8') as stream:
            json.dump({'at_utc':now(),'source_sha':MERGE,'maximum_token_request_commands':1,
                       'consumed_on_ambiguous_result':True},stream)
        obj=json.loads(run('native-execute',command(remote,True),360))
        assert obj['NATIVE_AUTH_PROBE']=='PASS' and obj['TOKEN_ISSUED'] is True
        print(json.dumps({'NATIVE_AUTH_PROBE':obj['NATIVE_AUTH_PROBE'],
             'permission_count':len(obj['runner_observation']['permissions']),
             'authenticated_deployments':len(obj['runner_observation']['deployments']),
             'expires_at':obj['cp1_credential']['expires_at']}))
    else:
        raise SystemExit('Unknown mode')

if __name__=='__main__':
    main()
