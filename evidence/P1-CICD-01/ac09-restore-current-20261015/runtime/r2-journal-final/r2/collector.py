"""Read exact AC09 claim/checkpoints and their original inode/mtime_ns; never write."""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import pwd
import re
import socket
import stat
import time

ROOT = '/home/server01_cicd-runner/FDS_CICD_DeployClaims'
PLANS = {'6e622c0bf539830c77cc841beb6852b0db65a9652822754d30141e587ca71d2d',
         '3b928b2c74600d81066f4577a0b3095df027351434137249a67ef5e328720183'}
UIDS = {'transaction-api': '8a2af808-ec33-41f2-80b5-addde4e28910',
        'fds-engine': 'bf825dec-465b-4603-8b71-f768d195531c'}
SHA = re.compile('[0-9a-f]{64}')


def no_secrets(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if k.lower() in ('token', 'password', 'authorization', 'private_key', 'client-key-data', 'bearer'):
                raise ValueError('SENSITIVE_FIELD')
            no_secrets(v)
    elif isinstance(value, list):
        for v in value:
            no_secrets(v)
    elif isinstance(value, str):
        if '-----BEGIN' in value or re.search(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', value):
            raise ValueError('SENSITIVE_VALUE')


def metadata(s):
    return dict(device=s.st_dev, inode=s.st_ino, size=s.st_size, mtime_ns=s.st_mtime_ns,
                ctime_ns=s.st_ctime_ns, uid=s.st_uid, mode=stat.S_IMODE(s.st_mode), nlink=s.st_nlink)


def open_directory():
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in ROOT.strip('/').split('/'):
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
            s = os.fstat(fd)
            if s.st_uid not in (0, os.getuid()) or s.st_mode & 0o022:
                raise ValueError('UNSAFE_DIRECTORY')
        if stat.S_IMODE(s.st_mode) != 0o700 or s.st_uid != os.getuid():
            raise ValueError('CLAIM_ROOT_INVALID')
        return fd
    except Exception:
        os.close(fd)
        raise


def read_file(fd, name):
    before = os.stat(name, dir_fd=fd, follow_symlinks=False)
    if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600 or not 0 < before.st_size <= 1048576):
        raise ValueError('UNSAFE_FILE')
    child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
    with os.fdopen(child, 'rb') as f:
        opened = os.fstat(f.fileno())
        if metadata(before) != metadata(opened):
            raise ValueError('FILE_CHANGED_BEFORE_READ')
        raw = f.read(1048577)
        after = os.fstat(f.fileno())
    if metadata(before) != metadata(after) or metadata(after) != metadata(os.stat(name, dir_fd=fd, follow_symlinks=False)):
        raise ValueError('FILE_CHANGED_DURING_READ')
    data = json.loads(raw)
    no_secrets(data)
    return {'name': name, 'original': metadata(after), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(), 'raw_b64': base64.b64encode(raw).decode(),
            'data': data, 'collected_unix_ns': time.time_ns()}


def verify(claim, checkpoints, expected):
    c = claim['data']
    if c.get('schema') != 'P1-CICD-deploy-claim-2' or c.get('state') != 'CLAIMED':
        raise ValueError('CLAIM_SCHEMA')
    for key, value in expected.items():
        if c.get(key) != value:
            raise ValueError('CLAIM_BINDING_' + key)
    previous = None
    candidates = {'PATCH_PENDING': None, 'APPLIED': None}
    for i, item in enumerate(checkpoints, 1):
        d = item['data']
        if (item['name'] != '%04d.json' % i or d.get('schema') != 'P1-CICD-deploy-checkpoint-1'
                or d.get('sequence') != i or d.get('previous_sha256') != previous
                or d.get('claim_sha256') != claim['sha256']):
            raise ValueError('CHECKPOINT_CHAIN_BINDING')
        r = d['receipt']
        for key, value in expected.items():
            if r.get(key) != value:
                raise ValueError('CHECKPOINT_BINDING_' + key)
        if r.get('claim') != {'state': 'CLAIMED', 'sha256': claim['sha256'], 'execution': expected['execution']}:
            raise ValueError('RECEIPT_CLAIM_BINDING')
        for service, v in r['images'].items():
            if service not in UIDS:
                raise ValueError('UNEXPECTED_TARGET')
            if not isinstance(v.get('before'), dict) or v['before'].get('uid') != UIDS[service]:
                raise ValueError('TARGET_UID_MISMATCH')
            for field in ('before', 'deploy_after', 'rollback_after', 'ready'):
                if field in v and v[field].get('uid') != UIDS[service]:
                    raise ValueError('TARGET_UID_MISMATCH')
            state = v.get('deploy')
            if state in candidates and candidates[state] is None:
                candidates[state] = {'file': item['name'], 'sha256': item['sha256'],
                    'service': service, 'original_mtime_ns': item['original']['mtime_ns']}
        previous = item['sha256']
    return candidates


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan-sha256', choices=sorted(PLANS), required=True)
    p.add_argument('--approval-sha256', required=True)
    p.add_argument('--workflow-sha', required=True)
    p.add_argument('--run-id', type=int, required=True)
    a = p.parse_args()
    if not SHA.fullmatch(a.approval_sha256) or not re.fullmatch('[0-9a-f]{40}', a.workflow_sha) or a.run_id <= 0:
        p.error('actual binding values required')
    if socket.gethostname() != 'cicd-runner01' or os.geteuid() != 1000 or pwd.getpwuid(1000).pw_name != 'server01_cicd-runner':
        raise ValueError('HOST_OR_ACCOUNT_MISMATCH')
    expected = {'plan_sha256': a.plan_sha256, 'approval_sha256': a.approval_sha256,
        'execution': {'repository': '321Team/infra-cicd', 'ref': 'refs/heads/main',
                      'workflow_sha': a.workflow_sha, 'run_id': a.run_id, 'attempt': 1}}
    out = {'schema': 'AC09-JOURNAL-ORIGINALS-1', 'host': socket.gethostname(), 'expected': expected,
        'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'mutation': False,
        'checkpoint_files': [], 'chain_binding': 'NOT_VERIFIED', 'timing': 'NOT_PROVEN_BY_COLLECTOR'}
    root = journal = None
    try:
        root = open_directory()
        out['claim'] = read_file(root, a.plan_sha256 + '.claim.json')
        journal = os.open(a.plan_sha256 + '.checkpoints', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
        s = os.fstat(journal)
        if s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) != 0o700:
            raise ValueError('CHECKPOINT_DIRECTORY_INVALID')
        out['directory_original'] = metadata(s)
        names = sorted(os.listdir(journal))
        if len(names) > 64 or any(not re.fullmatch(r'[0-9]{4}\.json', n) for n in names):
            raise ValueError('CHECKPOINT_NAMES_INVALID')
        for name in names:
            out['checkpoint_files'].append(read_file(journal, name))
        if names != sorted(os.listdir(journal)):
            raise ValueError('CHECKPOINT_SET_CHANGED')
        out['candidates'] = verify(out['claim'], out['checkpoint_files'], expected)
        out['chain_binding'] = 'MATCHED_CAPTURED_FILES'
        out['writer_stopped'] = 'NOT_ESTABLISHED_BY_READ'
    except (OSError, ValueError, KeyError, TypeError) as e:
        out['error'] = str(e) if isinstance(e, ValueError) else type(e).__name__
    finally:
        for fd in (journal, root):
            if fd is not None:
                os.close(fd)
    out['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    print(json.dumps(out, sort_keys=True))
    return 0 if out['chain_binding'] == 'MATCHED_CAPTURED_FILES' else 2


if __name__ == '__main__':
    sys = __import__('sys')
    sys.exit(main())
