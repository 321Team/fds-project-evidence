"""Read completed CI81 receipts and archives; never issue tokens or run serve."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
M = json.loads((HERE / 'session.json').read_text(encoding='utf-8'))
SSH = ['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=8', 'fds-ansible01']
KEY = '/home/server01_ansible/.ssh/p1_ansible_ed25519'


def call(args):
    return subprocess.run(args, capture_output=True, check=True, timeout=60).stdout


def remote(command, user=None):
    if user:
        command = shlex.join(['ssh', '-T', '-i', KEY, '-o', 'BatchMode=yes',
                              '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
                              '-o', 'ConnectTimeout=8', user + '@10.250.10.20', command])
    return call(SSH + [command])


def api(path):
    return json.loads(call(['gh', 'api', 'repos/321Team/infra-ansible/' + path]))


def save(name, raw):
    p = HERE / name
    if p.exists():
        assert p.read_bytes() == raw, 'COLLECTION_CONFLICT: ' + name
    else:
        p.write_bytes(raw)


def main():
    job = api('actions/jobs/' + str(M['job']))
    assert job['head_sha'] == M['head'] and job['run_id'] == M['run']
    assert job['status'] == 'completed', 'WAIT_JOB_COMPLETION'
    runner = 'server01_cicd-runner'
    rc = remote('cat ' + shlex.quote(M['task'] + '/operator.rc'), runner)
    save('operator.rc', rc)
    for name in ['auth-ready.txt', 'operator-ended.txt', 'bundle-check.txt',
                 'input-guard-check.txt', 'input-guard-result.log', 'preflight.json', 'serve.log']:
        save(name, remote('cat ' + shlex.quote(M['task'] + '/' + name), runner))
    save('release-result.json', remote('cat ' + shlex.quote(M['admin_dir'] + '/release-result.json')))
    log = (HERE / 'serve.log').read_text(encoding='utf-8')
    paths = re.findall(r'^HOME_EVIDENCE=(/home/server01_cicd-runner/ansible-actions-evidence-[A-Za-z0-9_-]+/ansible-actions-runner-evidence\.tar\.gz)\r?$', log, re.M)
    assert len(paths) == 1, 'ARCHIVE_REFERENCE_NOT_UNIQUE'
    archive = paths[0]
    raw = remote('cat ' + shlex.quote(archive), runner)
    sidecar = remote('cat ' + shlex.quote(archive + '.sha256'), runner)
    assert hashlib.sha256(raw).hexdigest() == sidecar.decode().split()[0]
    save('ansible-actions-runner-evidence.tar.gz', raw)
    save('ansible-actions-runner-evidence.tar.gz.sha256', sidecar)
    check = '''import datetime,json,os,pathlib,stat,sys
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uid':os.getuid()}
out['packet_present']=os.path.lexists(sys.argv[1]);out['incoming_present']=os.path.lexists(sys.argv[1]+'.incoming')
out['boot']=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
print(json.dumps(out))'''
    receiver = json.loads(remote(shlex.join(['python3', '-I', '-B', '-c', check, M['packet']]), runner))
    containers = json.loads(remote('cd /tmp && sudo -n -u ansible-verify env HOME=/home/ansible-verify XDG_RUNTIME_DIR=/run/user/1001 podman ps -a --format json', 'svc_ansible'))
    process_code = '''import json,subprocess
r=subprocess.run(['sudo','-n','pgrep','-u','1001','-f','runner.py'],capture_output=True)
assert r.returncode in (0,1)
print(json.dumps({'runner_process_present':r.returncode==0}))'''
    process = json.loads(remote(shlex.join(['python3', '-I', '-B', '-c', process_code]), 'svc_ansible'))
    # Paths only: never read packet contents or token hashes.
    admin_code = '''import json,pathlib
p=pathlib.Path.home();print(json.dumps({'packet_paths_present':[str(x) for x in p.glob('ansible-runner-token-*.json*')]}))'''
    admin_packets = json.loads(remote(shlex.join(['python3', '-I', '-B', '-c', admin_code])))
    runners = api('actions/runners')
    result = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'archive_remote_path': archive, 'archive_sha256': hashlib.sha256(raw).hexdigest(),
              'operator_rc': int(rc), 'receiver': receiver, 'admin': admin_packets,
              'containers': [{k:x.get(k) for k in ('Id','Names','State')} for x in containers],
              **process, 'registered_runners': runners['total_count'],
              'job': {k: job.get(k) for k in ('id','run_id','run_attempt','head_sha','status','conclusion','runner_id','runner_name')},
              'human_identity': 'user-designated operator; personal execution report pending'}
    (HERE / 'CLEANUP_OBSERVATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
