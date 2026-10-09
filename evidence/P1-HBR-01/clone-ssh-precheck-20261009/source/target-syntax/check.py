"""One-shot READ ONLY target parser check. Writes only private work and receipt.
No install/reload, no account, no NIC or Docker command. Fixtures are not deployment inputs.
"""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import tempfile
import time

SHARE = Path('/mnt/hbr-ssh-syntax')
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
SOURCE_HEAD = '69cfb6a684c061dbb78d37f507781a1188a3d3c8'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def shadow_ssh(main, destination):
    pattern = re.compile(r'(?im)^([ \t]*Include[ \t]+)(["\']?)/etc/ssh/sshd_config\.d/\*\.conf\2[ \t]*(?:#.*)?$')
    require(len(pattern.findall(main)) == 1, 'SSH_INCLUDE_LAYOUT_UNSUPPORTED')
    return pattern.sub(lambda m: m[1] + str(destination / '*.conf'), main)


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_UID')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-ssh-syntax-local-'), 'LOCAL_PATH')
    require(time.time() < int((local / 'expires-epoch.txt').read_text()), 'EXPIRED')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE')
    os.umask(0o077)
    private = Path(tempfile.mkdtemp(prefix='hbr-ssh-target-syntax-', dir='/root'))
    summary = {'scope': 'READ_ONLY_TARGET_PARSERS', 'runtime': 'NOT_RUN', 'mutations': 'NONE',
               'source_head': SOURCE_HEAD, 'started_epoch': time.time(), 'private': str(private),
               'collector_sha256': digest(Path(__file__).read_bytes()), 'commands': [],
               'fixtures': 'ens160 / synthetic MAC and public-key bytes; NOT allocated or deployable',
               'issues': []}
    renderer = local / 'render-clone-ssh-plan.py'
    summary['renderer_sha256'] = digest(renderer.read_bytes())
    spec = importlib.util.spec_from_file_location('renderer', renderer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wire = struct.pack('>I', 11) + b'ssh-ed25519' + struct.pack('>I', 32) + bytes(range(32))
    fixtures = module.render('ens160', '00:50:56:30:00:02',
                             'ssh-ed25519 ' + base64.b64encode(wire).decode(), int(time.time()) + 3600)
    def query(name, argv):
        out, err = private / (name + '.stdout'), private / (name + '.stderr')
        with out.open('xb') as stdout, err.open('xb') as stderr:
            try:
                rc = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    env=ENV, timeout=20, cwd=private).returncode
            except subprocess.TimeoutExpired:
                rc = 124
            except OSError:
                rc = 127
        raw, errors = out.read_bytes(), err.read_bytes()
        hints = [word for word in ['not allowed within a Match block', 'Bad configuration option',
                 'Permission denied', 'syntax error', 'No such file', 'unknown option']
                 if word.lower() in errors.decode(errors='replace').lower()]
        summary['commands'].append({'name': name, 'argv': argv, 'rc': rc,
              'stdout_bytes': len(raw), 'stdout_sha256': digest(raw),
              'stderr_bytes': len(errors), 'stderr_sha256': digest(errors), 'fixed_error_hints': hints})
        return rc, raw
    query('sshd-baseline', ['/usr/sbin/sshd', '-t'])
    ssh_dir = private / 'sshd_config.d'
    ssh_dir.mkdir()
    for path in Path('/etc/ssh/sshd_config.d').glob('*.conf'):
        require(not path.is_symlink() and path.is_file(), 'SSH_CONFIG_SYMLINK')
        (ssh_dir / path.name).write_bytes(path.read_bytes())
    require(not (ssh_dir / '00-hbr-mgmt-sshd.conf').exists(), 'SSH_CANDIDATE_ALREADY_INSTALLED')
    (ssh_dir / '00-hbr-mgmt-sshd.conf').write_text(fixtures['00-hbr-mgmt-sshd.conf.candidate'])
    try:
        shadow = shadow_ssh(Path('/etc/ssh/sshd_config').read_text(), ssh_dir)
        config = private / 'sshd_config'
        config.write_text(shadow)
        query('sshd-combined', ['/usr/sbin/sshd', '-t', '-f', str(config)])
        selected = {}
        for i, (user, peer) in enumerate([('hbrctl', '192.168.253.1'), ('server08', '192.168.253.1'),
                                         ('root', '192.168.253.1'), ('hbrctl', '192.168.253.3')]):
            context = f'user={user},host=harbor01,addr={peer},laddr=192.168.253.2,lport=22'
            rc, raw = query('sshd-context-' + str(i), ['/usr/sbin/sshd', '-T', '-f', str(config), '-C', context])
            allowed = {'allowusers', 'usepam', 'passwordauthentication', 'authenticationmethods',
                       'disableforwarding', 'forcecommand', 'permitrootlogin', 'trustedusercakeys'}
            selected[str(i)] = {'context': context, 'rc': rc, 'values': [line for line in raw.decode(errors='replace').splitlines()
                               if line.split(' ', 1)[0] in allowed]}
        summary['ssh_selected'] = selected
    except ValueError as error:
        summary['issues'].append(str(error))
    nft = private / 'guard.nft'
    nft.write_text(fixtures['hbr-mgmt.nft.candidate'])
    query('nft-candidate-check', ['/usr/sbin/nft', '--check', '--file', str(nft)])
    firewall = private / 'firewalld'
    (firewall / 'zones').mkdir(parents=True)
    (firewall / 'zones/hbr-mgmt.xml').write_text(fixtures['hbr-mgmt.xml.candidate'])
    query('firewalld-candidate-check', ['/usr/bin/firewall-offline-cmd', '--system-config=' + str(firewall), '--check-config'])
    # Query supported flags before building a shadow NM config; never start/reload NM.
    rc, help_raw = query('nm-help', ['/usr/sbin/NetworkManager', '--help'])
    if rc == 0 and b'--config-dir' in help_raw and b'--print-config' in help_raw:
        nm_dir = private / 'nm-conf.d'
        nm_dir.mkdir()
        for path in Path('/etc/NetworkManager/conf.d').glob('*.conf'):
            require(not path.is_symlink() and path.is_file(), 'NM_CONFIG_SYMLINK')
            (nm_dir / path.name).write_bytes(path.read_bytes())
        require(not (nm_dir / '90-hbr-no-auto-default.conf').exists(), 'NM_CANDIDATE_ALREADY_INSTALLED')
        (nm_dir / '90-hbr-no-auto-default.conf').write_text(fixtures['90-hbr-no-auto-default.conf.candidate'])
        rc, raw = query('nm-candidate-print', ['/usr/sbin/NetworkManager', '--print-config',
                   '--config=/etc/NetworkManager/NetworkManager.conf', '--config-dir=' + str(nm_dir)])
        summary['nm_selected'] = [line for line in raw.decode(errors='replace').splitlines()
                                 if line.startswith(('no-auto-default=', 'match-device=', 'managed=', '[device-hbr-mgmt]'))]
    else:
        summary['issues'].append('NM_SHADOW_OPTIONS_UNCONFIRMED')
    summary['finished_epoch'] = time.time()
    summary['nonzero'] = [{'name': c['name'], 'rc': c['rc']} for c in summary['commands'] if c['rc']]
    summary['verdict'] = 'REVIEW_REQUIRED_NOT_INSTALL_GO'
    raw = (json.dumps(summary, indent=2) + '\n').encode()
    (private / 'SUMMARY.json').write_bytes(raw)
    destination = SHARE / 'TARGET_SYNTAX'
    destination.mkdir(exist_ok=False)
    (destination / 'SUMMARY.json').write_bytes(raw)
    manifest = (digest(raw) + '  SUMMARY.json\n').encode()
    (destination / 'SHA256SUMS').write_bytes(manifest)
    with (SHARE / 'EXPORT_DONE').open('x') as out:
        out.write(digest(manifest) + '\n')
    print('TARGET_SYNTAX_EXPORTED REVIEW_REQUIRED NONZERO=' + str(len(summary['nonzero'])) +
          ' ISSUES=' + str(len(summary['issues'])))
    print('No install, reload, service, account, NIC or Docker changes performed.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('TARGET_SYNTAX_STOP; preserve private output. No automatic retry or apply.')
        raise SystemExit(2)
