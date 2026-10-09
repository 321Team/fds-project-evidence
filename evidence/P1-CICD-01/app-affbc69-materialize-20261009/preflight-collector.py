"""Fixed paths; metadata only, no server writes or application execution."""
import datetime
import json
import os
from pathlib import Path
import pwd
import shutil
import socket
import stat

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
assert datetime.datetime.fromisoformat('2026-10-09T13:20:00+09:00') <= now < datetime.datetime.fromisoformat('2026-10-09T17:00:00+09:00')
user = pwd.getpwuid(os.getuid())
assert os.getuid() == os.geteuid() == 1000
assert user.pw_name == 'server01_cicd-runner'
assert user.pw_dir == '/home/server01_cicd-runner'
assert socket.gethostname().split('.')[0] == 'cicd-runner01'
home = Path(user.pw_dir)
parent = home / 'FDS_CICD_Runtime'
target = parent / 'FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a'
paths = [Path('/'), Path('/home'), home, parent, target,
         parent / 'FDS_CICD_ApkoSupply.adc90410f99cb.f4d55db6ecbe']
rows = []
for p in paths:
    try:
        s = p.lstat()
        rows.append(dict(path=str(p), exists=True, uid=s.st_uid, gid=s.st_gid,
                         mode=oct(stat.S_IMODE(s.st_mode)), symlink=stat.S_ISLNK(s.st_mode),
                         directory=stat.S_ISDIR(s.st_mode), device=s.st_dev, inode=s.st_ino,
                         writable=os.access(p, os.W_OK), searchable=os.access(p, os.X_OK)))
    except FileNotFoundError:
        rows.append(dict(path=str(p), exists=False))
result = dict(schema='fds.materialize-preflight.metadata.v1', collected_at_kst=now.isoformat(),
              host=socket.gethostname(), account=user.pw_name, uid=os.getuid(), paths=rows,
              free_bytes=shutil.disk_usage(parent).free, readonly=bool(os.statvfs(parent).f_flag & os.ST_RDONLY),
              server_writes=False, materialize='NOT_RUN', podman='NOT_RUN', runtime='NOT_RUN',
              concurrency_exclusion='USER_WINDOW_PLUS_SEPARATE_GITHUB_SNAPSHOT_NOT_A_HOST_LOCK')
print(json.dumps(result, indent=2))
