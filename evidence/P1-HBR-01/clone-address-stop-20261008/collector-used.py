"""Read-only receipt of the fixed A2 STOP. Never invoke Docker or trial code."""
import hashlib
import json
import os
from pathlib import Path
import socket
import time

SOURCE_SHA = '1b6647b7883dc0458fb0d22d00f3eb88d30e2fa191df353180a41cf46cce8064'
WORK = Path('/root/hbr-address-trial-20261008-1500')

def require(ok, code):
    if not ok:
        raise RuntimeError(code)

def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER_MISMATCH')
    share = Path(__file__).resolve().parent
    require(str(share) in ('/mnt/hgfs/HBR_RESULT', '/mnt/hbr-result'), 'SHARE_PATH_MISMATCH')
    require(not WORK.is_symlink(), 'WORK_SYMLINK')
    source = WORK / 'apply-result.json'
    require(source.is_file() and not source.is_symlink() and source.stat().st_size < 1024 * 1024, 'RESULT_INVALID')
    raw = source.read_bytes()
    result = json.loads(raw)
    require(result['mode'] == 'apply' and result['status'] == 'STOP_BEFORE_CHANGE', 'UNEXPECTED_RESULT')
    require(result['source_sha256'] == SOURCE_SHA, 'TRIAL_SOURCE_MISMATCH')
    require(not any(c['name'] == 'recreate-apps' for c in result['commands']), 'CHANGE_COMMAND_PRESENT')
    files = {'apply-result.json': raw}
    # The reviewed driver emits these selected metadata records without env/secrets.
    for command in result['commands']:
        name = command['name']
        if name not in ('state', 'listener') and not name.startswith('image-'):
            continue
        filename = command['stdout_file']
        require(Path(filename).name == filename and filename.endswith('.stdout'), 'OUTPUT_NAME_INVALID')
        path = WORK / filename
        require(path.is_file() and not path.is_symlink() and path.stat().st_size < 1024 * 1024, 'OUTPUT_INVALID')
        files[filename] = path.read_bytes()
    # Hash other private files for traceability, never export configuration/stderr.
    private = []
    for path in sorted(WORK.iterdir()):
        if path.is_file() and not path.is_symlink():
            data = path.read_bytes()
            private.append({'name': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'exported': path.name in files})
    receipt = {'collected_epoch': time.time(), 'private_source': str(WORK), 'source_sha256': SOURCE_SHA,
               'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'collector_scope': 'READ_ONLY_FILES; no Docker/subprocess/service commands', 'private_files': private}
    files['RECEIPT.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    destination = share / 'A2_STOP'
    destination.mkdir(exist_ok=False)
    for name, data in files.items():
        with (destination / name).open('xb') as f:
            f.write(data)
    with (destination / 'SHA256SUMS').open('x') as f:
        f.write(''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in sorted(files.items())))
    with (share / 'EXPORT_DONE').open('x') as f:
        f.write(hashlib.sha256((destination / 'SHA256SUMS').read_bytes()).hexdigest() + '\n')
    print('A2_STOP_EXPORTED ERROR=' + result.get('error_code', 'UNSPECIFIED'))
    print('No apply, restore, restart or retry performed.')

if __name__ == '__main__':
    main()
