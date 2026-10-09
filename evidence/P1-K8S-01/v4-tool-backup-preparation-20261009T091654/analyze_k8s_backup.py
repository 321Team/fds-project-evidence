"""Offline projection replay; optional private receipt/byte verification."""
import base64,hashlib,json,pathlib,sys
def sha(raw): return hashlib.sha256(raw).hexdigest()
def project(data):
    data=json.loads(json.dumps(data))
    for row in data['files']:
        if 'content_base64' in row:
            del row['content_base64']
            row['content_storage']='PRIVATE_PC_RECEIPT_NOT_INCLUDED'
    return data
def analyze(root,private=None):
    planraw=(root/'plan.json').read_bytes();plan=json.loads(planraw)
    expected={(r['host'],r['path']):r for r in plan['changes']}
    refs={r['deployed_path']:r for r in plan['reference_files']}
    out=dict(schema='fds.k8s-tool-backup-analysis.v1',hosts=[],files=0,exports=0,
             exported_bytes=0,unchanged_from_plan=0,approved_match=0,approved_different=0,
             private_receipt_check='NOT_INCLUDED' if private is None else 'PASS',
             private_byte_hashes_verified=0,private_receipt_hashes_verified=0,
             metadata_objects=0,full_xattr_names=[],remote_backup='NOT_CREATED',
             runtime_restore='NOT_RUN',backup_readiness='NOT_ESTABLISHED')
    seen=set();xnames=set()
    for folder in sorted((root/'receipts').iterdir()):
        p=json.loads((folder/'projection.json').read_bytes());data=p['projection']
        inv=json.loads((folder/'invocation.json').read_bytes())
        assert inv['rc']==0 and not (folder/'stderr.txt').read_bytes()
        assert sha((folder/'collector.py').read_bytes())==inv['collector_sha256']
        assert p['source_stdout_sha256']==inv['stdout_sha256'] and inv['plan_sha256']==sha(planraw)
        assert data['status']=='COLLECTED' and data['host']==folder.name
        assert data['remote_write'] is False and data['selinux_enforce']=='1'
        assert len(data['files'])==9 and len(data['parents'])==4
        if private:
            raw=(private/folder.name/'stdout.json').read_bytes()
            assert sha(raw)==inv['stdout_sha256']
            full=json.loads(raw);assert project(full)==data
            out['private_receipt_hashes_verified']+=2
        host=dict(host=data['host'],files=9,exports=0,contexts={},parents=[])
        for row in data['files']+data['parents']:
            assert row['stable_during_read'] and row['acl']['rc']==0
            assert row['metadata']['uid']==row['metadata']['gid']==0
            for key,value in row['xattrs'].items():
                raw=base64.b64decode(value['content_base64'],validate=True)
                assert len(raw)==value['size'] and sha(raw)==value['sha256']
                xnames.add(key)
            out['metadata_objects']+=1
        for row in data['files']:
            key=(data['host'],row['path']);assert key not in seen;seen.add(key)
            assert row['path'] in refs
            item=expected.get(key)
            wanted=item['observed_sha256'] if item else refs[row['path']]['sha256']
            assert row['sha256']==wanted and row['exported']==bool(item)
            out['files']+=1;out['unchanged_from_plan']+=1
            out['approved_match' if row['sha256']==refs[row['path']]['sha256'] else 'approved_different']+=1
            context=base64.b64decode(row['xattrs']['security.selinux']['content_base64']).rstrip(b'\0').decode('ascii')
            host['contexts'][context]=host['contexts'].get(context,0)+1
            if item:
                out['exports']+=1;host['exports']+=1;out['exported_bytes']+=row['metadata']['size']
                if private:
                    original=next(r for r in full['files'] if r['path']==row['path'])
                    raw=base64.b64decode(original['content_base64'],validate=True)
                    copy=(private/folder.name/'bytes'/pathlib.PurePosixPath(row['path']).name).read_bytes()
                    assert raw==copy and sha(raw)==row['sha256'] and len(raw)==row['metadata']['size']
                    compile(raw,row['path'],'exec');out['private_byte_hashes_verified']+=1
        for row in data['parents']:
            host['parents'].append({k:row[k] for k in ('path','metadata','filesystem','acl')})
        out['hosts'].append(host)
    assert (out['files'],out['exports'],out['approved_match'],out['approved_different'])==(45,17,28,17)
    out['full_xattr_names']=sorted(xnames)
    return out
if __name__=='__main__':
    print(json.dumps(analyze(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else None),sort_keys=True,indent=2))
