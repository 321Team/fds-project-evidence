#!/usr/bin/env python3
"""PR4 follow-up: read-only remote SFTP probe; local evidence export only."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import shlex
import signal
import stat
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone

APPROVED = '3a02dc8934adb1f80df48ec6763689c401a1e8d6'
SOURCE_HASHES = {'.gitattributes': '9de428650885b9dc5d77a706ebff4a8544e2f3e83b8f78c75c43107b9a7e119c', '.gitignore': 'dddfe1147ac2e358915a4c2bc9cd95f213e959631280abc81543d87a842ad729', 'README.md': '9403f76b2063fb9daaaaed98da62ed001c6f9e94424e9030b2b9a55cc08002e9', 'ansible.cfg': '4e0ef45e734ca1c84fea10628cb93dee50acf13133de01e1f8c69eccdbad379c', 'docs/change/CR-P1-ANS-01-01.md': '1aff2db9690b0ac9e9fdc6668ce22209d29dd583cfcef59923461addfba0918c', 'docs/runbooks/CR-P1-ANS-01-01.md': '536bd5a664cd3ed3f6d9e2f6e4f9de5c9db7f8c0739bacf20bbafcea7443ab7c', 'docs/runbooks/SSH-Key-Guard-Verification.md': '69a00c4b3c50dfd1c94b0cfd702ff8de005f1a7e86223c53b262a8aa0296ec61', 'inventory/group_vars/all.yml': '6aa1c898197769baf68a9f793a2cdb68ea7052e677ab7c5c451e83dcee686902', 'inventory/hosts.yml': 'd73a8b2826e1ee51a1f0493e7ffd237b605502da04fa2e4f58c60f2627f63bf0', 'playbooks/cr-p1-ans-01-01-apply-control-plane.yml': '34dbdd59f7e923a5194bc061ba3791affcfc7fabbde3033e788bbb2d42048103', 'playbooks/cr-p1-ans-01-01-apply-workers.yml': '8969a68ccf972f5e168ff9f46b64a0efa8e30ae409c80451f94bb10f1b82037b', 'playbooks/cr-p1-ans-01-01-precheck.yml': 'b093ff2973cf2c0be5f12af349a98ae2a2cecfac1f49cb7cd1a20382aa123799', 'playbooks/cr-p1-ans-01-01-rollback.yml': '13f6bfbf816132a8852e986649f7b535935a9bdd0df157dfbe42cbfa1f297128', 'playbooks/cr-p1-ans-01-01-verify.yml': '2ef70483db0ab222576e6da6f072283df8ed44ca4f176c823f117ade1d6baa69', 'playbooks/harden_svc_ansible_key.yml': 'aa3f94e94a5901bb55b26ac8342f1077776f8ee482e72e6fc659a65105c62e79', 'playbooks/p1-lb-01-stage-a-nodes.yml': '92b1893cd9a773aeb9b822269f09763e71a196c34f99accdc596377755fc3946', 'playbooks/precheck.yml': 'e3c31bc3b0a3f481852bd6ee27ec5e4e81d07d98c14a7974d756c68653ccf0ff', 'playbooks/site.yml': '1f9053b6a654988132ede57003b66a646a3ef34b48cb079aaf914e9a055c1234', 'roles/common/tasks/main.yml': '020e2e9e7b4db316cccbeb6a03b4482136ce9347f43cdd05294bb52f995459b4', 'roles/dns_resolver/tasks/main.yml': '3b7fa1ae042421c2d0b9352e794cf9e83dcaf5843aa01e69b8a354544daeb4a7', 'roles/dns_resolver/tasks/verify.yml': 'f526c67069d6f21dff2c1533bfe950eb22cb60c8832f020a0482a3319b3090e9', 'roles/k8s_prereq/handlers/main.yml': '7b95d285122ff3f0d23b7daef840a45dd8fa70d8c231e11ba360bf2ace48c4ff', 'roles/k8s_prereq/tasks/main.yml': 'b6c7e084f00231593a9bedc7310099430b015fd20b444ae9bfe706fdde30420a', 'scripts/cr-p1-ans-01-01-run.sh': '62bdfe8dfa3785952da91d97554616f73eee314d56537efd951689a0776846b2', 'scripts/verify-ssh-main.py': '36837825cbed578e091d3d6946028c427d1cbebc17abfe8b0a428efbfd908cdb', 'tests/ssh-server-readonly.yml': '7cd568368effc695a4bb98837cfe6b18ebd579eeddff231a903a12bd37a7bf51', 'tests/test-dns-resolver-normalization.yml': 'df0b649f605e5038d71041034eccf1307027dda058e8f38c582647a679d8276c', 'tests/test-ssh-key-guards.py': 'eeccc5198c33a3111f8411037dcad2adeeb8e1cd666a65ad5d27c56769881729'}
NODES = {'k8s-worker01': '10.1.93.105', 'k8s-worker02': '10.1.93.107',
         'k8s-worker03': '10.1.93.108', 'k8s-control01': '10.1.93.102',
         'k8s-control02': '10.1.93.103', 'k8s-control03': '10.1.93.104'}
REMOTE = r'''
import hashlib,json,os,pwd,stat,subprocess,sys
from pathlib import Path
host,ip,connection=sys.argv[1:]
observed=subprocess.check_output(['/usr/bin/hostnamectl','--static'],text=True).strip()
parts=connection.split()
if observed!=host or pwd.getpwuid(os.geteuid()).pw_name!='svc_ansible' or len(parts)!=4 or parts[0]!='10.250.10.10' or parts[2]!=ip:
    raise RuntimeError('hostname/user/source/destination guard failed')
p=Path('/home/svc_ansible/.ssh/authorized_keys')
if p.is_symlink() or p.parent.is_symlink() or not stat.S_ISREG(p.lstat().st_mode):
    raise RuntimeError('managed key path is not a regular file')
st=p.stat()
key={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'uid':st.st_uid,'gid':st.st_gid,'mode':stat.S_IMODE(st.st_mode),'mtime_ns':st.st_mtime_ns}
commands=[]
context='user=svc_ansible,addr='+parts[0]+',laddr='+ip+',lport='+parts[3]
for cmd in [['/usr/bin/rpm','-q','openssh-server','openssh-clients'],['/usr/bin/sudo','-n','/usr/sbin/sshd','-T','-C',context]]:
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
        lines=r.stdout.splitlines()
        if '-T' in cmd:
            names={'subsystem','forcecommand','chrootdirectory','passwordauthentication','kbdinteractiveauthentication','pubkeyauthentication','permittty','disableforwarding'}
            lines=[x for x in lines if x.split() and x.split()[0] in names]
        commands.append({'command':cmd,'rc':r.returncode,'stdout':'\n'.join(lines),'stderr':r.stderr[:4000]})
    except (OSError,subprocess.TimeoutExpired) as e:
        commands.append({'command':cmd,'rc':None,'error':type(e).__name__})
print(json.dumps({'hostname':observed,'source':parts[0],'destination':parts[2],'key_state':key,'os_release_sha256':hashlib.sha256(Path('/etc/os-release').read_bytes()).hexdigest(),'commands':commands,'sshd_context_limit':'Default sshd config; observed address/user context. Match Host and custom daemon -f overrides require separate confirmation.'}))
'''

def scrub(text):
    return re.sub(r'(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)', '[REDACTED_TOKEN]', text)

def run(cmd, cwd=None, env=None, data=None, timeout=30):
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(data, timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            rc = 124
            stderr += '\nCOLLECTOR_TIMEOUT\n'
        return {'rc': rc, 'stdout': scrub(stdout), 'stderr': scrub(stderr)}
    except OSError as exc:
        return {'rc': 127, 'stdout': '', 'stderr': scrub(str(exc))}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_repo(repo):
    git_env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    for args, want in [(['rev-parse', '--show-toplevel'], str(repo)),
                       (['symbolic-ref', '--short', 'HEAD'], 'main'),
                       (['rev-parse', 'HEAD'], APPROVED)]:
        r = run(['/usr/bin/git', '-C', str(repo)] + args, env=git_env)
        if r['rc'] != 0 or r['stdout'].strip() != want:
            raise RuntimeError('operational repository identity/branch/HEAD differs; no fetch or reset performed')
    for name, expected in SOURCE_HASHES.items():
        path = repo / name
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise RuntimeError('approved source mismatch: ' + name)

def options(home, ip):
    return ['-i', str(home / '.ssh/p1_ansible_ed25519'), '-o', 'Hostname=' + ip,
            '-o', 'BatchMode=yes', '-o', 'PreferredAuthentications=publickey',
            '-o', 'PasswordAuthentication=no', '-o', 'KbdInteractiveAuthentication=no',
            '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(home / '.ssh/known_hosts'),
            '-o', 'IdentitiesOnly=yes', '-o', 'IdentityAgent=none',
            '-o', 'ControlMaster=no', '-o', 'ControlPersist=no', '-o', 'ControlPath=none',
            '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=1',
            '-o', 'UpdateHostKeys=no', '-o', 'PermitLocalCommand=no']

def remote_snapshot(home, host, ip):
    command = '/usr/bin/python3 -c ' + shlex.quote(REMOTE) + ' ' + shlex.quote(host) + ' ' + shlex.quote(ip) + ' "$SSH_CONNECTION"'
    result = run(['/usr/bin/ssh', '-T'] + options(home, ip) + ['svc_ansible@' + ip, command])
    if result['rc'] == 0:
        try:
            result['parsed'] = json.loads(result['stdout'])
        except json.JSONDecodeError:
            result['rc'] = 65
            result['stderr'] += '\nUnexpected remote stdout; snapshot not accepted.'
    return result

def classify(before, transfer, after, downloaded):
    if before.get('rc') != 0 or after.get('rc') != 0:
        return 'SSH_OR_CONTEXT_CHECK_FAILED'
    b, a = before.get('parsed', {}), after.get('parsed', {})
    if not all(k in b and k in a for k in ['key_state', 'hostname', 'source', 'destination', 'os_release_sha256']):
        return 'INCOMPLETE_SNAPSHOT'
    if any(b[k] != a[k] for k in ['key_state', 'hostname', 'source', 'destination', 'os_release_sha256']):
        return 'REMOTE_STATE_CHANGED_REVIEW_REQUIRED'
    if transfer.get('rc') != 0:
        return 'SFTP_READ_TRANSFER_FAILED'
    if not downloaded.is_file() or downloaded.is_symlink() or digest(downloaded) != b['os_release_sha256']:
        return 'SFTP_CONTENT_MISMATCH'
    return 'SFTP_READ_TRANSFER_PASS'

def batch_get(path):
    text = str(path)
    if '\n' in text or '\r' in text:
        raise RuntimeError('unsupported local path')
    quoted = text.replace('\\', '\\\\').replace('"', '\\"')
    return 'get /etc/os-release "' + quoted + '"\nbye\n'

def export(out, report):
    (out / 'SFTP_REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    files = sorted(x for x in out.iterdir() if x.is_file())
    (out / 'SHA256SUMS').write_text(''.join(digest(x) + '  ' + x.name + '\n' for x in files))
    archive = out / 'FDS_SFTP_Followup_Result.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for file in files + [out / 'SHA256SUMS']:
            tar.add(file, arcname='results/' + file.name, recursive=False)
    sidecar = out / (archive.name + '.sha256')
    sidecar.write_text(digest(archive) + '  ' + archive.name + '\n')
    print('STATUS=' + report['status'])
    print('ARCHIVE=' + str(archive))
    print('SIDECAR=' + str(sidecar))

def main():
    os.umask(0o077)
    home = Path.home()
    if os.geteuid() == 0 or pwd.getpwuid(os.geteuid()).pw_name != 'server01_ansible':
        raise RuntimeError('run as server01_ansible, without sudo')
    r = run(['/usr/bin/hostnamectl', '--static'])
    if r['rc'] != 0 or r['stdout'].strip() != 'ansible01':
        raise RuntimeError('run on ansible01')
    for file in [home / '.ssh/p1_ansible_ed25519', home / '.ssh/known_hosts']:
        if not file.is_file() or file.is_symlink():
            raise RuntimeError('required existing SSH input missing or symlink: ' + str(file))
    repo = home / 'p1-ans-01'
    verify_repo(repo)
    key_meta = [(str(x), digest(x), x.stat().st_mtime_ns, stat.S_IMODE(x.stat().st_mode))
                for x in [home / '.ssh/known_hosts']]
    out = Path(tempfile.mkdtemp(prefix='FDS_SFTP_Followup.', dir=home))
    report = {'schema_version': 1, 'status': 'DIAGNOSTICS_COMPLETE_REVIEW_REQUIRED',
              'started_at': datetime.now(timezone.utc).isoformat(), 'code_commit': APPROVED,
              'scope': 'REMOTE_READ_ONLY_SFTP_GET_OS_RELEASE; no put/config/apply/service/engine change',
              'original_warning_replay': False, 'successful_original_fallback': 'NOT_DETERMINED',
              'bootstrap': 'HOLD', 'nodes': [], 'commands': {}}
    env = os.environ.copy()
    env['ANSIBLE_CONFIG'] = str(repo / 'ansible.cfg')
    try:
        for name, cmd in [('engine', ['/usr/bin/ansible', '--version']),
                          ('packages', ['/usr/bin/rpm', '-q', '--qf', '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\nVendor=%{VENDOR}\n', 'ansible-core', 'python3', 'openssh-clients']),
                          ('ssh_version', ['/usr/bin/ssh', '-V'])]:
            value = run(cmd, cwd=repo, env=env)
            report['commands'][name] = value
        config = run(['/usr/bin/ansible-config', 'dump', '--only-changed', '-t', 'connection'], cwd=repo, env=env)
        allowed = ['transfer_method', 'pipelining', 'sftp_batch_mode', 'sftp_executable', 'scp_executable', 'ssh_executable', 'scp_if_ssh']
        config['stdout'] = '\n'.join(x for x in config['stdout'].splitlines() if any(k in x.lower() for k in allowed))
        report['selected_connection_config'] = config
        names = ['ANSIBLE_SSH_TRANSFER_METHOD', 'ANSIBLE_SFTP_EXECUTABLE', 'ANSIBLE_SCP_EXECUTABLE', 'ANSIBLE_SSH_EXECUTABLE', 'ANSIBLE_PIPELINING', 'ANSIBLE_SFTP_BATCH_MODE', 'ANSIBLE_SCP_IF_SSH']
        report['selected_environment'] = {k: scrub(os.environ[k]) for k in names if k in os.environ}
        report['controller_sftp_executable'] = {'path': '/usr/bin/sftp', 'exists': Path('/usr/bin/sftp').is_file()}
        for host, ip in NODES.items():
            before = remote_snapshot(home, host, ip)
            (out / (host + '_before.json')).write_text(json.dumps(before, indent=2) + '\n')
            if before['rc'] != 0:
                report['nodes'].append({'host': host, 'status': 'SSH_OR_CONTEXT_CHECK_FAILED', 'probe_run': False})
                print(host + '=SSH_OR_CONTEXT_CHECK_FAILED')
                continue
            target = out / (host + '_os-release.txt')
            transfer = run(['/usr/bin/sftp', '-vv', '-b', '-'] + options(home, ip) + ['svc_ansible@' + ip], data=batch_get(target))
            (out / (host + '_sftp.json')).write_text(json.dumps(transfer, indent=2) + '\n')
            after = remote_snapshot(home, host, ip)
            (out / (host + '_after.json')).write_text(json.dumps(after, indent=2) + '\n')
            verdict = classify(before, transfer, after, target)
            report['nodes'].append({'host': host, 'ip': ip, 'status': verdict, 'probe_run': True,
                                    'sftp_rc': transfer['rc'], 'download_sha256': digest(target) if target.is_file() else None})
            print(host + '=' + verdict)
        verify_repo(repo)
        if any(not Path(path).is_file() or digest(Path(path)) != sha or Path(path).stat().st_mtime_ns != mtime or stat.S_IMODE(Path(path).stat().st_mode) != mode for path,sha,mtime,mode in key_meta):
            raise RuntimeError('known_hosts changed during diagnostic')
        report['source_and_known_hosts_preserved'] = True
    except Exception as exc:
        report['status'] = 'DIAGNOSTICS_PARTIAL_REVIEW_REQUIRED'
        report['error'] = scrub(str(exc))
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report['sftp_pass_count'] = sum(x['status'] == 'SFTP_READ_TRANSFER_PASS' for x in report['nodes'])
    report['expected_nodes'] = list(NODES)
    report['all_nodes_probed'] = len(report['nodes']) == len(NODES) and all(x['probe_run'] for x in report['nodes'])
    export(out, report)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOP=' + scrub(str(exc)))
        raise SystemExit(1)
