"""One-shot read-only inventory; never run udev test/trigger/reload or install files."""
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

SHARE = Path('/mnt/hbr-ssh-naming')
EXPECTED_FP = 'SHA256:wcqHnqpzbcZfyZ3PhLWYFOuKDURNqQRvU75Nu5ICuvk'
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_UID')
    uuid = Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()
    require(uuid in ('564d9e38-f024-efe2-b68f-137a5047788a',
                    '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'PHYSICAL_NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-ssh-naming-local-'), 'LOCAL_PATH')
    require(time.time() < int((local / 'expires-epoch.txt').read_text()), 'EXPIRED')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE')
    require(not (SHARE / 'NAMING_PRECHECK').exists(), 'RECEIPT_EXISTS')
    os.umask(0o077)
    work = Path(tempfile.mkdtemp(prefix='hbr-ssh-naming-', dir='/root'))
    summary = {'scope': 'READ_ONLY_NAMING_PREREQUISITES_NOT_PARSER_OR_HOTPLUG',
               'started_epoch': time.time(), 'private': str(work), 'uuid': uuid,
               'collector_sha256': sha(Path(__file__).read_bytes()),
               'source_head_under_review': '918603f7187bff211cd80347a1f030babf26dc10',
               'system_mutations': 'NONE', 'commands': [], 'issues': [], 'files': [],
               'install': 'NOT_RUN', 'hotplug': 'NOT_RUN'}

    def query(name, argv):
        try:
            result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                                    cwd=work, env=ENV, timeout=15, check=False)
            rc, out, err = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            rc, out, err = 124, exc.stdout or b'', exc.stderr or b''
        except OSError as exc:
            rc, out, err = 127, b'', type(exc).__name__.encode()
        (work / (name + '.stdout')).write_bytes(out)
        (work / (name + '.stderr')).write_bytes(err)
        summary['commands'].append({'name': name, 'argv': argv, 'rc': rc,
            'stdout_sha256': sha(out), 'stdout_bytes': len(out),
            'stderr_sha256': sha(err), 'stderr_bytes': len(err)})
        if rc:
            summary['issues'].append('QUERY_NONZERO:' + name)
        return rc, out

    for name, argv in [('udev-version', ['/usr/bin/udevadm', '--version']),
                       ('udev-active', ['/usr/bin/systemctl', 'is-active', 'systemd-udevd.service']),
                       ('selinux', ['/usr/sbin/getenforce'])]:
        rc, out = query(name, argv)
        summary[name] = out.decode(errors='replace').strip() if rc == 0 else 'UNCONFIRMED'
    if summary['udev-active'] != 'active' or summary['selinux'] != 'Enforcing':
        summary['issues'].append('SERVICE_OR_SELINUX_NOT_READY')
    summary['install_state_exists'] = Path('/var/lib/hbr-ssh-control').exists()
    summary['interface_name_exists'] = (Path('/sys/class/net') / 'hbrmgmt0').exists()
    if summary['install_state_exists'] or summary['interface_name_exists']:
        summary['issues'].append('INSTALL_OR_NAME_ALREADY_EXISTS')
    roots = [Path(p) for p in ('/etc/systemd/network', '/run/systemd/network',
                              '/usr/local/lib/systemd/network', '/usr/lib/systemd/network')]
    summary['directories'] = []
    for directory in roots:
        entry = {'path': str(directory), 'exists': directory.exists(), 'symlink': directory.is_symlink()}
        if directory.exists():
            info = directory.lstat()
            entry.update(uid=info.st_uid, mode=oct(stat.S_IMODE(info.st_mode)))
        summary['directories'].append(entry)
    if not roots[0].is_dir() or roots[0].is_symlink():
        summary['issues'].append('INSTALL_PARENT_MISSING_OR_SYMLINK')
    candidates = []
    for directory in roots:
        if directory.is_dir() and not directory.is_symlink():
            candidates += list(directory.glob('*.link')) + list(directory.glob('*.link.d/*.conf'))
    for directory in (Path('/etc/udev/rules.d'), Path('/run/udev/rules.d'), Path('/usr/lib/udev/rules.d')):
        if directory.is_dir() and not directory.is_symlink():
            candidates += list(directory.glob('*.rules'))
    require(len(candidates) <= 512, 'INVENTORY_LIMIT')
    for idx, path in enumerate(sorted(set(candidates))):
        info = path.lstat()
        entry = {'path': str(path), 'uid': info.st_uid, 'mode': oct(stat.S_IMODE(info.st_mode))}
        if not stat.S_ISREG(info.st_mode) or any(p.is_symlink() for p in path.parents):
            entry['status'] = 'NONREGULAR_OR_SYMLINK_PARENT_NOT_READ'
            summary['files'].append(entry)
            continue
        require(info.st_size <= 1048576, 'SOURCE_SIZE_LIMIT')
        raw = path.read_bytes()
        (work / ('source-%03d.txt' % idx)).write_bytes(raw)
        entry.update(status='PRIVATE_PRESERVED', bytes=len(raw), sha256=sha(raw))
        lines = raw.decode(errors='replace').splitlines()
        if path.suffix == '.link' or '.link.d' in str(path):
            entry['selected_lines'] = [line for line in lines if re.match(
                r'^\s*(\[(Match|Link)\]|(MACAddress|PermanentMACAddress|OriginalName|Driver|Type|Path|Name|NamePolicy|MACAddressPolicy|ActivationPolicy)\s*=)', line)]
            if path.name <= '10-hbr-mgmt.link':
                summary['issues'].append('EARLY_LINK_REVIEW:' + str(path))
        else:
            # Only fixed structural hints leave private storage, never arbitrary RUN/PROGRAM text.
            entry['network_name_rule_hint'] = bool(re.search(r'(net_setup_link|ID_NET_NAME|NAME\s*[:+]?=)', raw.decode(errors='replace')))
        if path.name == '10-hbr-mgmt.link' or '10-hbr-mgmt.link.d' in str(path):
            summary['issues'].append('NAMING_CONFIG_COLLISION:' + str(path))
        summary['files'].append(entry)
    hostkey = Path('/etc/ssh/ssh_host_ed25519_key.pub')
    require(hostkey.is_file() and not hostkey.is_symlink(), 'HOST_PUBLIC_KEY_MISSING')
    public = hostkey.read_bytes()
    require(len(public) < 4096 and public.strip().startswith(b'ssh-ed25519 '), 'PUBLIC_KEY_FORMAT')
    rc, out = query('host-key-fingerprint', ['/usr/bin/ssh-keygen', '-lf', str(hostkey), '-E', 'sha256'])
    matches = rc == 0 and EXPECTED_FP in out.decode(errors='replace').split()
    summary['host_key_matches_previous_receipt'] = matches
    summary['host_key_fingerprint_expected'] = EXPECTED_FP
    if not matches:
        summary['issues'].append('HOST_KEY_DRIFT_OR_UNCONFIRMED')
    summary['finished_epoch'] = time.time()
    summary['verdict'] = 'REVIEW_REQUIRED_NOT_INSTALL_GO'
    result = (json.dumps(summary, indent=2) + '\n').encode()
    (work / 'SUMMARY.json').write_bytes(result)
    destination = SHARE / 'NAMING_PRECHECK'
    destination.mkdir()
    exports = {'SUMMARY.json': result}
    if matches:
        exports['ssh_host_ed25519_key.pub'] = public
    for name, raw in exports.items():
        (destination / name).write_bytes(raw)
    manifest = ''.join(sha(raw) + '  ' + name + '\n' for name, raw in sorted(exports.items())).encode()
    (destination / 'SHA256SUMS').write_bytes(manifest)
    print('SSH_NAMING_PRECHECK_EXPORTED REVIEW_REQUIRED ISSUES=' + str(len(summary['issues'])))
    print('No install, reload, trigger, NIC, account, service or Docker changes performed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        reason = str(exc)
        print('SSH_NAMING_PRECHECK_STOP ' + (reason if re.fullmatch('[A-Z_]+', reason) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
