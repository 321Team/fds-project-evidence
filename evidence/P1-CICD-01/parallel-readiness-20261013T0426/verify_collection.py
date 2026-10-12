import hashlib,json,sys
from pathlib import Path
P=Path(sys.argv[1])
checked=0
for line in (P/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1)
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
    checked+=1
folders=[P/'broker-key-metadata-controller',P/'broker-key-metadata-cp1',P/'cp1-existing-auth',*sorted(P.glob('oid03-inventory-*'))]
assert len(folders)==9
for d in folders:
    r=json.loads((d/'receipt.json').read_text());assert r['rc']==0
    for name,key in [('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:
        assert hashlib.sha256((d/name).read_bytes()).hexdigest()==r[key]
    raw=(P/('read_oid03_inventory.py' if d.name.startswith('oid03-') else 'read_broker_key_metadata.py')).read_bytes() if d.name!='cp1-existing-auth' else (d/'collector.py').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==r['source_sha256']
auth=json.loads((P/'cp1-existing-auth/stdout.json').read_text())
assert (auth['host'],auth['user'],auth['uid'],auth['api_get']['rc'])==('k8s-control01','server02',1000,0)
assert auth['token_issued'] is False and auth['mutation'] is False
bundle_raw=(P/'native-source-2d8a14c.json').read_bytes();bundle=json.loads(bundle_raw)
meta=json.loads((P/'SOURCE_BUNDLE_MANIFEST.json').read_text())
assert hashlib.sha256(bundle_raw).hexdigest()==meta['bundle_sha256']
assert bundle['source_sha']==meta['source_sha'] and len(bundle['files'])==7
for name,item in bundle['files'].items():
    raw=item['content'].encode()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob']
    compile(raw,name,'exec')
summary=json.loads((P/'OID03_INVENTORY_SUMMARY.json').read_text())
assert len(summary['hosts'])==6
for h in summary['hosts']:
    raw=json.loads((P/h['raw']).read_text());assert raw['host']==h['host']
    assert raw['mutation'] is False and raw['network_fetch'] is False
    assert len(raw['selected_rpm_cache']['matches'])==h['matching_cache_packages']
draft=json.loads((P/'DEPLOY_PREPARATION.pending.json').read_text())
assert draft['template_only'] is True and draft['runtime_authorized'] is False
assert draft['new_push_receipt'] is None and draft['rollback_approved'] is False
print(json.dumps({'sealed_files_verified':checked,'read_receipts_verified':9,'source_files':7,
                  'oid_inventory_hosts':6,'token_issued':False,'deploy':'NOT_EXECUTED','ac_accepted':False}))
