import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cleanup',HERE/'legacy_cleanup.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=json.loads((HERE/'LEGACY_FRESH_METADATA.json').read_text())['packets']
results=[]
for kind in ('dry_no_delete','exact_targets_only','changed_late_target_prevents_all','symlink_rejected','hardlink_rejected','changed_before_unlink_stops','partial_delete_error_recorded'):
    rows=copy.deepcopy(original);state={Path(r['path']).name:dict(r) for r in rows}
    untouched='unrelated.json';state[untouched]=dict(rows[0]);deleted=[];events=[];counts={}
    last=Path(rows[-1]['path']).name
    if kind=='changed_late_target_prevents_all':state[last]['ino']+=1
    if kind=='symlink_rejected':state[last]['regular']=False
    if kind=='hardlink_rejected':state[last]['nlink']=2
    def fake_stat(name,**kw):
        if name not in state:raise FileNotFoundError(name)
        counts[name]=counts.get(name,0)+1
        r=dict(state[name])
        if kind=='changed_before_unlink_stops' and counts[name]==2:r['ctime_ns']+=1
        return SimpleNamespace(st_dev=r['dev'],st_ino=r['ino'],st_uid=r['uid'],st_gid=r['gid'],
            st_mode=(0o100000 if r['regular'] else 0o120000)|int(r['mode'],8),st_nlink=r['nlink'],st_size=r['size'],
            st_mtime_ns=r['mtime_ns'],st_ctime_ns=r['ctime_ns'])
    def fake_unlink(name,**kw):
        if kind=='partial_delete_error_recorded' and len(deleted)==1:raise PermissionError('synthetic')
        del state[name];deleted.append(name)
    error=None
    with patch.object(m.os,'stat',fake_stat),patch.object(m.os,'unlink',fake_unlink):
        try:m.operate(123,rows,kind!='dry_no_delete',events.append)
        except Exception as exc:error=type(exc).__name__
    assert untouched in state
    if kind=='dry_no_delete':assert error is None and deleted==[]
    elif kind=='exact_targets_only':assert error is None and len(deleted)==28 and events[-1]['status']=='ALL_TARGETS_ABSENT'
    elif kind=='partial_delete_error_recorded':assert error=='PermissionError' and len(deleted)==1 and sum(e['status']=='DELETED' for e in events)==1
    else:assert error=='ValueError' and deleted==[]
    results.append({'case':kind,'result':'PASS','deleted_synthetic':len(deleted)})
(HERE/'LEGACY_MOCK_RESULTS.json').write_text(json.dumps({'type':'MOCK','server_files_deleted':0,'cases':results},indent=2)+'\n')
print(json.dumps({'mock_passed':len(results),'server_files_deleted':0}))
