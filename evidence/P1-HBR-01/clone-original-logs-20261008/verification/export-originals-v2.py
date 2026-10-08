#!/usr/bin/env python3
"""Read only the approved clone trial logs; export bytes to the dedicated HGFS share."""
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import tarfile
import uuid

SOURCE = Path('/home/server08/harbor-clone-t0-01')
NAMES = ('start.txt', 'end.txt', 'up.log', 'up.rc', 'before-restart.txt',
         'restart-start.txt', 'restart.log', 'restart.rc', 'state-errors.txt',
         'docker-journal.txt', 'failure.sha256', 'recovery-start.txt',
         'recovery.log', 'recovery.rc')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validate_destination(destination, mount_text):
    allowed = {Path('/mnt/hbr-out'), Path('/mnt/hgfs/HBR_LOG_OUT')}
    if destination not in allowed:
        raise ValueError('use /mnt/hbr-out or /mnt/hgfs/HBR_LOG_OUT')
    covering = []
    for line in mount_text.splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        mountpoint = Path(fields[1])
        if destination == mountpoint or mountpoint in destination.parents:
            covering.append((len(mountpoint.parts), fields))
    if not covering:
        raise ValueError('HGFS mount missing')
    fields = max(covering, key=lambda row: row[0])[1]
    if fields[2] != 'fuse.vmhgfs-fuse' or fields[0] not in ('vmhgfs-fuse', '.host:/', '.host:/HBR_LOG_OUT'):
        raise ValueError('destination is not on the expected HGFS filesystem')

def collect(source):
    if source.is_symlink() or source.resolve() != source:
        raise ValueError('source path is not canonical')
    bodies, metadata = {}, {}
    for name in NAMES:
        fd = os.open(source / name, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > 20*1024*1024:
                raise ValueError('source type/size rejected: ' + name)
            data = handle.read(20*1024*1024 + 1)
            after = os.fstat(handle.fileno())
        fields = ('st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_ino', 'st_dev')
        if any(getattr(before, f) != getattr(after, f) for f in fields) or len(data) != before.st_size:
            raise ValueError('source changed while reading: ' + name)
        bodies[name] = data
        metadata[name] = dict(size=len(data), sha256=digest(data), mode=oct(stat.S_IMODE(before.st_mode)),
                              uid=before.st_uid, gid=before.st_gid, mtime_ns=before.st_mtime_ns)
    expected = {'state-errors.txt', 'docker-journal.txt'}
    seen = set()
    for line in bodies['failure.sha256'].decode('utf-8').splitlines():
        value, sep, raw = line.partition('  ')
        path = Path(raw)
        if not sep or path.parent != source or path.name not in expected or path.name in seen:
            raise ValueError('failure.sha256 path/format mismatch')
        if digest(bodies[path.name]) != value:
            raise ValueError('failure.sha256 content mismatch: ' + path.name)
        seen.add(path.name)
    if seen != expected:
        raise ValueError('failure.sha256 incomplete')
    for name in ('up.rc', 'restart.rc', 'recovery.rc'):
        if bodies[name].strip() != b'0':
            raise ValueError('unexpected recorded exit code: ' + name)
    # This verifies stored command rc values, not application health or automatic recovery.
    return bodies, metadata

def main():
    os.umask(0o077)
    if os.geteuid() != 0 or socket.gethostname().split('.')[0] != 'harbor01':
        raise ValueError('run through normal sudo on harbor01 clone')
    if any((p/'device').exists() for p in Path('/sys/class/net').iterdir()):
        raise ValueError('physical/VM NIC detected; stop')
    destination = Path(__file__).resolve().parent
    validate_destination(destination, Path('/proc/mounts').read_text())
    bodies, metadata = collect(SOURCE)
    record = {'schema':'fds.harbor.clone-original-export.v1',
              'captured_at':datetime.datetime.now().astimezone().isoformat(),
              'host':socket.gethostname(), 'source':str(SOURCE),
              'collector_sha256':digest(Path(__file__).read_bytes()),
              'source_mutations':False, 'new_runtime_test':False,
              'failure_manifest':'MATCH_2_OF_2', 'files':metadata}
    bodies['EXPORT_RECEIPT.json'] = (json.dumps(record, ensure_ascii=False, indent=2)+'\n').encode()
    bodies['RECEIVED_SHA256SUMS'] = ''.join(digest(v)+'  '+k+'\n' for k,v in sorted(bodies.items())).encode()
    stamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    archive = destination/('harbor-originals-'+stamp+'.tar.gz')
    # x mode refuses any existing target; no overwrite or source cleanup.
    with archive.open('xb') as output:
        with tarfile.open(fileobj=output, mode='w:gz') as tar:
            for name, data in sorted(bodies.items()):
                item = tarfile.TarInfo(name)
                item.size, item.mode = len(data), 0o600
                tar.addfile(item, io.BytesIO(data))
        output.flush()
        os.fsync(output.fileno())
    with (destination/(archive.name+'.sha256')).open('x') as output:
        output.write(digest(archive.read_bytes())+'  '+archive.name+'\n')
        output.flush()
        os.fsync(output.fileno())
    with (destination/'EXPORT_READY.json').open('x') as output:
        json.dump({'archive':archive.name,'sha256':digest(archive.read_bytes())},output)
        output.flush()
        os.fsync(output.fileno())
    print('EXPORT_OK: 14 original files; failure hashes 2/2 matched; no runtime changes')
    print('Unmount the temporary HGFS mounts after EXPORT_OK; host share removal is automatic.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as error:
        print('STOP:', str(error))
        raise SystemExit(2)
