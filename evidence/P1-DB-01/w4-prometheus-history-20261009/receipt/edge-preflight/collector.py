import datetime, hashlib, json, os, pathlib, re, socket, stat
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert socket.gethostname() == 'edge01'
assert '2026-10-09T00:00:00+09:00' <= now() < '2026-10-09T09:00:00+09:00'
out={'schema':'fds.edge-log-preflight.v1','host':socket.gethostname(),'euid':os.geteuid(),'started_at_kst':now(),'files':[],'configs':[],'errors':[]}
root=pathlib.Path('/var/log/nginx')
try:
    for p in sorted(root.iterdir())[:64]:
        s=p.lstat()
        out['files'].append({'path':str(p),'size':s.st_size,'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid,'gid':s.st_gid,'mtime_ns':s.st_mtime_ns,'readable_by_current_account':os.access(p,os.R_OK),'symlink':p.is_symlink()})
except OSError as e: out['errors'].append({'path':str(root),'errno':e.errno})
for p in [pathlib.Path('/etc/nginx/nginx.conf')]+sorted(pathlib.Path('/etc/nginx/conf.d').glob('*.conf'))[:32]:
    try:
        if p.is_symlink() or p.stat().st_size>262144: continue
        raw=p.read_bytes(); text=raw.decode(errors='replace')
        # Export logging directives only, never full nginx config or log payload.
        text=re.sub(r'(?m)^\s*#.*$', '', text)
        directives=re.findall(r'(?m)^\s*(?:log_format|access_log)\s+[^;]+;',text)
        out['configs'].append({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'logging_directives':directives})
    except OSError as e: out['errors'].append({'path':str(p),'errno':e.errno})
out['finished_at_kst']=now();print(json.dumps(out))
