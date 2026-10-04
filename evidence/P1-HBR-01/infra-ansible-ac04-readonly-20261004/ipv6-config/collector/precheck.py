import datetime, hashlib, json, os, pathlib, pwd, shutil, socket, stat, subprocess, sys, tarfile, tempfile

HEAD = 'badbe29440916ec3ec79da8fc81722c2e6c4e75b'
BRANCH = 'feat/p1-hbr-01-ac04-firewall-allowlist'
HOME_DIR = pathlib.Path('/home/server01_ansible')
PLAYBOOKS = ['playbooks/p1-hbr-01-ac04-forward-discover.yml', 'playbooks/p1-hbr-01-ac04-precheck.yml']

class Stop(Exception):
    pass

def require(ok, code):
    if not ok:
        raise Stop(code)

def private_file(path):
    s = path.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == os.getuid() and not s.st_mode & 0o022, 'UNSAFE_FILE')

def check_login():
    require(os.getuid() != 0 and pwd.getpwuid(os.getuid()).pw_name == 'server01_ansible', 'LOGIN_ACCOUNT')
    require(socket.gethostname().split('.')[0] == 'ansible01', 'HOST')
    require(pathlib.Path(os.environ.get('HOME', '')).resolve() == HOME_DIR and not HOME_DIR.is_symlink(), 'HOME')
    private_file(HOME_DIR / '.config/ansible/p1-ans-01.env')

def validate_pr(p):
    require(p['number'] == 63 and p['state'] == 'open' and p['head']['sha'] == HEAD
            and p['head']['ref'] == BRANCH and p['head']['repo']['full_name'] == '321Team/infra-ansible'
            and p['base']['repo']['full_name'] == '321Team/infra-ansible', 'PR_CHANGED')

def validate_inventory(p):
    require(p['hbr']['hosts'] == ['harbor01'], 'INVENTORY_TARGET')
    hosts = p['_meta']['hostvars']
    require(set(hosts) == {'harbor01'}, 'INVENTORY_EXTRA_HOST')
    h = hosts['harbor01']
    require(h['ansible_host'] == '10.1.93.54' and h['ansible_user'] == 'svc_ansible'
            and h['expected_hostname'] == 'harbor01', 'INVENTORY_IDENTITY')
    args = h.get('ansible_ssh_common_args', '')
    require('StrictHostKeyChecking=yes' in args and 'IdentitiesOnly=yes' in args
            and 'StrictHostKeyChecking=no' not in args, 'SSH_POLICY')

def main():
    check_login()
    if sys.argv[1:] == ['check-login']:
        print('LOGIN_CHECK=PASS')
        return 0
    os.umask(0o077)
    stage = pathlib.Path(tempfile.mkdtemp(prefix='hbr-ac04-ipv6-config-', dir=HOME_DIR))
    evidence = stage / 'evidence'
    evidence.mkdir()
    source = stage / 'source'
    source.mkdir()
    result = {'source_commit': HEAD, 'repository': '321Team/infra-ansible', 'host': 'ansible01',
              'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'FAIL_OR_INCOMPLETE', 'production_apply': False, 'engine_transition': False,
              'scope': 'targeted NetworkManager IPv6 method and selected persistent sysctl directives; not reboot persistence or apply approval',
              'nic_vip_client_review': 'PENDING_APPLY_TIME_RECONFIRMATION'}
    env = os.environ.copy()
    env.update(ANSIBLE_NOCOLOR='1', ANSIBLE_STDOUT_CALLBACK='default', ANSIBLE_HOST_KEY_CHECKING='True',
               ANSIBLE_RETRY_FILES_ENABLED='False', ANSIBLE_LOCAL_TEMP=str(stage / 'ansible-local'),
               ANSIBLE_CONFIG=str(source / 'ansible.cfg'))
    env.pop('ANSIBLE_LOG_PATH', None)

    def run(name, argv, cwd=source, timeout=120):
        print('STAGE=' + name, flush=True)
        (evidence / (name + '.command.json')).write_text(json.dumps(argv, indent=2) + '\n')
        with (evidence / (name + '.stdout.log')).open('wb') as out, (evidence / (name + '.stderr.log')).open('wb') as err:
            try:
                r = subprocess.run(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=timeout)
                rc = r.returncode
            except subprocess.TimeoutExpired:
                rc = 124
        (evidence / (name + '.rc')).write_text(str(rc) + '\n')
        require(rc == 0, name + '_FAILED_RC_' + str(rc))
        return (evidence / (name + '.stdout.log')).read_text(errors='replace')

    rc = 1
    try:
        for tool in ['git', 'gh', 'ansible-playbook', 'ansible-inventory']:
            require(shutil.which(tool) is not None, 'MISSING_' + tool)
        key = pathlib.Path(env.get('ANSIBLE_PRIVATE_KEY_FILE', '')).expanduser()
        require(key.is_absolute() and key.is_file(), 'PRIVATE_KEY_NOT_CONFIGURED')
        private_file(key)
        # No key or operational environment contents enter the evidence archive.
        repo = HOME_DIR / 'p1-ans-01'
        require(repo.is_dir() and not repo.is_symlink(), 'REPOSITORY_PATH')
        origin_query = subprocess.run(['git', '-C', str(repo), 'remote', 'get-url', 'origin'],
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=30)
        require(origin_query.returncode == 0, 'ORIGIN_QUERY_FAILED')
        origin = origin_query.stdout.decode().strip()
        require(origin in ['git@github.com:321Team/infra-ansible.git', 'https://github.com/321Team/infra-ansible.git',
                           'https://github.com/321Team/infra-ansible'], 'ORIGIN_MISMATCH')
        # Fetch does not switch branches or change the user's working tree.
        run('fetch', ['git', '-C', str(repo), 'fetch', 'origin', BRANCH], timeout=180)
        actual = run('fetched-head', ['git', '-C', str(repo), 'rev-parse', 'FETCH_HEAD']).strip()
        require(actual == HEAD, 'REMOTE_HEAD_CHANGED')
        # Keep a minimal PR identity record rather than the entire PR response.
        pr_raw = subprocess.run(['gh', 'api', 'repos/321Team/infra-ansible/pulls/63'],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=60)
        require(pr_raw.returncode == 0, 'PR_QUERY_FAILED')
        validate_pr(json.loads(pr_raw.stdout))
        (evidence / 'PR_IDENTITY.json').write_text(json.dumps({'pr': 63, 'head': HEAD, 'branch': BRANCH, 'state': 'open'}, indent=2)+'\n')
        archive = stage / 'source.tar'
        run('source-archive', ['git', '-C', str(repo), 'archive', '--format=tar', '--output=' + str(archive), HEAD])
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                require(not member.name.startswith('/') and '..' not in pathlib.PurePosixPath(member.name).parts
                        and (member.isfile() or member.isdir()), 'UNSAFE_SOURCE_ARCHIVE')
            t.extractall(source, filter='data')
        require((source / 'ansible.cfg').is_file(), 'ANSIBLE_CONFIG_MISSING')
        result['source_archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
        version = run('engine', ['ansible-playbook', '--version'])
        require('ansible-playbook [core 2.16.19]' in version, 'OPERATIONAL_ENGINE_MISMATCH')
        inv = json.loads(run('inventory', ['ansible-inventory', '-i', 'inventory/hbr.yml', '--list']))
        validate_inventory(inv)
        kit = pathlib.Path(__file__).resolve().parent
        extra_play = source / 'ac04-ipv6-config-supplemental.yml'
        shutil.copyfile(kit / 'supplemental.yml', extra_play)
        collector = source / 'ac04-collect-ipv6-config.py'
        shutil.copyfile(kit / 'collect_surface.py', collector)
        (evidence / 'COLLECTOR_SHA256.txt').write_text(hashlib.sha256(collector.read_bytes()).hexdigest() + '\n')
        (evidence / 'SUPPLEMENTAL_PLAYBOOK.yml').write_text(extra_play.read_text())
        run('supplemental-syntax', ['ansible-playbook', '-i', 'inventory/hbr.yml', '--syntax-check', str(extra_play), '-e', json.dumps({'ac04_collector_path': str(collector)})])
        log = run('surface', ['ansible-playbook', '-i', 'inventory/hbr.yml', '--limit', 'harbor01', str(extra_play), '-e', json.dumps({'ac04_collector_path': str(collector)})], timeout=600)
        require('IPV6_CONFIG_CAPTURED_REVIEW_REQUIRED' in log, 'SURFACE_MARKER_MISSING')
        result['status'] = 'IPV6_CONFIG_READONLY_CAPTURED_REVIEW_REQUIRED'
        result['client_population'] = 'NOT_PROVEN_BY_POINT_IN_TIME_CAPTURE'
        result['ipv6_reboot_reconnect_persistence'] = 'NOT_TESTED'
        result['change_window'] = 'NOT_CONFIRMED'
        result['apply_approval'] = 'NOT_GRANTED'
        result['previous_preapply_archive_sha256'] = '2a4908f103934e2ed06456c2b2848566a22e0de0c7bf3e38dc8ef0b199051fe2'
        rc = 0
    except (Stop, OSError, ValueError, KeyError, subprocess.TimeoutExpired, tarfile.TarError) as exc:
        result['failure'] = str(exc) if isinstance(exc, Stop) else type(exc).__name__
        print('STOP=' + result['failure'], flush=True)
    finally:
        result['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['rc'] = rc
        (evidence / 'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
        files = sorted(f for f in evidence.iterdir() if f.is_file())
        (evidence / 'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in files))
        archive = stage / 'hbr-ac04-ipv6-config-evidence.tar.gz'
        with tarfile.open(archive, 'w:gz') as t:
            t.add(evidence, arcname='evidence')
        archive.with_name(archive.name+'.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
        print('STATUS=' + result['status'])
        print('HOME_EVIDENCE=' + str(archive))
        print('IPV6_CONFIG_EXIT_CODE=' + str(rc))
    return rc

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Stop, OSError) as exc:
        print('STOP=' + (str(exc) if isinstance(exc, Stop) else type(exc).__name__))
        sys.exit(1)
