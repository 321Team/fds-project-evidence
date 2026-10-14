"""Offline verification only: no network, subprocesses or file writes."""
import base64, datetime, hashlib, importlib.util, json, os, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'): ROOT=pathlib.Path('\\\\?\\'+str(ROOT))
H=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_bytes())
def safe(base,name):
    rel=pathlib.PurePosixPath(name)
    assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in name
    return base/name
for line in (ROOT/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
    expected,name=line.split('  ',1);assert H(safe(ROOT,name).read_bytes())==expected,name
binding=load(ROOT/'references/CODE_BINDING.json')
assert binding['merge_sha']=='65ae4fd3b274efc04c3cb686b41cc99fb07383b8'
for name,record in binding['files'].items():
    assert H(safe(ROOT/'references',name).read_bytes())==record['sha256']
spec=importlib.util.spec_from_file_location('approved_compare',ROOT/'references/compare_scan_observations.py')
compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
total_files=total_manifest=0
for case,run,job in [('vulnerability','38553120620',115815618445),('scanner-error','38553393207',115816526113)]:
    folder=ROOT/'cases'/case
    for label in ('before-app','after-app','before-runner','after-runner','original-collection'):
        d=folder/label;receipt=load(d/'receipt.json');assert receipt['rc']==0
        for filename,key in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert H((d/filename).read_bytes())==receipt[key]
    for label in ('before-app','after-app'):
        assert (folder/label/'collector.py').read_bytes()==(ROOT/'references/capture_app_state.py').read_bytes()
    export=load(folder/'original-collection/stdout.json');index={**export['files'],**export['hash_only']}
    for name,item in export['files'].items():
        b=base64.b64decode(item['base64'],validate=True);assert len(b)==item['bytes'] and H(b)==item['sha256']
        assert safe(folder/'raw',name).read_bytes()==b
    claim=base64.b64decode(export['claim']['base64'],validate=True);assert H(claim)==export['claim']['sha256'] and (folder/'raw/claim.json').read_bytes()==claim
    result=load(folder/'raw/result.json');scan=load(folder/'raw/scan/result.json')
    assert json.loads(claim)==result['context']==scan['context']
    assert result['context']['run_id']==run and result['context']['workflow_sha']==binding['merge_sha'] and result['context']['attempt']==1
    assert result['PUSH']==result['DEPLOY']==scan['push']==scan['deploy']=='NOT_EXECUTED'
    assert result['scan_result_sha256']==H((folder/'raw/scan/result.json').read_bytes())
    manifests=0
    for name,item in export['files'].items():
        if name=='SHA256SUMS' or name.endswith('/SHA256SUMS'):
            for line in base64.b64decode(item['base64']).decode().splitlines():
                h,n=line.split('  ',1);rel=pathlib.PurePosixPath(n);assert not rel.is_absolute() and '..' not in rel.parts
                full=(pathlib.PurePosixPath(name).parent/rel).as_posix();assert index[full]['sha256']==h
                if name=='SHA256SUMS':manifests+=1
    assert manifests==export['manifest_matches']
    expected={'transaction-api':(93404160,'218c57b0613dc37e9628745d3ae580886543902714bbb9ab6249b5ac90d1266f'),
              'fds-engine':(74496512,'a8895e245ea2a2f30aa106524bf858020fccc65a12fc543d26f3c09a87f04d1c')}
    for service,(size,h) in expected.items():
        for prefix in ('fixture-inputs/','scan/'):
            item=index[prefix+service+'.oci.tar'];assert item['sha256']==h and item['bytes']==size
    assert not any(k.startswith('scan/fds-engine/') for k in index)
    rc=int((folder/'raw/scan/transaction-api/exit-code.txt').read_text());assert result['scanner_adapter_rc']==rc
    if case=='vulnerability':
        assert rc==10 and scan['IMAGE_SCAN']=='BLOCK' and scan['error_code']=='HIGH_CRITICAL_FINDINGS'
        image=scan['images']['transaction-api'];assert image['counts']=={'HIGH':61,'CRITICAL':3} and image['exit_code']==10
        assert image['report_sha256']==index['scan/transaction-api/report.json']['sha256']==export['report_summary']['source_sha256']
        assert image['counts']==export['report_summary']['counts']
        db=load(folder/'raw/scan/db/result.json');assert scan['db_result_sha256']==H((folder/'raw/scan/db/result.json').read_bytes())
        assert db['DB_PREFLIGHT']=='PASS' and db['download_exit_code']==0 and db['context']==result['context']
        assert db['db_sha256']==index['scan/db/cache/db/trivy.db']['sha256'] and db['metadata_sha256']==H((folder/'raw/scan/db/cache/db/metadata.json').read_bytes())
        dt=lambda x:datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
        assert dt(db['metadata']['UpdatedAt'])<=dt(db['metadata']['DownloadedAt'])<=dt(db['validated_at'])<dt(db['metadata']['NextUpdate'])
    else:
        assert rc==1 and scan['IMAGE_SCAN']=='FAIL' and scan['error_code']=='SCANNER_EXECUTION_ERROR' and scan['images']=={}
        assert scan['db_mode']=='INTENTIONAL_EMPTY_CACHE_NO_DOWNLOAD'
        inv=load(folder/'raw/scan/transaction-api/scanner-invocation.json');raw=(folder/'raw/scan/transaction-api/scanner-stderr.log').read_bytes()
        assert inv['outcome']=='COMPLETED' and inv['exit_code']==1 and inv['stderr_sha256']==H(raw)
        assert b'--skip-db-update cannot be specified on the first run' in raw and len(raw)<1024**2
        assert not any(k.startswith('scan/db/') or k.endswith('/report.json') or k.endswith('/trivy.db') for k in index)
    api=load(folder/'github-run.json');jobs=load(folder/'github-jobs.json')['jobs']
    assert str(api['id'])==run and api['head_sha']==binding['merge_sha'] and api['run_attempt']==1 and api['conclusion']=='failure'
    assert len(jobs)==1 and jobs[0]['id']==job and jobs[0]['runner_id']==2 and jobs[0]['runner_name']=='cicd-runner01' and jobs[0]['conclusion']=='failure'
    computed=compare.compare(load(folder/'before-app/stdout.json'),load(folder/'after-app/stdout.json'),result,run,binding['merge_sha'],case)
    saved=load(folder/'VERIFIED.json');assert saved['comparison']==computed and saved['classification']==result['NEGATIVE_CASE']=='EXPECTED_FAILURE_OBSERVED'
    runner=load(folder/'after-runner/stdout.json');assert runner['readiness']=='READY' and runner['process_counts'].get('Runner.Worker',0)==0
    total_files+=len(export['files'])+1;total_manifest+=manifests
assert (total_files,total_manifest)==(21,56)
print(json.dumps({'OFFLINE_EVIDENCE':'PASS','received_original_files':total_files,'root_manifest_references':total_manifest,'cases':2,'IMAGE_PRESERVATION':'OBSERVED_UNCHANGED','new_runtime':False,'hash_only_current_server_revalidation':False}))
