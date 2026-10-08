"""Read-only Docker/SELinux metadata for the sealed A2R1 mount-mode delta."""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time

WORK = Path('/root/hbr-address-trial-20261008-1607')
EXPECTED_SOURCE = '584fe787f78eec41e13390dfa08a8af656183cb9befbbd154e47bb89c4ee41a8'
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
DOCKER = ['docker', '--host=unix:///var/run/docker.sock']

def require(ok, code):
    if not ok:
        raise RuntimeError(code)

def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_MISMATCH')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID_MISMATCH')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'PHYSICAL_NIC_PRESENT')
    share = Path(__file__).resolve().parent
    require(str(share) in ('/mnt/hgfs/HBR_LABELS', '/mnt/hbr-labels'), 'SHARE_MISMATCH')
    result = json.loads((WORK / 'apply-result.json').read_text())
    require(result['source_sha256'] == EXPECTED_SOURCE and result.get('error_code') == 'PRESERVATION_MOUNTS', 'RESULT_MISMATCH')
    os.umask(0o077)
    private = Path(tempfile.mkdtemp(prefix='hbr-a2r1-labels-', dir='/root'))
    files = {}; commands = []
    def query(name, argv):
        started = time.time()
        try:
            p = subprocess.run(argv, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            rc, stdout, stderr = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, stdout, stderr = 124, exc.stdout or b'', exc.stderr or b''
        except OSError:
            rc, stdout, stderr = 127, b'', b'QUERY_UNAVAILABLE'
        (private / (name + '.stdout')).write_bytes(stdout)
        (private / (name + '.stderr')).write_bytes(stderr)
        commands.append({'name': name, 'argv': argv, 'rc': rc, 'started_epoch': started,
                         'finished_epoch': time.time(), 'stderr_sha256': hashlib.sha256(stderr).hexdigest()})
        files[name + '.stdout'] = stdout
    query('docker-version', DOCKER + ['version', '--format', '{{json .Server}}'])
    query('compose-version', DOCKER + ['compose', 'version', '--short'])
    query('docker-security', DOCKER + ['info', '--format', '{"security_options":{{json .SecurityOptions}},"root":{{json .DockerRootDir}},"driver":{{json .Driver}}}'])
    query('getenforce', ['getenforce'])
    ids = [r['id'] for r in result['after'].values()]
    require(len(ids) == 10 and all(re.fullmatch('[0-9a-f]{64}', s) for s in ids), 'CONTAINER_INPUT_INVALID')
    fmt = ('{"id":{{json .Id}},"name":{{json .Name}},"status":{{json .State.Status}},'
           '"health":{{if .State.Health}}{{json .State.Health.Status}}{{else}}null{{end}},'
           '"mount_label":{{json .MountLabel}},"process_label":{{json .ProcessLabel}},'
           '"security_opt":{{json .HostConfig.SecurityOpt}},"privileged":{{json .HostConfig.Privileged}},'
           '"mount_requests":{{json .HostConfig.Mounts}},"mounts":{{json .Mounts}}}')
    query('container-labels', DOCKER + ['inspect', '--type', 'container', '--format', fmt, *ids])
    images = sorted({r['image'] for r in result['after'].values()})
    require(all(re.fullmatch('sha256:[0-9a-f]{64}', s) for s in images), 'IMAGE_INPUT_INVALID')
    query('image-volume-declarations', DOCKER + ['image', 'inspect', '--format', '{"id":{{json .Id}},"declared_volumes":{{json .Config.Volumes}}}', *images])
    paths = sorted({m['Source'] for r in result['before'].values() for m in r['mounts'] if m['Type'] == 'volume'})
    require(len(paths) == 9 and all(re.fullmatch('/var/lib/docker/volumes/[0-9a-f]{64}/_data', s) for s in paths), 'VOLUME_PATH_INVALID')
    labels = []
    for path in paths:
        entry = {'path': path}
        try:
            entry['selinux_xattr'] = os.getxattr(path, 'security.selinux').decode(errors='replace').rstrip('\x00')
            entry['xattr_status'] = 'READ'
        except OSError as exc:
            entry['xattr_status'] = 'UNAVAILABLE'; entry['errno'] = exc.errno
        labels.append(entry)
    files['volume-directory-labels.json'] = (json.dumps(labels, indent=2) + '\n').encode()
    enforcement = Path('/sys/fs/selinux/enforce')
    meta = {'selinux_enforce_file': enforcement.read_text().strip() if enforcement.exists() else 'ABSENT',
            'daemon_json_selinux_enabled': 'FILE_OR_PROPERTY_ABSENT'}
    daemon = Path('/etc/docker/daemon.json')
    if daemon.is_file():
        try:
            val = json.loads(daemon.read_text()).get('selinux-enabled', 'PROPERTY_ABSENT')
            meta['daemon_json_selinux_enabled'] = val if isinstance(val, bool) else 'PROPERTY_ABSENT_OR_INVALID'
        except (ValueError, OSError):
            meta['daemon_json_selinux_enabled'] = 'UNREADABLE_OR_INVALID'
    files['selected-selinux-config.json'] = (json.dumps(meta, indent=2) + '\n').encode()
    receipt = {'collected_epoch': time.time(), 'private_results': str(private), 'commands': commands,
               'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'READ_ONLY_METADATA_NO_RELABEL_NO_SECURITY_CHANGE', 'RUNTIME_RETRY': 'NOT_RUN',
               'RESTORE': 'NOT_RUN', 'DOCKER_RESTART': 'NOT_RUN'}
    files['RECEIPT.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    out = share / 'A2R1_LABELS'; out.mkdir(exist_ok=False)
    for name, data in files.items():
        with (out / name).open('xb') as f: f.write(data)
    with (out / 'SHA256SUMS').open('x') as f:
        f.write(''.join(hashlib.sha256(v).hexdigest() + '  ' + n + '\n' for n, v in sorted(files.items())))
    with (share / 'EXPORT_DONE').open('x') as f: f.write(hashlib.sha256((out / 'SHA256SUMS').read_bytes()).hexdigest() + '\n')
    print('A2R1_LABELS_EXPORTED ' + ','.join(c['name'] + ':' + str(c['rc']) for c in commands))
    print('No recreate/restart/restore or SELinux changes performed.')

if __name__ == '__main__':
    main()
