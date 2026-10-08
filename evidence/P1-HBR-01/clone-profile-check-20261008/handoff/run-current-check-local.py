"""Transfer the pinned #17 source, run ONLY check-current, export selected evidence.

Locally checked read-only handoff wrapper; not independently reviewed trial code.
No apply, restore, service restart, relabel, network or daemon configuration changes.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time

SOURCE_SHA = '0a79b3b70d18211fcacb94903332b81e71168ade18225909ed4d53e26be3d8c4'
HEAD = '1a24d45c7ee6b9418e0b60f059fe13dc78670969'
MERGE = 'a77990c5c7d52114a4b9f361125248c79f129a42'
WORK = '/root/hbr-address-trial-20261008-1607'
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
SAFE_NAMES = {'state', 'listener', 'profile-engine', 'profile-compose', 'profile-security',
              'profile-enforcing', 'profile-labels'}


def require(ok, code):
    if not ok:
        raise RuntimeError(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_file(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 8*1024*1024, 'INVALID_FILE')
    return path.read_bytes()


def selected_files(private):
    raw = read_file(private / 'check-current-result.json')
    result = json.loads(raw)
    require(result['mode'] == 'check-current' and result['source_sha256'] == SOURCE_SHA,
            'RESULT_SCOPE_MISMATCH')
    require(result['DOCKER_RESTART'] == 'NOT_RUN', 'UNEXPECTED_RESULT')
    files = {'check-current-result.json': raw}
    stderr_metadata = []
    for cmd in result['commands']:
        filename = cmd['stdout_file']
        require(re.fullmatch(r'check-current-\d+-[a-z0-9-]+\.stdout', filename) is not None,
                'INVALID_OUTPUT_NAME')
        name = cmd['name']
        if name in SAFE_NAMES or name.startswith(('image-', 'volume-')):
            files[filename] = read_file(private / filename)
        # base/effective Compose renderings and all raw stderr stay private.
        stderr = read_file(private / filename.replace('.stdout', '.stderr'))
        stderr_metadata.append({'name': name, 'rc': cmd['rc'], 'bytes': len(stderr), 'sha256': sha(stderr)})
    files['stderr-metadata.json'] = (json.dumps(stderr_metadata, indent=2) + '\n').encode()
    return result, files


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER_MISMATCH')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID_MISMATCH')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'PHYSICAL_NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-check-local-'), 'LOCAL_PATH_MISMATCH')
    share = Path('/mnt/hbr-check')
    require(str(share) in ('/mnt/hgfs/HBR_CHECK', '/mnt/hbr-check'), 'SHARE_PATH_MISMATCH')
    expiry = int(read_file(local / 'expires-epoch.txt'))
    require(time.time() < expiry, 'HANDOFF_EXPIRED')
    os.umask(0o077)
    # One invocation per delivered bundle; failures are retained, never retried automatically.
    with (share / 'STARTED').open('x') as f:
        f.write(str(time.time()) + '\n')
    raw = read_file(local / 'clone-address-trial.py')
    require(sha(raw) == SOURCE_SHA, 'SOURCE_HASH_MISMATCH')
    bundle = Path(tempfile.mkdtemp(prefix='hbr-profile-approved-', dir='/root'))
    source = bundle / 'clone-address-trial.py'
    source.write_bytes(raw)
    require(sha(read_file(source)) == SOURCE_SHA, 'COPIED_SOURCE_HASH_MISMATCH')
    argv = ['python3', str(source), 'check-current', '--bundle', str(bundle),
            '--work', WORK, '--a2r1-mode-profile']
    started = time.time()
    with (bundle / 'wrapper.stdout').open('xb') as out, (bundle / 'wrapper.stderr').open('xb') as err:
        try:
            rc = subprocess.run(argv, env=ENV, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                timeout=1200).returncode
        except subprocess.TimeoutExpired:
            rc = 124
        except KeyboardInterrupt:
            rc = 130
    stdout = read_file(bundle / 'wrapper.stdout').decode('utf-8', errors='replace')
    match = re.fullmatch(r'(CANDIDATE_METADATA_VERIFIED|STOP_BEFORE_CHANGE) PRIVATE=(/root/hbr-a2r1-check-[a-z0-9_]+)\n', stdout)
    receipt = {'approved_head': HEAD, 'merge': MERGE, 'source_sha256': SOURCE_SHA,
               'wrapper_sha256': sha(read_file(Path(__file__))), 'wrapper_review': 'LOCAL_SELF_CHECK_ONLY',
               'argv': argv, 'started_epoch': started, 'finished_epoch': time.time(), 'rc': rc,
               'private_bundle': str(bundle), 'DOCKER_RESTART': 'NOT_RUN', 'RESTORE': 'NOT_RUN',
               'APPLY': 'NOT_RUN', 'AUTOSTART': 'NOT_TESTED'}
    files = {}
    if match:
        private = Path(match[2])
        require(not private.is_symlink(), 'RESULT_SYMLINK')
        result, files = selected_files(private)
        receipt.update(private_result=str(private), status=result['status'])
    else:
        receipt['status'] = 'NO_COMPLETE_RESULT_REQUIRES_PRIVATE_REVIEW'
    files['RECEIPT.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    dest = share / 'CHECK_RESULT'
    dest.mkdir(exist_ok=False)
    for name, data in files.items():
        with (dest / name).open('xb') as f:
            f.write(data)
    (dest / 'SHA256SUMS').write_text(''.join(sha(data) + '  ' + name + '\n'
        for name, data in sorted(files.items())), encoding='utf-8')
    print('CHECK_EXPORTED STATUS=' + receipt['status'] + ' RC=' + str(rc))
    print('No apply, restore, restart or security changes performed.')
    return rc


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        code = str(exc)
        print('HANDOFF_STOP ' + (code if re.fullmatch('[A-Z_]+', code) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
