"""Bounded historical receipt discovery. Read-only; no rescan or credential read."""
import datetime, hashlib, json, os, pathlib, socket, stat
assert socket.gethostname() == 'cicd-runner01' and os.getuid() == 1000
home = pathlib.Path('/home/server01_cicd-runner')
targets = {'35047422631','35050018964','35588577241','35683010080'}
out = {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'rescan':False,'matches':[],'missing_result_count':0}
roots = sorted(set(home.glob('FDS_CICD_AppWorkflow.*')) | set(home.glob('trivy-ci-*')))
assert len(roots) <= 150
for root in roots:
    st = root.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != 1000 or root.is_symlink(): continue
    p = root/'result.json'
    if not p.exists(): out['missing_result_count'] += 1; continue
    s = p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and not p.is_symlink() and s.st_size < 2*1024**2
    raw = p.read_bytes(); data = json.loads(raw)
    context = data.get('context',{})
    run_id = str(context.get('run_id',data.get('run_id','')))
    if run_id not in targets and not any(root.name.startswith('trivy-ci-'+r+'-') for r in targets): continue
    receipts = {}
    for name in ('result.json','context.json','handoff.json','build-scan/result.json','build-scan/scan/result.json','build-scan/scan/db/result.json'):
        q = root/name
        if not q.exists(): continue
        for part in (q,*q.parents): assert not part.is_symlink()
        sq = q.lstat(); assert stat.S_ISREG(sq.st_mode) and sq.st_uid == 1000 and sq.st_size < 2*1024**2
        blob = q.read_bytes(); record = json.loads(blob)
        receipts[name] = {'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'data':record}
    out['matches'].append({'path':str(root),'mode':oct(stat.S_IMODE(st.st_mode)),'run_id':run_id,'top_files':sorted(p.name for p in root.iterdir()),'receipts':receipts})
out['matched_roots'] = len(out['matches'])
print(json.dumps(out))
