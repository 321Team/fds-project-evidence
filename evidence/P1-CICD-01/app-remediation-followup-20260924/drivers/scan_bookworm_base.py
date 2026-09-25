"""Local candidate-only scan; no production context or approval is fabricated."""
import hashlib, json, os, pathlib, subprocess, sys, tarfile
from datetime import datetime, timezone

root = pathlib.Path(__file__).resolve().parent
evidence = root / 'bookworm-scan'
evidence.mkdir(mode=0o700)
binary = root / 'bin/trivy'
expected = 'd89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(binary) == expected
consumer = root.parent / 'trivy-followup/cicd-snapshot/tools/trivy'
sys.path.insert(0, str(consumer))
from oci_archive import inspect_archive
from prepare_db import validate_metadata

archive = root / 'bookworm/supply/base.oci.tar'
identity = inspect_archive(archive)
assert identity['manifest_digest'] == 'sha256:1aaa65a85fda306ffb8b910824d4e93bdce61e212c7e87168123ea3073b41a1a'
layout = evidence / 'layout'
layout.mkdir(mode=0o700)
with tarfile.open(archive, 'r:') as source:
    source.extractall(layout, filter='data')
cache = root / 'base-scan/cache'
prior = json.loads((root / 'base-scan/result.json').read_text())
assert sha(cache/'db/trivy.db') == prior['db_sha256']
assert sha(cache/'db/metadata.json') == prior['metadata_sha256']
(evidence / 'empty.yaml').write_text('{}\n')
(evidence / 'empty.ignore').write_text('')
env = {k: v for k, v in os.environ.items() if k in ('PATH','HOME','HTTPS_PROXY','HTTP_PROXY','NO_PROXY','https_proxy','http_proxy','no_proxy')}
result = {'scope':'LOCAL_BASE_COMPARISON_SAME_DB','host':'Codex Linux','started_at':datetime.now(timezone.utc).isoformat(),'binary_sha256':expected,'base_identity':identity,'APP_IMAGE_SCAN':'NOT_RUN','DELIVERY_GATE':'NOT_VERIFIED','BASE_SCAN':'NOT_RUN'}
def run(label, argv, timeout):
    (evidence / (label + '-argv.json')).write_text(json.dumps(argv,indent=2)+'\n')
    with (evidence / (label + '.log')).open('wb') as log:
        completed = subprocess.run(argv,cwd=evidence,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
    result[label + '_exit_code'] = completed.returncode
    return completed.returncode
try:
    argv=[str(binary),'image','--cache-dir',str(cache),'--db-repository','ghcr.io/aquasecurity/trivy-db:2','--download-db-only','--skip-version-check','--no-progress','--timeout','5m']
    result['db_reused_from'] = str(root / 'base-scan/result.json')
    metadata=cache/'db/metadata.json'; db=cache/'db/trivy.db'
    validate_metadata(json.loads(metadata.read_bytes()),datetime.now(timezone.utc))
    result['DB_PREFLIGHT']='PASS'
    result['db_sha256']=sha(db); result['metadata_sha256']=sha(metadata)
    result['metadata']=json.loads(metadata.read_bytes())
    argv=[str(binary),'image','--input',str(layout),'--cache-dir',str(cache),'--config',str(evidence/'empty.yaml'),'--ignorefile',str(evidence/'empty.ignore'),'--ignore-unfixed=false','--scanners','vuln','--pkg-types','os,library','--list-all-pkgs','--skip-db-update','--skip-java-db-update','--offline-scan','--skip-version-check','--severity','HIGH,CRITICAL','--exit-code','10','--format','json','--output',str(evidence/'report.json'),'--no-progress','--timeout','10m']
    rc=run('scan',argv,630)
    assert rc in (0,10),'SCANNER_ERROR'
    report=json.loads((evidence/'report.json').read_bytes())
    assert report['SchemaVersion']==2 and report['Trivy']['Version']=='0.74.0'
    assert report['ArtifactType']=='container_image'
    assert report['Metadata']['ImageID']==identity['config_digest']
    assert report['Metadata']['DiffIDs']==identity['diff_ids']
    assert any(x.get('Class')=='os-pkgs' and x.get('Packages') for x in report['Results']), 'NO_OS_INVENTORY'
    findings=[v for x in report['Results'] for v in x.get('Vulnerabilities',[])]
    assert all(v['Severity'] in ('HIGH','CRITICAL') for v in findings)
    counts={s:sum(v['Severity']==s for v in findings) for s in ('HIGH','CRITICAL')}
    assert (rc==10)==bool(findings),'EXIT_COUNT_MISMATCH'
    assert sha(db)==result['db_sha256'] and sha(metadata)==result['metadata_sha256']
    validate_metadata(json.loads(metadata.read_bytes()),datetime.now(timezone.utc))
    assert sha(binary)==expected and sha(archive)==identity['archive_sha256']
    result.update(BASE_SCAN='BLOCK' if rc==10 else 'PASS',counts=counts,unique_cves=len({v['VulnerabilityID'] for v in findings}),report_sha256=sha(evidence/'report.json'))
except Exception as error:
    result.update(BASE_SCAN='ERROR',error_type=type(error).__name__,error=str(error))
finally:
    result['finished_at']=datetime.now(timezone.utc).isoformat()
    (evidence/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
