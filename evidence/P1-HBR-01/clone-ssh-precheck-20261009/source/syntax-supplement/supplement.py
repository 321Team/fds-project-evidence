"""Read-only NM parser supplement and private firewalld warning check."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time

SHARE = Path('/mnt/hbr-ssh-supplement')
OLD = Path('/root/hbr-ssh-target-syntax-i7ref62c')
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_UID')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a',
             '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-ssh-supplement-local-'), 'LOCAL_PATH')
    require(time.time() < int((local / 'expires-epoch.txt').read_text()), 'EXPIRED')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE')
    old = json.loads((OLD / 'SUMMARY.json').read_text())
    require(old['collector_sha256'] == '9da3ada302c3172800dfc202298a2742612e36751120a9c6d1117e24142bfdcf', 'SOURCE_DRIFT')
    original_error = (OLD / 'firewalld-candidate-check.stderr').read_bytes()
    require(sha(original_error) == '920ef6367f9fade8ab0df630444f2359cfdb936b6ed5d67f072acb11be1ba73b', 'STDERR_DRIFT')
    os.umask(0o077)
    work = Path(tempfile.mkdtemp(prefix='hbr-ssh-supplement-', dir='/root'))
    summary = {'scope': 'READ_ONLY_PARSER_SUPPLEMENT', 'started_epoch': time.time(),
               'private': str(work), 'previous_private': str(OLD), 'commands': [], 'issues': [],
               'collector_sha256': sha(Path(__file__).read_bytes()), 'mutations': 'NONE',
               'runtime': 'NOT_RUN', 'original_firewalld_stderr_sha256': sha(original_error),
               'original_warning_mentions_private_firewalld_conf':
                    str(OLD / 'firewalld/firewalld.conf').encode() in original_error}
    def query(name, argv):
        out, err = work / (name + '.stdout'), work / (name + '.stderr')
        with out.open('xb') as stdout, err.open('xb') as stderr:
            try:
                rc = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    cwd=work, env=ENV, timeout=20).returncode
            except subprocess.TimeoutExpired:
                rc = 124
            except OSError:
                rc = 127
        raw, errors = out.read_bytes(), err.read_bytes()
        summary['commands'].append({'name': name, 'argv': argv, 'rc': rc, 'stdout_bytes': len(raw),
             'stdout_sha256': sha(raw), 'stderr_bytes': len(errors), 'stderr_sha256': sha(errors)})
        return rc, raw
    rc, help_all = query('nm-help-all', ['/usr/sbin/NetworkManager', '--help-all'])
    summary['nm_options'] = {key: key.encode() in help_all for key in ('--config-dir', '--print-config', '--config')}
    if rc == 0 and all(summary['nm_options'].values()):
        nm = work / 'nm-conf.d'
        nm.mkdir()
        for path in Path('/etc/NetworkManager/conf.d').glob('*.conf'):
            require(not path.is_symlink() and path.is_file(), 'NM_SOURCE_SYMLINK')
            (nm / path.name).write_bytes(path.read_bytes())
        require(not (nm / '90-hbr-no-auto-default.conf').exists(), 'CANDIDATE_ALREADY_INSTALLED')
        # Exact NM bytes produced by the approved #21 renderer; pinned in this handoff.
        candidate = (local / '90-hbr-no-auto-default.conf.candidate').read_bytes()
        (nm / '90-hbr-no-auto-default.conf').write_bytes(candidate)
        summary['nm_candidate_sha256'] = sha(candidate)
        rc, raw = query('nm-shadow-print', ['/usr/sbin/NetworkManager', '--print-config',
                     '--config=/etc/NetworkManager/NetworkManager.conf', '--config-dir=' + str(nm)])
        summary['nm_selected'] = [line for line in raw.decode(errors='replace').splitlines()
                   if line.startswith(('no-auto-default=', '[device-hbr-mgmt]', 'match-device=', 'managed='))]
    else:
        summary['issues'].append('NM_OPTIONS_STILL_UNCONFIRMED')
    firewall = work / 'firewalld'
    (firewall / 'zones').mkdir(parents=True)
    # Preserve the installed main configuration in PRIVATE work; never export its contents.
    require(Path('/etc/firewalld/firewalld.conf').is_file(), 'FIREWALL_CONFIG_MISSING')
    (firewall / 'firewalld.conf').write_bytes(Path('/etc/firewalld/firewalld.conf').read_bytes())
    zone = (OLD / 'firewalld/zones/hbr-mgmt.xml').read_bytes()
    (firewall / 'zones/hbr-mgmt.xml').write_bytes(zone)
    summary['zone_sha256'] = sha(zone)
    query('firewall-shadow-check', ['/usr/bin/firewall-offline-cmd', '--system-config=' + str(firewall), '--check-config'])
    summary['nonzero'] = [c['name'] for c in summary['commands'] if c['rc']]
    summary['warnings'] = [c['name'] for c in summary['commands'] if c['stderr_bytes']]
    summary['finished_epoch'] = time.time()
    summary['verdict'] = 'REVIEW_REQUIRED_NOT_INSTALL_GO'
    raw = (json.dumps(summary, indent=2) + '\n').encode()
    (work / 'SUMMARY.json').write_bytes(raw)
    dest = SHARE / 'SUPPLEMENT'
    dest.mkdir(exist_ok=False)
    (dest / 'SUMMARY.json').write_bytes(raw)
    (dest / 'nm-help-all.stdout').write_bytes(help_all)
    manifest = (sha(raw) + '  SUMMARY.json\n' + sha(help_all) + '  nm-help-all.stdout\n').encode()
    (dest / 'SHA256SUMS').write_bytes(manifest)
    with (SHARE / 'EXPORT_DONE').open('x') as out:
        out.write(sha(manifest) + '\n')
    print('SSH_SYNTAX_SUPPLEMENT_EXPORTED REVIEW_REQUIRED NONZERO=' + str(len(summary['nonzero'])) +
          ' ISSUES=' + str(len(summary['issues'])) + ' WARNINGS=' + str(len(summary['warnings'])))
    print('No install, reload, NIC, account, service or Docker changes performed.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('SSH_SYNTAX_SUPPLEMENT_STOP; preserve private results; no automatic retry.')
        raise SystemExit(2)
