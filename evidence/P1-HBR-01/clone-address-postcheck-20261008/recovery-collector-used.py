"""Read existing results and Docker metadata only; never mutate services/data."""
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
SOURCE_SHA = '584fe787f78eec41e13390dfa08a8af656183cb9befbbd154e47bb89c4ee41a8'
DOCKER = ['docker', '--host=unix:///var/run/docker.sock']
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
FORMAT = ('{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Image}},'
          '"service":{{json (index .Config.Labels "com.docker.compose.service")}},'
          '"project":{{json (index .Config.Labels "com.docker.compose.project")}},'
          '"status":{{json .State.Status}},"health":{{if .State.Health}}{{json .State.Health.Status}}{{else}}null{{end}},'
          '"restart":{{json .HostConfig.RestartPolicy}},"mounts":{{json .Mounts}},'
          '"ports":{{json .HostConfig.PortBindings}},"logging":{{json .HostConfig.LogConfig}}}')
VFORMAT = ('{"name":{{json .Name}},"driver":{{json .Driver}},"mountpoint":{{json .Mountpoint}},'
           '"scope":{{json .Scope}},"has_options":{{if .Options}}true{{else}}false{{end}}}')
ERROR_HINTS = ('permission denied', 'connection refused', 'read-only file system',
               'failed to initialize logging driver', 'address already in use',
               'no such file or directory', 'no such container', 'no such volume',
               'in use by container', 'bind source path does not exist', 'context deadline exceeded')

def require(ok, code):
    if not ok:
        raise RuntimeError(code)

def read_safe(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 16 * 1024 * 1024, 'FILE_INVALID')
    return path.read_bytes()

def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER_MISMATCH')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID_MISMATCH')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'PHYSICAL_NIC_PRESENT')
    share = Path(__file__).resolve().parent
    require(str(share) in ('/mnt/hgfs/HBR_RESULT', '/mnt/hbr-result'), 'SHARE_PATH_MISMATCH')
    require(not WORK.is_symlink(), 'WORK_SYMLINK')
    raw = read_safe(WORK / 'apply-result.json')
    result = json.loads(raw)
    require(result['mode'] == 'apply' and result['status'] == 'STOP_RECOVERY_REQUIRED', 'UNEXPECTED_RESULT')
    require(result['source_sha256'] == SOURCE_SHA, 'TRIAL_SOURCE_MISMATCH')
    require(sum(c['name'] == 'recreate-apps' for c in result['commands']) == 1, 'UNEXPECTED_ATTEMPT_COUNT')
    files = {'apply-result.json': raw}
    errors = []
    for command in result['commands']:
        filename = command['stdout_file']
        require(Path(filename).name == filename and filename.endswith('.stdout'), 'OUTPUT_NAME_INVALID')
        name = command['name']
        if name in ('state', 'listener') or name.startswith(('image-', 'volume-')):
            files[filename] = read_safe(WORK / filename)
        stderr = WORK / filename.replace('.stdout', '.stderr')
        data = read_safe(stderr)
        text = data.decode(errors='replace').lower()
        errors.append({'command': name, 'rc': command['rc'], 'stderr_sha256': hashlib.sha256(data).hexdigest(),
                       'stderr_bytes': len(data), 'fixed_hints': [hint for hint in ERROR_HINTS if hint in text]})
    files['ERROR_HINTS.json'] = (json.dumps(errors, indent=2) + '\n').encode()
    os.umask(0o077)
    private = Path(tempfile.mkdtemp(prefix='hbr-a2r1-readonly-', dir='/root'))
    commands = []
    def query(name, argv):
        started = time.time()
        try:
            p = subprocess.run(argv, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            rc, stdout, stderr = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, stdout, stderr = 124, exc.stdout or b'', exc.stderr or b''
        (private / (name + '.stdout')).write_bytes(stdout)
        (private / (name + '.stderr')).write_bytes(stderr)
        commands.append({'name': name, 'argv': argv, 'rc': rc, 'started_epoch': started, 'finished_epoch': time.time(),
                         'stderr_sha256': hashlib.sha256(stderr).hexdigest()})
        files['current-' + name + '.stdout'] = stdout
        return rc, stdout
    rc, stdout = query('container-ids', DOCKER + ['ps', '-aq', '--filter', 'label=com.docker.compose.project=harbor'])
    ids = stdout.decode().split() if rc == 0 else []
    require(len(ids) <= 32 and all(re.fullmatch('[0-9a-f]{12,64}', s) for s in ids), 'INVENTORY_INVALID')
    if ids:
        query('state', DOCKER + ['inspect', '--type', 'container', '--format', FORMAT, *ids])
    volumes = sorted({m['Name'] for row in result.get('before', {}).values() for m in row['mounts'] if m['Type'] == 'volume'})
    require(len(volumes) <= 32 and all(re.fullmatch('[0-9a-f]{64}', s) for s in volumes), 'VOLUME_INPUT_INVALID')
    if volumes:
        query('original-volumes', DOCKER + ['volume', 'inspect', '--format', VFORMAT, *volumes])
    query('listener', ['ss', '-H', '-ltn4', 'sport', '=', ':1514'])
    receipt = {'collected_epoch': time.time(), 'private_source': str(WORK), 'fresh_private_results': str(private),
               'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'READ_ONLY_FILE_RECEIPT_AND_DOCKER_PS_INSPECT_SS', 'commands': commands,
               'APPLY_RETRY': 'NOT_RUN', 'RESTORE': 'NOT_RUN', 'DOCKER_RESTART': 'NOT_RUN'}
    files['RECEIPT.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    destination = share / 'A2R1_RECOVERY'
    destination.mkdir(exist_ok=False)
    for name, data in files.items():
        with (destination / name).open('xb') as f:
            f.write(data)
    with (destination / 'SHA256SUMS').open('x') as f:
        f.write(''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in sorted(files.items())))
    with (share / 'EXPORT_DONE').open('x') as f:
        f.write(hashlib.sha256((destination / 'SHA256SUMS').read_bytes()).hexdigest() + '\n')
    print('A2R1_RECOVERY_EXPORTED ERROR=' + result.get('error_code', 'UNSPECIFIED'))
    print('CURRENT_QUERY_RCS=' + ','.join(c['name'] + ':' + str(c['rc']) for c in commands))
    print('No apply, restore, restart or retry performed.')

if __name__ == '__main__':
    main()
