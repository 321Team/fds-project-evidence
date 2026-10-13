"""Bounded metadata-only cleanup. Default is read-only; stdin is metadata, never tokens."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import socket
import stat
import sys

def identity(s):
    return {'dev':s.st_dev,'ino':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,
            'mode':oct(stat.S_IMODE(s.st_mode)),'regular':stat.S_ISREG(s.st_mode),
            'nlink':s.st_nlink,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}

def checked(fd,row):
    s=os.stat(Path(row['path']).name,dir_fd=fd,follow_symlinks=False)
    value=identity(s)
    if not value['regular'] or value['nlink']!=1 or value['uid']!=1000 or value['mode']!='0o600':
        raise ValueError('FILE_TYPE_OWNER_OR_MODE_CHANGED')
    if any(value[k]!=row[k] for k in value):
        raise ValueError('FILE_METADATA_CHANGED')

def operate(fd,rows,execute,emit):
    for row in rows: checked(fd,row)
    emit({'status':'ALL_TARGETS_MATCH','count':len(rows),'execute':execute})
    if not execute:return
    for row in rows:
        checked(fd,row)
        os.unlink(Path(row['path']).name,dir_fd=fd)
        emit({'status':'DELETED','path':row['path'],'at_utc':dt.datetime.now(dt.timezone.utc).isoformat()})
    for row in rows:
        try:os.stat(Path(row['path']).name,dir_fd=fd,follow_symlinks=False)
        except FileNotFoundError:continue
        raise ValueError('TARGET_REAPPEARED')
    emit({'status':'ALL_TARGETS_ABSENT','count':len(rows)})

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    expected=json.load(sys.stdin)
    assert socket.gethostname()==expected['host']=='ansible01'
    assert os.getuid()==expected['uid']==1000
    assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected['boot']
    rows=expected['packets']; names=[x['path'] for x in rows]
    assert len(rows)==len(set(names))==28
    parent=Path('/home/server01_ansible')
    for name in names:
        f=Path(name)
        assert f.parent==parent and f.name.startswith('ansible-runner-token-') and f.suffix=='.json'
    fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    emit=lambda value:print(json.dumps(value),flush=True)
    try:
        assert os.fstat(fd).st_uid==1000
        operate(fd,rows,args.execute,emit)
    finally:os.close(fd)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'STOP','reason':type(exc).__name__,'detail':str(exc)}),flush=True)
        raise SystemExit(1)
