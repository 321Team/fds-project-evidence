"""Bounded fresh recheck after a local DB re-use hash mismatch."""
import hashlib, json, os, pathlib, subprocess, sys, tarfile
from datetime import datetime, timezone

root=pathlib.Path(__file__).resolve().parent
out=root/'paired-rescan'
out.mkdir(mode=0o700)
cache=out/'cache';cache.mkdir(mode=0o700)
binary=root/'bin/trivy'
expected='d89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791'
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
sys.path.insert(0,str(root.parent/'trivy-followup/cicd-snapshot/tools/trivy'))
from oci_archive import inspect_archive
from prepare_db import validate_metadata
env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','HTTPS_PROXY','HTTP_PROXY','NO_PROXY','https_proxy','http_proxy','no_proxy')}
result={'scope':'LOCAL_BASE_COMPARISON','started_at':datetime.now(timezone.utc).isoformat(),'status':'ERROR','binary_sha256':expected,'images':{},'APP_IMAGE_SCAN':'NOT_RUN','DELIVERY_GATE':'NOT_VERIFIED'}
def run(label,argv,timeout):
    (out/(label+'-argv.json')).write_text(json.dumps(argv,indent=2)+'\n')
    with (out/(label+'.log')).open('wb') as log:
        return subprocess.run(argv,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
try:
    assert sha(binary)==expected,'BINARY_HASH_MISMATCH'
    rc=run('download',[str(binary),'image','--cache-dir',str(cache),'--db-repository','ghcr.io/aquasecurity/trivy-db:2','--download-db-only','--skip-version-check','--no-progress','--timeout','5m'],330)
    assert rc==0,'DB_DOWNLOAD_FAILED'
    db=cache/'db/trivy.db';metadata=cache/'db/metadata.json'
    db_hash=sha(db);meta_hash=sha(metadata)
    db.chmod(0o444);metadata.chmod(0o444)
    result.update(db_sha256=db_hash,metadata_sha256=meta_hash,metadata=json.loads(metadata.read_bytes()))
    archives={'trixie':root.parent/'app-remediation/supply/base.oci.tar','bookworm':root/'bookworm/supply/base.oci.tar'}
    for name,archive in archives.items():
        assert sha(db)==db_hash and sha(metadata)==meta_hash,'DB_CHANGED_BEFORE_'+name
        validate_metadata(json.loads(metadata.read_bytes()),datetime.now(timezone.utc))
        identity=inspect_archive(archive)
        folder=out/name;folder.mkdir();layout=folder/'layout';layout.mkdir()
        with tarfile.open(archive,'r:') as package:package.extractall(layout,filter='data')
        config=folder/'empty.yaml';config.write_text('{}\n')
        ignore=folder/'empty.ignore';ignore.write_text('')
        report_path=folder/'report.json'
        rc=run(name,[str(binary),'image','--input',str(layout),'--cache-dir',str(cache),'--config',str(config),'--ignorefile',str(ignore),'--ignore-unfixed=false','--scanners','vuln','--pkg-types','os,library','--list-all-pkgs','--skip-db-update','--skip-java-db-update','--offline-scan','--skip-version-check','--severity','HIGH,CRITICAL','--exit-code','10','--format','json','--output',str(report_path),'--no-progress','--timeout','10m'],630)
        assert rc in (0,10),'SCANNER_ERROR_'+name
        report=json.loads(report_path.read_bytes())
        assert report['SchemaVersion']==2 and report['Trivy']['Version']=='0.74.0' and report['ArtifactType']=='container_image'
        assert report['Metadata']['ImageID']==identity['config_digest'] and report['Metadata']['DiffIDs']==identity['diff_ids']
        assert any(x.get('Class')=='os-pkgs' and x.get('Packages') for x in report['Results'])
        findings=[v for x in report['Results'] for v in x.get('Vulnerabilities',[])]
        assert all(v['Severity'] in ('HIGH','CRITICAL') for v in findings)
        assert (rc==10)==bool(findings)
        assert sha(db)==db_hash and sha(metadata)==meta_hash,'DB_CHANGED_AFTER_'+name
        assert sha(binary)==expected and sha(archive)==identity['archive_sha256']
        validate_metadata(json.loads(metadata.read_bytes()),datetime.now(timezone.utc))
        result['images'][name]={'status':'BLOCK' if rc==10 else 'PASS','exit_code':rc,'counts':{s:sum(v['Severity']==s for v in findings) for s in ('HIGH','CRITICAL')},'unique_cves':len({v['VulnerabilityID'] for v in findings}),'report_sha256':sha(report_path),'identity':identity}
        print(name,json.dumps(result['images'][name]),flush=True)
    result['status']='COMPARISON_COMPLETE'
except Exception as error:
    result.update(error_type=type(error).__name__,error=str(error))
finally:
    result['finished_at']=datetime.now(timezone.utc).isoformat()
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
