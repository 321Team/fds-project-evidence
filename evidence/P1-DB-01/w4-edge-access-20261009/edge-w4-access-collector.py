"""One-shot offline access-log aggregation; payloads never exported."""
import collections
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import stat
import time

KST=dt.timezone(dt.timedelta(hours=9))
START=dt.datetime.fromisoformat('2026-10-08T20:26:49+09:00')
END=dt.datetime.fromisoformat('2026-10-08T20:27:52+09:00')
MONTHS={x:i for i,x in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(),1)}
LINE=re.compile(rb'^\S+ \S+ \S+ \[(\d\d)/(\w{3})/(\d{4}):(\d\d):(\d\d):(\d\d) ([+-]\d{4})\] "((?:[^"\\]|\\.)*)" ([1-5]\d\d) (?:\d+|-)(?:\s|$)')

def now():return dt.datetime.now(KST).isoformat()

def parse(line):
    m=LINE.match(line)
    if not m:return None
    try:
        day,month,year,hour,minute,second,offset,request,statuscode=m.groups()
        tz=offset.decode(); delta=(int(tz[1:3])*60+int(tz[3:]))*(1 if tz[0]=='+' else -1)
        t=dt.datetime(int(year),MONTHS[month.decode()],int(day),int(hour),int(minute),int(second),tzinfo=dt.timezone(dt.timedelta(minutes=delta)))
        parts=request.split(); path=parts[1].split(b'?',1)[0] if len(parts)>=2 else b''
        label=path.decode('ascii') if path in (b'/api/v1/transactions',b'/readyz',b'/livez',b'/metrics') else 'OTHER'
        return t,statuscode.decode(),label
    except (ValueError,KeyError,UnicodeError):return None

def aggregate(raw, compressed, deadline, cap=64*1024*1024):
    stream=gzip.GzipFile(fileobj=io.BytesIO(raw)) if compressed else io.BytesIO(raw)
    read=valid=unparsed=0;first=last=None;counts=collections.Counter();complete=False;continuation=False
    with stream:
        while read<cap and time.monotonic()<deadline:
            line=stream.readline(min(65536,cap-read));read+=len(line)
            if not line:complete=True;break
            if continuation:
                unparsed+=1;continuation=not line.endswith(b'\n');continue
            if not line.endswith(b'\n'):
                # An unfinished/oversized line is not evidence of a complete request.
                unparsed+=1;continuation=True;continue
            p=parse(line)
            if p is None:unparsed+=1;continue
            t,statuscode,path=p;valid+=1
            first=t if first is None else min(first,t);last=t if last is None else max(last,t)
            if START<=t<=END:counts[(t.astimezone(KST).isoformat(),statuscode,path)]+=1
    return {'parsed_records':valid,'unparsed_chunks':unparsed,'decoded_bytes':read,'stream_complete':complete,
            'first_record_kst':first.astimezone(KST).isoformat() if first else None,
            'last_record_kst':last.astimezone(KST).isoformat() if last else None,
            'w4_counts':[dict(at_kst=t,status=s,path_class=p,count=n) for (t,s,p),n in sorted(counts.items())]}

def collect():
    assert socket.gethostname()=='edge01' and os.geteuid()==0,'STOP host/euid'
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00','STOP outside window'
    out={'schema':'fds.edge-w4-access-projection.v1','host':socket.gethostname(),'started_at_kst':now(),
         'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'interval_start_kst':START.isoformat(),'interval_end_kst':END.isoformat(),
         'boundary':'Read existing /var/log/nginx/*access* only; no nginx command, restart, permission change, HTTP request or log payload export.',
         'format':'nginx common prefix parser; effective log_format and full route coverage NOT_VERIFIED',
         'http_5xx_overall_verdict':'NOT_MEASURED','files':[],'errors':[]}
    deadline=time.monotonic()+60;raw_budget=64*1024*1024;decoded_budget=128*1024*1024
    paths=sorted(p for p in Path('/var/log/nginx').iterdir() if 'access' in p.name)
    out['discovered_paths']=len(paths)
    if len(paths)>32:out['errors'].append('file-count cap: first32 only')
    for path in paths[:32]:
        if time.monotonic()>=deadline or raw_budget<=0 or decoded_budget<=0:
            out['errors'].append('time/byte cap reached');break
        row={'path':str(path)}
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_NOATIME)
            with os.fdopen(fd,'rb') as f:
                before=os.fstat(f.fileno())
                if not stat.S_ISREG(before.st_mode):raise ValueError('not regular file')
                if before.st_size>min(16*1024*1024,raw_budget):
                    row.update(status='SKIPPED_SIZE_CAP',size=before.st_size);out['files'].append(row);continue
                raw=f.read(before.st_size);after=os.fstat(f.fileno())
            raw_budget-=len(raw)
            current=path.lstat()
            stable=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and current.st_ino==before.st_ino and current.st_dev==before.st_dev
            row.update(size_before=before.st_size,size_after=after.st_size,read_bytes=len(raw),read_sha256=hashlib.sha256(raw).hexdigest(),stable_during_read=stable,inode=before.st_ino,mtime_ns=before.st_mtime_ns)
            projection=aggregate(raw,path.suffix=='.gz',deadline,min(64*1024*1024,decoded_budget))
            decoded_budget-=projection['decoded_bytes'];row.update(projection)
            row['status']='SCANNED' if stable and len(raw)==before.st_size and projection['stream_complete'] and projection['unparsed_chunks']==0 else 'PARTIAL_OR_UNPARSED'
        except (OSError,ValueError,EOFError) as e:row.update(status='READ_ERROR',error_type=type(e).__name__,errno=getattr(e,'errno',None))
        out['files'].append(row)
    out['finished_at_kst']=now();return out

def main():
    # One private projection result, owned by staging account for receipt. No overwrite.
    directory=Path(__file__).resolve().parent
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        owner=os.fstat(dfd)
        assert owner.st_uid!=0 and stat.S_IMODE(owner.st_mode)==0o755,'STOP staging directory'
        data=collect()
        raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
        fd=os.open('result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=dfd)
        with os.fdopen(fd,'wb') as f:
            f.write(raw);f.flush();os.fsync(f.fileno());os.fchown(f.fileno(),owner.st_uid,owner.st_gid)
        print('COLLECTION_FINISHED result='+str(directory/'result.json'))
        print('SHA256='+hashlib.sha256(raw).hexdigest())
        print('FILES='+str(len(data['files']))+' OVERALL_5XX=NOT_MEASURED')
    finally:os.close(dfd)

if __name__=='__main__':main()
