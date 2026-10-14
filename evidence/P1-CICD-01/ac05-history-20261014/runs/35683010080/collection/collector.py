"""Read four fixed historical rounds; never invoke old workflow/scanner code."""
import base64,collections,datetime,hashlib,json,os,pathlib,re,socket,stat,sys
assert socket.gethostname() == 'cicd-runner01' and os.getuid() == 1000
CASES = {
 '35588577241':('FDS_CICD_AppWorkflow.vej0q8at','b5effa840f6b8166cd6f6f52edafe98c7d7a94f4','app'),
 '35683010080':('FDS_CICD_AppWorkflow.log3xwta','7e939d7f77c38c13fd331b38f6649580bf0d05bd','app'),
 '35047422631':('trivy-ci-35047422631-1-xhbwyzog','434a6ddf0d475ffb9857a01dfa2b229eaf637526','toolcheck'),
 '35050018964':('trivy-ci-35050018964-1-yvbjy09i','80d6968b8cf5d145bb37b685d92b3cccf4ecffa7','toolcheck')}
run = sys.argv[1]; name,expected_sha,kind = CASES[run]
root = pathlib.Path('/home/server01_cicd-runner')/name
assert not root.is_symlink() and root.stat().st_uid == 1000 and stat.S_IMODE(root.stat().st_mode) == 0o700
out = {'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'new_runtime':False,'run_id':run,'root':str(root),'expected_workflow_sha':expected_sha,'files':{},'hash_only':{},'missing':[],'report_summaries':{}}
def regular(name,limit):
    p = root/name
    assert not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts
    if not p.exists(): out['missing'].append(name); return None
    for part in (p,*p.parents): assert not part.is_symlink()
    s = p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and s.st_nlink == 1 and s.st_size <= limit
    return p,s
def unchanged(p,s):
    after = p.stat(); assert (s.st_ino,s.st_size,s.st_mtime_ns) == (after.st_ino,after.st_size,after.st_mtime_ns)
def read(name,required=True):
    found = regular(name,8*1024**2)
    if not found:
        assert not required, 'MISSING_REQUIRED:'+name
        return None
    p,s = found; raw = p.read_bytes(); unchanged(p,s)
    out['files'][name] = {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mode':oct(stat.S_IMODE(s.st_mode)),'base64':base64.b64encode(raw).decode()}
    return raw
def hash_file(name,expected):
    # Historical DB size was read separately (1.414/1.427 GB). Stream within
    # a bounded 2 GiB limit; do not copy DB bytes to the workstation.
    found = regular(name,2*1024**3)
    if not found:
        out['hash_only'][name] = {'present':False,'expected_sha256':expected}; return
    p,s = found; h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''): h.update(block)
    unchanged(p,s)
    assert expected is None or h.hexdigest() == expected, 'HASH_MISMATCH:'+name
    out['hash_only'][name] = {'present':True,'bytes':s.st_size,'sha256':h.hexdigest(),'expected_sha256':expected,'expected_match':None if expected is None else True,'raw_copied':False}
def report(name,expected):
    hash_file(name,expected)
    found = regular(name,64*1024**2)
    if not found: return
    p,s = found; data = json.loads(p.read_bytes()); unchanged(p,s)
    counts = collections.Counter(); entries = []
    for result in data.get('Results',[]):
        for v in result.get('Vulnerabilities') or []:
            if v.get('Severity') not in ('HIGH','CRITICAL'): continue
            counts[v['Severity']] += 1
            entries.append({k:v.get(k) for k in ('VulnerabilityID','PkgName','InstalledVersion','FixedVersion','Severity','Status')})
    out['report_summaries'][name] = {'counts':{k:counts[k] for k in ('HIGH','CRITICAL')},'findings':entries,'allowed_fields_only':True,'source_sha256':out['hash_only'][name]['sha256'],'scope':'Historical report; not current vulnerability validation'}
if kind == 'app':
    app = json.loads(read('result.json')); context = app['context']
    assert context['run_id'] == run and context['attempt'] == 1 and context['workflow_sha'] == expected_sha
    read('SHA256SUMS'); handoff = read('handoff.json')
    assert hashlib.sha256(handoff).hexdigest() == app['handoff_sha256']
    result_by_folder = {'':app}
    for folder in ('build-scan/','build-scan/scan/','build-scan/scan/db/'):
        result_by_folder[folder] = json.loads(read(folder+'result.json')); read(folder+'SHA256SUMS')
    build = result_by_folder['build-scan/']; scan = result_by_folder['build-scan/scan/']; db = result_by_folder['build-scan/scan/db/']
    assert app['build_result_sha256'] == out['files']['build-scan/result.json']['sha256']
    assert build['scan_result_sha256'] == out['files']['build-scan/scan/result.json']['sha256']
    assert scan['db_result_sha256'] == out['files']['build-scan/scan/db/result.json']['sha256']
    for folder,data in result_by_folder.items():
        for step in data.get('steps',[]):
            label = step['name']; assert re.fullmatch('[A-Za-z0-9_.-]+',label) and '..' not in label
            assert hashlib.sha256(read(folder+label+'.log')).hexdigest() == step['log_sha256']
    for image in ('transaction-api','fds-engine'):
        read('build-scan/scan/'+image+'/exit-code.txt',False)
        read('build-scan/scan/'+image+'/empty.yaml',False)
        read('build-scan/scan/'+image+'/empty.ignore',False)
        if image in scan['images']:
            report('build-scan/scan/'+image+'/report.json',scan['images'][image]['report_sha256'])
        if image in build['images']:
            hash_file('build-scan/'+image+'.oci.tar',build['images'][image]['archive_sha256'])
    hash_file('build-scan/source.tar',build['source_archive_sha256'])
    hash_file('build-scan/scan/db/cache/db/trivy.db',db['db_sha256'])
    assert hashlib.sha256(read('build-scan/scan/db/cache/db/metadata.json')).hexdigest() == db['metadata_sha256']
else:
    context = json.loads(read('context.json'))
    assert context['run_url'].endswith('/'+run) and context['attempt'] == 1 and context['workflow_sha'] == expected_sha
    for name in ('result.json','SHA256SUMS','DB_SHA256SUMS','installed-binary.sha256','metadata.json','findings.exit-code.txt','findings.log','fixture/requirements.txt','missing-db.exit-code.txt','missing-db.log'):read(name)
    # A filesystem fixture scan, not an application image report. Still keep
    # only a whitelist summary; exclude unneeded report metadata from Git.
    report('findings.json',None)
out['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(out))
