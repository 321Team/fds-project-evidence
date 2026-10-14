"""Recheck received original bytes, GitHub identity and reviewed offline comparison."""
import base64,datetime,hashlib,importlib.util,json,pathlib,sys
OUT=pathlib.Path(__file__).resolve().parent
REPO=OUT.parent.parent/'phase1-work-20261013/cicd-scan-negative-20261014'
SHA='65ae4fd3b274efc04c3cb686b41cc99fb07383b8'
case=sys.argv[1];assert case in ('vulnerability','scanner-error')
load=lambda p:json.loads(p.read_bytes())
h=lambda raw:hashlib.sha256(raw).hexdigest()
originals=load(OUT/(case+'-originals/stdout.json'))
raw={}
for name,v in originals['files'].items():
    pure=pathlib.PurePosixPath(name);assert not pure.is_absolute() and '..' not in pure.parts
    b=base64.b64decode(v['base64'],validate=True);assert len(b)==v['bytes'] and h(b)==v['sha256'];raw[name]=b
index={**originals['files'],**originals['hash_only']}
count=0
for name,b in raw.items():
    if name=='SHA256SUMS' or name.endswith('/SHA256SUMS'):
        for line in b.decode().splitlines():
            expected,rel=line.split('  ',1);p=pathlib.PurePosixPath(rel);assert not p.is_absolute() and '..' not in p.parts
            full=(pathlib.PurePosixPath(name).parent/p).as_posix();assert index[full]['sha256']==expected
            if name=='SHA256SUMS':count+=1
assert count==originals['manifest_matches']
result=json.loads(raw['result.json']);scan=json.loads(raw['scan/result.json']);context=result['context'];run=context['run_id']
assert originals['run_id']==run and originals['case']==result['case']==case
assert context['workflow_sha']==SHA and context['attempt']==1 and scan['context']==context
assert result['NEGATIVE_CASE']=='EXPECTED_FAILURE_OBSERVED' and result['SCAN_NEGATIVE_WORKFLOW']=='FAIL'
assert result['PUSH']==result['DEPLOY']==scan['push']==scan['deploy']=='NOT_EXECUTED'
assert result['scan_result_sha256']==h(raw['scan/result.json'])
claim=base64.b64decode(originals['claim']['base64'],validate=True);assert h(claim)==originals['claim']['sha256'] and json.loads(claim)==context
for service,fixture in result['fixture_hashes'].items():
    for prefix in ('fixture-inputs/','scan/'):
        v=index[prefix+service+'.oci.tar'];assert v['sha256']==fixture['sha256'] and v['bytes']==fixture['bytes']
assert not any(k.startswith('scan/fds-engine/') for k in index)
rc=int(raw['scan/transaction-api/exit-code.txt']);assert result['scanner_adapter_rc']==rc
details={}
if case=='vulnerability':
    assert rc==10 and result['error_code']==scan['error_code']=='HIGH_CRITICAL_FINDINGS' and scan['IMAGE_SCAN']=='BLOCK'
    assert set(scan['images'])=={'transaction-api'}
    image=scan['images']['transaction-api'];assert image['exit_code']==10 and image['scan']=='BLOCK'
    assert image['report_sha256']==index['scan/transaction-api/report.json']['sha256']==originals['report_summary']['source_sha256']
    assert image['counts']==originals['report_summary']['counts'] and sum(image['counts'].values())>0
    db=json.loads(raw['scan/db/result.json']);assert db['DB_PREFLIGHT']=='PASS' and db['download_exit_code']==0
    assert scan['db_result_sha256']==h(raw['scan/db/result.json'])
    assert db['db_sha256']==index['scan/db/cache/db/trivy.db']['sha256']
    assert db['metadata_sha256']==h(raw['scan/db/cache/db/metadata.json'])
    dt=lambda t:datetime.datetime.fromisoformat(t.replace('Z','+00:00'))
    meta=db['metadata'];assert dt(meta['UpdatedAt'])<=dt(meta['DownloadedAt'])<=dt(db['validated_at'])<dt(meta['NextUpdate'])
    assert dt(db['started_at'])<=dt(meta['DownloadedAt'])<=dt(db['finished_at'])
    details={'counts':image['counts'],'db_fresh':True,'report_raw':'HASH_ONLY'}
else:
    assert rc==1 and result['error_code']==scan['error_code']=='SCANNER_EXECUTION_ERROR' and scan['IMAGE_SCAN']=='FAIL'
    assert scan['images']=={} and scan['db_mode']=='INTENTIONAL_EMPTY_CACHE_NO_DOWNLOAD'
    inv=json.loads(raw['scan/transaction-api/scanner-invocation.json']);stderr=raw['scan/transaction-api/scanner-stderr.log']
    assert inv['outcome']=='COMPLETED' and inv['exit_code']==1 and inv['stderr_sha256']==h(stderr)
    assert len(stderr)<1024**2 and b'--skip-db-update cannot be specified on the first run' in stderr
    assert not any(k.startswith('scan/db/') or k.endswith('/report.json') or k.endswith('/trivy.db') for k in index)
    details={'missing_db_error_verified':True,'stderr_sha256':h(stderr),'stderr_bytes':len(stderr)}
for label in (case+'-originals',case+'-before-app',case+'-after-app',case+'-after-runner'):
    receipt=load(OUT/label/'receipt.json');assert receipt['rc']==0
    for f,key in [('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256'),('collector.py','source_sha256')]:assert h((OUT/label/f).read_bytes())==receipt[key]
api=load(OUT/(case+'-run.json'));jobs=load(OUT/(case+'-jobs.json'))['jobs']
assert str(api['id'])==run and api['head_sha']==SHA and api['run_attempt']==1 and api['conclusion']=='failure' and api['event']=='workflow_dispatch'
assert len(jobs)==1 and jobs[0]['conclusion']=='failure' and jobs[0]['runner_id']==2 and jobs[0]['runner_name']=='cicd-runner01'
after_runner=load(OUT/(case+'-after-runner/stdout.json'));assert after_runner['readiness']=='READY'
sp=importlib.util.spec_from_file_location('cmp',REPO/'tools/trivy/compare_scan_observations.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
comparison=m.compare(load(OUT/(case+'-before-app/stdout.json')),load(OUT/(case+'-after-app/stdout.json')),result,run,SHA,case)
dst=OUT/(case+'-raw');dst.mkdir(exist_ok=False)
for name,b in raw.items():
    p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
(dst/'claim.json').write_bytes(claim)
summary={k:v for k,v in originals.items() if k not in ('files','claim')}
summary['files']={k:{a:b for a,b in v.items() if a!='base64'} for k,v in originals['files'].items()}
(OUT/(case+'-original-index.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
verified={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case':case,'run_id':run,'job_id':jobs[0]['id'],'workflow_sha':SHA,
          'github_conclusion':'failure','classification':'EXPECTED_FAILURE_OBSERVED','scanner_rc':rc,'program_rc':1,'IMAGE_PRESERVATION':comparison['IMAGE_PRESERVATION'],
          'raw_files_received':len(raw)+1,'root_manifest_entries_verified':count,'comparison':comparison,'worker_count':after_runner['process_counts'].get('Runner.Worker',0),
          'push':'NOT_EXECUTED','deploy':'NOT_EXECUTED','second_image_scan':'NOT_SCANNED',**details}
(OUT/('VERIFIED-'+case+'.json')).write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(verified,ensure_ascii=False,indent=2))
