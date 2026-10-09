"""Offline replay only; metadata collection is distinct from deployment approval."""
import collections,hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1])
sha=lambda b:hashlib.sha256(b).hexdigest()
prior=json.loads((root/'inputs/COMPARISON-0000.json').read_bytes())
baseline={(h['host'],f['path']):f for h in prior['node_code_comparison'] for f in h['files']}
assert len(baseline)==45
receipts={};verified=0
for d in sorted((root/'receipts').iterdir()):
    inv=json.loads((d/'invocation.json').read_bytes());raw=(d/'stdout.json').read_bytes()
    assert inv['rc']==0 and not (d/'stderr.txt').read_bytes(),str(d)
    assert sha(raw)==inv['stdout_sha256'] and sha((d/'collector.py').read_bytes())==inv['collector_sha256'],str(d)
    data=json.loads(raw);kind='metadata' if data['schema']=='fds.k8s-tool-metadata.v1' else 'context'
    assert (kind,data['host']) not in receipts
    receipts[kind,data['host']]=data;verified+=2
assert len(receipts)==10
hosts=[];allrows=[]
for host in sorted({k[0] for k in baseline}):
    meta=receipts['metadata',host];ctx=receipts['context',host]
    defaults={r['path']:r for r in ctx['queries']};assert len(defaults)==9
    rows=[]
    for r in meta['files']:
        key=(host,r['path']);b=baseline[key];c=defaults[r['path']]
        assert c['rc']==0 and not c['stderr']
        assert r['status']=='COLLECTED' and r['stable_during_read'] and r['acl']['rc']==0
        actual=r['xattrs']['security.selinux']['value'];expected=c['stdout'].strip()
        assert len(actual.split(':'))>=4 and len(expected.split(':'))>=4
        row={'host':host,'path':r['path'],'sha256':r['sha256'],
             'same_bytes_as_0000':r['sha256']==b['observed_sha256'],
             'approved_source_match':r['sha256']==b['expected_sha256'],
             'metadata':r['metadata'],'observed_selinux_context':actual,'policy_default_context':expected,
             'full_context_matches_policy_default':actual==expected,
             'type_matches_policy_default':actual.split(':')[2]==expected.split(':')[2],
             'acl_access_xattr':r['xattrs']['system.posix_acl_access']['status'],
             'capability_xattr':r['xattrs']['security.capability']['status'],'numeric_acl':r['acl']['stdout']}
        rows.append(row)
    assert len(rows)==9 and len({r['path'] for r in rows})==9
    hosts.append({'host':host,'metadata_interval_kst':[meta['started_at_kst'],meta['finished_at_kst']],
                  'policy_query_interval_kst':[ctx['started_at_kst'],ctx['finished_at_kst']],
                  'selinux_enforce':meta['selinux_enforce'],'parent_count':len(meta['parents']),
                  'parents_on_readonly_filesystem':sum(p['filesystem_readonly'] for p in meta['parents']),
                  'match':sum(r['approved_source_match'] for r in rows),
                  'different':sum(not r['approved_source_match'] for r in rows),
                  'type_mismatch':sum(not r['type_matches_policy_default'] for r in rows)})
    allrows.extend(rows)
assert {(r['host'],r['path']) for r in allrows}==set(baseline)
result={'schema':'fds.k8s-tool-metadata-analysis.v1','receipt_file_hashes_verified':verified,
        'files':45,'same_bytes_as_0000':sum(r['same_bytes_as_0000'] for r in allrows),
        'approved_source_match':sum(r['approved_source_match'] for r in allrows),
        'approved_source_different':sum(not r['approved_source_match'] for r in allrows),
        'full_context_mismatch':sum(not r['full_context_matches_policy_default'] for r in allrows),
        'type_mismatch':sum(not r['type_matches_policy_default'] for r in allrows),
        'hosts':hosts,'rows':allrows,
        'interpretation':'Snapshots and local policy defaults only; not approved replacement metadata, backup verification, execution preflight, AVC result or functional validation.',
        'backup':'NOT_CREATED','concurrent_invocation_exclusion':'NOT_ESTABLISHED',
        'deployment':'NOT_RUN','runtime_go':'NOT_GRANTED','review':'PENDING'}
print(json.dumps(result,indent=2,ensure_ascii=False))
