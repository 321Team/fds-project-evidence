import hashlib,json,pathlib,sys
def analyze(root):
    r=pathlib.Path(root); inv=json.loads((r/'invocation.json').read_bytes())
    for name,field in [('collector.py','collector_sha256'),('stdout.json','stdout_sha256')]:
        assert hashlib.sha256((r/name).read_bytes()).hexdigest()==inv[field],name
    assert inv['rc']==0 and (r/'stderr.txt').read_bytes()==b''
    d=json.loads((r/'stdout.json').read_bytes());qs=d['queries']
    assert len(qs)==3 and all(q['rc']==0 and q['stderr_bytes']==0 for q in qs)
    assert d['host']=='k8s-control01' and d['status']=='COLLECTED' and d['deployment_unchanged']
    assert qs[0]['projection']==qs[2]['projection']
    dep=qs[0]['projection'];pods=qs[1]['projection']['items'];assert len(pods)==1
    pod=pods[0];assert dep['spec']==pod['spec']
    env=dep['spec']['containers'][0]['admin_env']
    refs={x['name']:x['valueFrom']['secretKeyRef'] for x in env}
    assert set(refs)=={'GF_SECURITY_ADMIN_USER','GF_SECURITY_ADMIN_PASSWORD'}
    assert all(not x['literal_present_value_omitted'] for x in env)
    assert refs['GF_SECURITY_ADMIN_USER']['name']==refs['GF_SECURITY_ADMIN_PASSWORD']['name']=='grafana-admin-credentials'
    assert refs['GF_SECURITY_ADMIN_USER']['key']=='admin-user'
    assert refs['GF_SECURITY_ADMIN_PASSWORD']['key']=='admin-password'
    assert pod['status']['containers'][0]['ready'] is True
    return dict(status='REFERENCE_METADATA_MATCH',receipt_hashes_matched=2,query_rc_zero=3,
        started_at_kst=d['started_at_kst'],finished_at_kst=d['finished_at_kst'],
        deployment=dep['metadata'],pod=pod['metadata'],admin_references=refs,
        pod_ready=True,pod_restart_count=pod['status']['containers'][0]['restartCount'],
        secret_object_values_and_existence='NOT_QUERIED',active_application_password='NOT_VERIFIED',
        human_custodian_rotation_audit='NOT_VERIFIED',access_exclusivity='NOT_VERIFIED',
        runtime_access_test='NOT_RUN',replicaset_owner_chain='NOT_QUERIED')
if __name__=='__main__':print(json.dumps(analyze(sys.argv[1]),ensure_ascii=False,sort_keys=True,indent=2))
