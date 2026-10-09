"""Read-only current-boot preservation; no restart, reload, install or NIC action."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import tempfile
import time

SHARE = Path('/mnt/hbr-ssh-bootcheck')
A3 = Path('/root/hbr-a3-joz3x6ya/result.json')
A3_SHA = '5df896fd9f501cbac82e1091c6368160d79dbca34baf651681f766f331102fa7'
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_safe(path):
    for parent in path.parents:
        info = parent.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                and not info.st_mode & 0o022, 'UNTRUSTED_PARENT')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0
                and info.st_size < 8 * 1024 * 1024, 'UNTRUSTED_FILE')
        return stream.read()


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_UID')
    uuid = Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()
    require(uuid in ('564d9e38-f024-efe2-b68f-137a5047788a',
                    '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-ssh-bootcheck-local-'), 'LOCAL_PATH')
    require(time.time() < int(read_safe(local / 'expires-epoch.txt')), 'HANDOFF_EXPIRED')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE')
    require(not (SHARE / 'BOOT_PRECHECK').exists(), 'RECEIPT_EXISTS')
    lock_fd = os.open('/root/hbr-a3-driver.lock', os.O_RDONLY | os.O_NOFOLLOW)
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.umask(0o077)
    work = Path(tempfile.mkdtemp(prefix='hbr-ssh-bootcheck-', dir='/root'))
    result = {'scope': 'READ_ONLY_BOOT_REVIEW_NOT_SHUTDOWN_OR_REBOOT_GO',
              'started_epoch': time.time(), 'private': str(work), 'uuid': uuid,
              'collector_sha256': sha(Path(__file__).read_bytes()),
              'commands': [], 'files': [], 'issues': [], 'system_mutations': 'NONE'}

    def preserve(path, name):
        try:
            raw = read_safe(path)
            (work / name).write_bytes(raw)
            result['files'].append({'path': str(path), 'private_copy': name,
                                    'bytes': len(raw), 'sha256': sha(raw)})
            return raw
        except (OSError, ValueError):
            result['issues'].append('FILE_UNAVAILABLE:' + str(path))
            return None

    def query(name, argv):
        began = time.time()
        try:
            proc = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                                  cwd=work, env=ENV, timeout=20, check=False)
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            rc, out, err = 124, exc.stdout or b'', exc.stderr or b''
        except OSError as exc:
            rc, out, err = 127, b'', type(exc).__name__.encode()
        (work / (name + '.stdout')).write_bytes(out)
        (work / (name + '.stderr')).write_bytes(err)
        result['commands'].append({'name': name, 'argv': argv, 'rc': rc,
            'started_epoch': began, 'finished_epoch': time.time(),
            'stdout_bytes': len(out), 'stdout_sha256': sha(out),
            'stderr_bytes': len(err), 'stderr_sha256': sha(err)})
        if rc:
            result['issues'].append('QUERY_NONZERO:' + name)
        return rc, out

    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    result['boot_id'] = boot
    a3raw = preserve(A3, 'original-a3-result.json')
    original = None
    if a3raw is not None and sha(a3raw) == A3_SHA:
        original = json.loads(a3raw)
        result['a3_original_hash_match'] = True
        result['same_boot_as_a3'] = boot == original['boot_before']
        if not result['same_boot_as_a3']:
            result['issues'].append('BOOT_CHANGED_SINCE_A3')
    else:
        result['issues'].append('A3_ORIGINAL_UNCONFIRMED')
    preserve(Path('/root/hbr-a3-docker-restart.claim'), 'a3-claim.private')
    raw = preserve(Path('/var/lib/hbr-ssh-control/state.json'), 'install-state.private.json')
    if raw is not None:
        state = json.loads(raw)
        result['installation'] = {k: state.get(k) for k in ('status', 'started_epoch', 'source_sha256')}
        result['plan'] = {k: state.get('plan', {}).get(k) for k in ('interface', 'mac', 'expires_epoch')}
        result['install_command_rcs'] = [r.get('rc') for r in state.get('commands', [])]
        if state.get('status') != 'INSTALLED_LINK_DISABLED':
            result['issues'].append('INSTALL_STATUS_CHANGED')
        allowed = {'/etc/NetworkManager/conf.d/90-hbr-no-auto-default.conf',
            '/etc/systemd/network/10-hbr-mgmt.link', '/etc/firewalld/zones/hbr-mgmt.xml',
            '/var/lib/hbr-ssh-control/hbr-mgmt.nft', '/etc/ssh/sshd_config.d/00-hbr-mgmt-sshd.conf',
            '/etc/ssh/hbr-mgmt-authorized_keys', '/etc/ssh/hbr-ssh-policy.json',
            '/usr/local/libexec/hbr-ssh-lifecycle.py', '/usr/local/libexec/hbr-ssh-readonly.py',
            '/etc/systemd/system/hbr-ssh-session.service', '/etc/systemd/system/hbr-ssh-expire.service',
            '/etc/systemd/system/hbr-ssh-expire.timer'}
        files = state.get('files', {})
        require(isinstance(files, dict) and len(files) <= 32, 'FILE_SET')
        result['installed_files_match'] = set(files) == allowed
        for idx, (name, digest) in enumerate(sorted(files.items())):
            if name not in allowed:
                result['issues'].append('UNEXPECTED_INSTALL_FILE')
                result['installed_files_match'] = False
                continue
            content = preserve(Path(name), 'installed-%02d.private' % idx)
            if content is None or sha(content) != digest:
                result['installed_files_match'] = False
                result['issues'].append('INSTALLED_FILE_DRIFT:' + name)
        result['session_claim_exists'] = Path('/var/lib/hbr-ssh-control/session.claim').exists()
    units = ('docker.service', 'docker.socket', 'containerd.service', 'firewalld.service',
             'NetworkManager.service', 'sshd.service', 'nftables.service',
             'hbr-ssh-session.service', 'hbr-ssh-expire.service', 'hbr-ssh-expire.timer')
    properties = ('Id', 'LoadState', 'ActiveState', 'SubState', 'UnitFileState', 'FragmentPath',
                  'DropInPaths', 'After', 'Before', 'Wants', 'Requires', 'Triggers', 'TriggeredBy')
    result['units'] = {}
    for unit in units:
        rc, out = query('unit-' + unit, ['/usr/bin/systemctl', 'show', unit,
                       '--property=' + ','.join(properties), '--no-pager'])
        if rc == 0:
            result['units'][unit] = dict(line.split('=', 1) for line in
                out.decode(errors='replace').splitlines() if '=' in line)
        query('unit-content-' + unit, ['/usr/bin/systemctl', 'cat', '--no-pager', unit])
    rc, out = query('unit-files', ['/usr/bin/systemctl', 'list-unit-files', '--no-pager', '--no-legend'])
    if rc == 0:
        result['boot_unit_candidates'] = [line for line in out.decode(errors='replace').splitlines()
            if re.search(r'(harbor|hbr|docker|containerd)', line, re.I)]
    for name, argv in (
        ('selinux', ['/usr/sbin/getenforce']),
        ('addresses', ['/usr/sbin/ip', '-j', 'address', 'show']),
        ('routes4', ['/usr/sbin/ip', '-j', '-4', 'route', 'show', 'table', 'all']),
        ('routes6', ['/usr/sbin/ip', '-j', '-6', 'route', 'show', 'table', 'all']),
        ('nft-tables', ['/usr/sbin/nft', 'list', 'tables']),
        ('ssh-nft', ['/usr/sbin/nft', '-j', 'list', 'table', 'inet', 'hbr_ssh_guard']),
        ('nm-devices', ['/usr/bin/nmcli', '-t', '-f', 'DEVICE,TYPE,STATE', 'device']),
        ('listeners', ['/usr/sbin/ss', '-lnt']),
        ('ssh-journal', ['/usr/bin/journalctl', '--no-pager', '-b', '0', '-n', '150',
            '-u', 'hbr-ssh-session.service', '-u', 'hbr-ssh-expire.service', '-o', 'json'])):
        rc, out = query(name, argv)
        if name == 'selinux':
            result['selinux'] = out.decode(errors='replace').strip()
        if rc == 0 and name in ('addresses', 'routes4', 'routes6'):
            result[name] = json.loads(out)
    for profile in ('6b9f0643-4a4e-324d-a969-9e5393d7e0bf', '3094c330-0b11-4463-9409-29c11bca6fcb'):
        rc, out = query('autoconnect-' + profile, ['/usr/bin/nmcli', '-g',
                       'connection.autoconnect', 'connection', 'show', profile])
        result.setdefault('autoconnect', {})[profile] = out.decode(errors='replace').strip() if rc == 0 else 'UNCONFIRMED'
    if original is not None:
        ids = sorted(r['id'] for r in original['after'].values())
        require(len(ids) == 10 and all(re.fullmatch('[a-f0-9]{64}', cid) for cid in ids), 'A3_ID_SET')
        # No full inspect: environment, credentials and mounts are not requested.
        fmt = '{"id":{{json .Id}},"state":{{json .State}},"restart":{{json .HostConfig.RestartPolicy}}}'
        rc, out = query('fixed-container-state', ['docker', 'inspect', '--format', fmt, *ids])
        if rc == 0:
            rows = [json.loads(line) for line in out.splitlines()]
            result['containers'] = [{'id': r['id'], 'status': r['state'].get('Status'),
                'running': r['state'].get('Running'), 'exit_code': r['state'].get('ExitCode'),
                'health': r['state'].get('Health', {}).get('Status'), 'restart': r['restart'],
                'error_sha256': sha(r['state'].get('Error', '').encode())} for r in rows]
    result['boot_unchanged_during_collection'] = boot == Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    result['physical_nics_at_end'] = [p.parent.name for p in Path('/sys/class/net').glob('*/device') if p.exists()]
    if not result['boot_unchanged_during_collection'] or result['physical_nics_at_end']:
        result['issues'].append('ENVIRONMENT_CHANGED_DURING_COLLECTION')
    result['finished_epoch'] = time.time()
    result['verdict'] = 'REVIEW_REQUIRED_NOT_REBOOT_GO'
    summary = (json.dumps(result, indent=2) + '\n').encode()
    (work / 'SUMMARY.json').write_bytes(summary)
    private_manifest = ''.join(sha(p.read_bytes()) + '  ' + p.name + '\n'
        for p in sorted(work.iterdir()) if p.is_file()).encode()
    (work / 'PRIVATE_SHA256SUMS').write_bytes(private_manifest)
    dest = SHARE / 'BOOT_PRECHECK'
    dest.mkdir()
    for name, content in {'SUMMARY.json': summary, 'PRIVATE_SHA256SUMS': private_manifest}.items():
        (dest / name).write_bytes(content)
    (dest / 'SHA256SUMS').write_text(''.join(sha((dest / n).read_bytes()) + '  ' + n + '\n'
        for n in ('PRIVATE_SHA256SUMS', 'SUMMARY.json')), encoding='ascii')
    print('SSH_BOOT_PRECHECK_EXPORTED REVIEW_REQUIRED ISSUES=' + str(len(result['issues'])))
    print('No shutdown, reboot, reload, NIC, account, service or Docker changes performed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        reason = str(exc)
        print('SSH_BOOT_PRECHECK_STOP ' + (reason if re.fullmatch('[A-Z_]+', reason) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
