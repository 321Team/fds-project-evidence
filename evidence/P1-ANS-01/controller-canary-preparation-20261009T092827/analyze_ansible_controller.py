"""Offline checks of controller receipt against pinned Git blob hashes."""
import hashlib,json,pathlib,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
def analyze(root):
    inv=json.loads((root/'invocation.json').read_bytes())
    assert inv['rc']==0 and not (root/'stderr.txt').read_bytes()
    assert sha((root/'collector.py').read_bytes())==inv['collector_sha256']
    assert sha((root/'stdout.json').read_bytes())==inv['stdout_sha256']
    data=json.loads((root/'stdout.json').read_bytes())
    expected=json.loads((root/'source-inputs.json').read_bytes())
    assert data['status']=='COLLECTED' and data['host']=='ansible01' and data['user']=='server01_ansible'
    assert data['remote_write'] is False and data['managed_host_connections']==0
    out=dict(schema='fds.ansible-controller-comparison.v1',receipt_hashes_verified=2,checkouts=[],
             git_blob_matches=0,expected_absent=0,cli_runtime_version='NOT_RUN',
             managed_host_connections=0,canary_apply='NOT_RUN',engine_switch='NOT_RUN')
    for c in data['checkouts']:
        ref=expected[c['path']];head=c['queries'][0]['stdout'].strip()
        assert head==ref['commit']==c['head_after']
        assert [x['rc'] for x in c['queries']]==[0,0,0,0]
        assert c['queries'][1]['stdout']=='' and c['queries'][2]['stdout'].strip()=='false'
        row=dict(path=c['path'],head=head,tracked_clean=True,untracked='NOT_QUERIED',matched=0,absent=[])
        for item in c['inputs']:
            name=item['relative_path'];wanted=ref['inputs'][name]
            if wanted is None:
                assert item['status']=='ABSENT';out['expected_absent']+=1;row['absent'].append(name)
            else:
                assert item['status']=='COLLECTED' and item['stable'] and item['matches_checkout_commit']
                assert item['sha256']==item['git_blob_sha256']==wanted
                out['git_blob_matches']+=1;row['matched']+=1
        out['checkouts'].append(row)
    assert (out['git_blob_matches'],out['expected_absent'])==(22,2)
    assert len(data['engine_metadata'])==6
    cli=data['engine_metadata'][:4]
    expected_interpreter='/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin/python'
    assert all(x['first_line']=='#!'+expected_interpreter for x in cli)
    assert data['engine_metadata'][4]['declarations']==['version = 3.12.14']
    assert data['engine_metadata'][5]['declarations']==['Name: ansible-core','Version: 2.21.3']
    out['candidate_installation_declaration']=dict(core='2.21.3',python='3.12.14',cli_shebangs=4)
    for item in data['access_metadata'][:2]:
        assert item['metadata']['mode']=='0o600' and item['metadata']['uid']==1000 and not item['is_symlink']
    out['key_known_hosts']='METADATA_ONLY_NOT_CONTENT_OR_AUTHENTICATION'
    out['new_scope_go']='NOT_GRANTED'
    return out
if __name__=='__main__':print(json.dumps(analyze(pathlib.Path(sys.argv[1])),sort_keys=True,indent=2))
