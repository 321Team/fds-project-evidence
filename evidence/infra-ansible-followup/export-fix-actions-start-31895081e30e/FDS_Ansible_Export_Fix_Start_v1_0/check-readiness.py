"""Runs without root as ansible-verify; reads receipt and image metadata only."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import subprocess

PREPARED = Path('/home/ansible-verify/ansible-actions-0965ce3ff3464f54acdddd46f24af4f6/evidence/PREPARED.json')
BUNDLE = 'e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6'
IMAGE = 'sha256:3f96787b2a8db29294002677a3e733689439952ad9e95db721acf8e16ff601f1'


def require(ok, code):
    if not ok:
        raise RuntimeError(code)


def validate_prepared(value):
    require(value.get('status') == 'PASS_PREPARE' and value.get('repository') == '321Team/infra-ansible'
            and value.get('runner_version') == '2.337.0' and value.get('bundle_sha256') == BUNDLE
            and value.get('image_id') == IMAGE and value.get('container_cleanup') == 'REMOVED', 'PREPARED_BINDING_MISMATCH')


def validate_image(items):
    require(type(items) is list and len(items) == 1, 'IMAGE_COUNT_MISMATCH')
    item = items[0]
    image = item.get('Id', '')
    if not image.startswith('sha256:'):
        image = 'sha256:' + image
    require(image == IMAGE and item.get('Architecture') == 'amd64' and item.get('Os') == 'linux'
            and item.get('Config', {}).get('Labels', {}).get('io.fds.bundle') == BUNDLE, 'IMAGE_BINDING_MISMATCH')


def check():
    require(os.getuid() == os.geteuid() == 1001 and os.getgid() == 1002
            and pwd.getpwuid(1001).pw_name == 'ansible-verify', 'DEDICATED_IDENTITY_MISMATCH')
    require(socket.gethostname().split('.')[0] == 'cicd-runner01', 'HOST_MISMATCH')
    require(not any(p.is_symlink() for p in (PREPARED, *PREPARED.parents)), 'LINKED_PREPARED_PATH')
    os.chdir('/home/ansible-verify')
    fd = os.open(PREPARED, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        info = os.fstat(f.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == 1001
                and stat.S_IMODE(info.st_mode) == 0o600 and 0 < info.st_size <= 65536, 'PREPARED_FILE_INVALID')
        raw = f.read(65537)
        require(len(raw) == info.st_size, 'PREPARED_CHANGED')
    validate_prepared(json.loads(raw))
    result = subprocess.run(['podman', '--remote=false', '--cgroup-manager=systemd', 'image', 'inspect', IMAGE],
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=60, cwd='/home/ansible-verify')
    require(result.returncode == 0 and len(result.stdout) <= 1024*1024, 'IMAGE_INSPECT_FAILED')
    validate_image(json.loads(result.stdout))
    return hashlib.sha256(raw).hexdigest()


def main():
    result = {'status': 'FAIL_RUNNER_READINESS', 'prepared': str(PREPARED), 'bundle_sha256': BUNDLE,
              'image_id': IMAGE, 'scope': 'receipt and current local image only; full host/IPC/isolation checks remain in launcher',
              'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'token_read': False,
              'container_started': False, 'runner_registered': False}
    try:
        result['prepared_sha256'] = check()
        result['status'] = 'PASS_PREPARED_IMAGE_READINESS'
    except RuntimeError as exc:
        result['error'] = str(exc)
    except Exception as exc:
        result['error_type'] = type(exc).__name__
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS_PREPARED_IMAGE_READINESS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
