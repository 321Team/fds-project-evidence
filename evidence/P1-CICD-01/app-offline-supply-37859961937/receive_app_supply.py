"""Receive exact hosted supply bytes locally; no image load or server transfer."""
import datetime,hashlib,json,pathlib,subprocess,zipfile
r=pathlib.Path(__file__).resolve().parent;root=r/'private/app-supply-37859961937'
root.mkdir(parents=True,exist_ok=False)
def api(path):return subprocess.check_output(['gh','api',path])
run=api('repos/321Team/fds-msa/actions/runs/37859961937');(root/'run.json').write_bytes(run);d=json.loads(run)
assert d['head_sha']=='8eac4c982076e3c219840a13686b15c46879981f' and d['run_attempt']==1 and d['conclusion']=='success'
assert d['event']=='workflow_dispatch' and d['path']=='.github/workflows/apko-offline-supply.yml'
arts=json.loads(api('repos/321Team/fds-msa/actions/runs/37859961937/artifacts'))['artifacts'];assert len(arts)==2
receipts=[]
for a in arts:
    assert not a['expired'] and a['size_in_bytes']<200*1024*1024
    kind='supply' if a['id']==11585741989 else 'diagnostics'
    assert a['id'] in (11585741989,11585507417)
    (root/(kind+'-artifact.json')).write_bytes((json.dumps(a,indent=2)+'\n').encode())
    target=root/(kind+'.zip')
    with target.open('xb') as f:
        p=subprocess.run(['gh','api',f"repos/321Team/fds-msa/actions/artifacts/{a['id']}/zip"],stdout=f,stderr=subprocess.PIPE,timeout=180)
    assert p.returncode==0,p.stderr.decode(errors='replace')
    with target.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    assert target.stat().st_size==a['size_in_bytes'] and 'sha256:'+digest==a['digest']
    receipts.append({'kind':kind,'artifact_id':a['id'],'size_bytes':a['size_in_bytes'],'sha256':digest,'api_digest_matches':True,'expires_at_utc':a['expires_at']})
    if kind=='diagnostics':
        dest=root/'diagnostics';dest.mkdir()
        with zipfile.ZipFile(target) as z:
            assert len(z.infolist())<100 and sum(i.file_size for i in z.infolist())<10*1024*1024
            seen=set()
            for i in z.infolist():
                path=pathlib.PurePosixPath(i.filename)
                assert i.filename not in seen;seen.add(i.filename)
                assert not path.is_absolute() and '..' not in path.parts and '\\' not in i.filename and ':' not in i.filename
                assert (i.external_attr>>16)&0o170000!=0o120000
                p=dest.joinpath(*path.parts)
                if i.is_dir():p.mkdir(parents=True,exist_ok=True)
                else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(i))
with zipfile.ZipFile(root/'supply.zip') as z:
    (root/'SUPPLY_MANIFEST.json').write_bytes(z.read('SUPPLY_MANIFEST.json'))
    # This full manifest lists remotely retained archive contents, not local Git files.
    (root/'SUPPLY_FILE_HASHES.txt').write_bytes(z.read('SHA256SUMS'))
(root/'run.log').write_bytes(subprocess.check_output(['gh','run','view','37859961937','--repo','321Team/fds-msa','--log']))
receipt={'schema':'fds.app-supply-receipt.v1','received_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
         'run_id':37859961937,'run_attempt':1,'source_sha':'affbc69beef9967f7977d09a6fec14f7fb6c0e94',
         'supply_tool_sha':d['head_sha'],'artifacts':receipts,'source_approval':'PENDING','server_transfer':'NOT_RUN','delivery_authorization':False}
(root/'receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt,indent=2))
