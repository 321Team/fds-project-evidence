"""Bounded, read-only export of one finished negative Run; binaries/report hash-only."""
import base64, collections, datetime, hashlib, json, os, pathlib, re, socket, stat, sys
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
run,case,folder=sys.argv[1:4]
assert re.fullmatch('[1-9][0-9]*',run) and case in ('vulnerability','scanner-error')
assert re.fullmatch('FDS_CICD_ScanNegative[.][a-z0-9_]+',folder)
home=pathlib.Path('/home/server01_cicd-runner');root=home/folder
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
out={'started_at_utc':now(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,
     'new_runtime':False,'run_id':run,'case':case,'root':str(root),'files':{},'hash_only':{},'report_summary':{},'manifest_matches':0}
allowed={'result.json','SHA256SUMS','scan/result.json','scan/SHA256SUMS','scan/db/result.json','scan/db/SHA256SUMS',
         'scan/db/cache/db/metadata.json','scan/transaction-api/exit-code.txt','scan/transaction-api/scanner-stderr.log',
         'scan/transaction-api/scanner-invocation.json','scan/transaction-api/empty.yaml','scan/transaction-api/empty.ignore'}
def check(p,limit):
    for v in (p,*p.parents):
        st=v.lstat();assert not stat.S_ISLNK(st.st_mode) and not st.st_mode & 0o022
    st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==1000 and st.st_nlink==1 and st.st_size<=limit
    return st
def content(p,limit):
    st=check(p,limit);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        opened=os.fstat(f.fileno());raw=f.read(limit+1);after=os.fstat(f.fileno())
    assert len(raw)<=limit
    assert (st.st_ino,st.st_size,st.st_mtime_ns)==(opened.st_ino,opened.st_size,opened.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    return raw,st
def export(name):
    raw,st=content(root/name,1024*1024)
    out['files'][name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mode':oct(stat.S_IMODE(st.st_mode)),'base64':base64.b64encode(raw).decode()}
    return raw
assert stat.S_IMODE(root.lstat().st_mode)==0o700
result=json.loads(export('result.json'))
assert result['context']['run_id']==run and result['context']['attempt']==1 and result['case']==case
assert result['context']['workflow_sha']=='65ae4fd3b274efc04c3cb686b41cc99fb07383b8'
claim,cs=content(home/('FDS_CICD_ScanNegative-'+run+'.claim'),1024*1024)
assert json.loads(claim)==result['context']
out['claim']={'name':'FDS_CICD_ScanNegative-'+run+'.claim','sha256':hashlib.sha256(claim).hexdigest(),'base64':base64.b64encode(claim).decode()}
manifest=export('SHA256SUMS').decode('utf-8');entries={};total=0
for line in manifest.splitlines():
    expected,name=line.split('  ',1);rel=pathlib.PurePosixPath(name)
    assert re.fullmatch('[0-9a-f]{64}',expected) and not rel.is_absolute() and '..' not in rel.parts and '\\' not in name and name not in entries
    entries[name]=expected
assert len(entries)<=300
actual=set()
for base,dirs,files in os.walk(root,followlinks=False):
    for n in dirs:assert not (pathlib.Path(base)/n).is_symlink()
    for n in files:
        p=pathlib.Path(base)/n;name=p.relative_to(root).as_posix()
        if name=='SHA256SUMS':continue
        st=check(p,2*1024**3);total+=st.st_size;assert total<=5*1024**3
        actual.add(name);assert name in entries
        with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
            opened=os.fstat(f.fileno());h=hashlib.file_digest(f,'sha256').hexdigest();after=os.fstat(f.fileno())
        assert (st.st_ino,st.st_size,st.st_mtime_ns)==(opened.st_ino,opened.st_size,opened.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
        assert h==entries[name],name
        out['manifest_matches']+=1
        if name in allowed:
            raw=export(name);assert out['files'][name]['sha256']==h
        else:out['hash_only'][name]={'sha256':h,'bytes':st.st_size,'raw_copied':False}
        if name=='scan/transaction-api/report.json':
            raw,_=content(p,64*1024**2);assert hashlib.sha256(raw).hexdigest()==h
            report=json.loads(raw);counts=collections.Counter();findings=[]
            for section in report.get('Results',[]):
                for v in section.get('Vulnerabilities') or []:
                    if v.get('Severity') in ('HIGH','CRITICAL'):
                        counts[v['Severity']]+=1
                        findings.append({k:v.get(k) for k in ('VulnerabilityID','PkgName','InstalledVersion','FixedVersion','Severity','Status')})
            out['report_summary']={'source_sha256':h,'counts':{k:counts[k] for k in ('HIGH','CRITICAL')},'findings':findings,'allowed_fields_only':True}
assert actual==set(entries)
for name,v in list(out['files'].items()):
    if name=='SHA256SUMS' or name.endswith('/SHA256SUMS'):
        parent=pathlib.PurePosixPath(name).parent
        for line in base64.b64decode(v['base64']).decode().splitlines():
            h,n=line.split('  ',1);rel=pathlib.PurePosixPath(n);assert not rel.is_absolute() and '..' not in rel.parts
            full=(parent/rel).as_posix();entry=out['files'].get(full) or out['hash_only'].get(full)
            assert entry and entry['sha256']==h,(name,full)
out['finished_at_utc']=now();out['total_hashed_bytes']=total
print(json.dumps(out,ensure_ascii=False))
