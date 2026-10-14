"""Read metadata and public-source hashes only for exact probe workdirs."""
import datetime as dt, hashlib, json, os, re, socket, stat, sys
from pathlib import Path
dirs=sys.argv[1:]
assert 1<=len(dirs)<=3
result={'host':socket.gethostname(),'uid':os.getuid(),'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mutation':False,'directories':[],'active_probe_processes':[]}
for value in dirs:
    p=Path(value)
    assert p.parent==Path.home() and re.fullmatch(r'FDS_NativeProbeSource\.[a-z0-9_]{8}',p.name)
    s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700
    row={'path':value,'mode':oct(stat.S_IMODE(s.st_mode)),'files':[]}
    for f in sorted(p.iterdir()):
        a=f.lstat();assert stat.S_ISREG(a.st_mode) and f.suffix=='.py' and a.st_uid==os.getuid() and stat.S_IMODE(a.st_mode)==0o600
        row['files'].append({'name':f.name,'bytes':a.st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mode':oct(stat.S_IMODE(a.st_mode))})
    result['directories'].append(row)
for p in Path('/proc').iterdir():
    if not p.name.isdigit() or int(p.name)==os.getpid():continue
    try:
        # Only Python processes can be broker/endpoints. Do not expose argv or env.
        comm=(p/'comm').read_text().strip()
        if 'python' not in comm:continue
        args=(p/'cmdline').read_bytes().split(b'\0')
        if any(any(v.encode() in a for v in dirs) for a in args):
            result['active_probe_processes'].append({'pid':int(p.name),'comm':comm})
    except (FileNotFoundError,PermissionError,ProcessLookupError):pass
print(json.dumps(result,sort_keys=True))
