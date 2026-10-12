"""Prepare non-executable next-stage observations and an unchanged source bundle."""
import datetime, hashlib, json, subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
repo=ROOT/'deliverables/p1-preapply-until-0930-20261012/other-work/checkouts/infra-cicd'
sha='2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()==sha
names=['deploy_native_probe.py','deploy_cp1_access.py','deploy_binding.py','deploy_credential.py',
       'deploy_transport.py','deploy_adapter.py','delivery_gate.py']
bundle={'schema':'P1-CICD-native-probe-source-1','source_sha':sha,'files':{}}
manifest=[]
for name in names:
    path='tools/delivery/'+name
    raw=subprocess.check_output(['git','show',sha+':'+path],cwd=repo)
    blob=subprocess.check_output(['git','rev-parse',sha+':'+path],cwd=repo).decode().strip()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
    compile(raw,path,'exec')
    bundle['files'][name]={'git_blob':blob,'content':raw.decode('utf-8')}
    manifest.append({'path':path,'git_blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
raw=(json.dumps(bundle,ensure_ascii=True,sort_keys=True,separators=(',',':'))+'\n').encode()
assert len(raw)<1024*1024 and raw.count(b'\n')==1
(P/'native-source-2d8a14c.json').write_bytes(raw)
meta={'source_sha':sha,'files':manifest,'bundle_sha256':hashlib.sha256(raw).hexdigest(),
      'bytes':len(raw),'remote_staging':'NOT_PERFORMED','token_issued':False,'deploy':'NOT_EXECUTED'}
(P/'SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
auth=json.loads((P/'cp1-existing-auth/stdout.json').read_text())
assert auth['api_get']['rc']==0 and auth['mutation'] is False and auth['token_issued'] is False
base=json.loads((P.parent/'p1-delivery-runner-20261013/INPUTS.observed.json').read_text())
draft={'schema':'P1-CICD-preparation-observations-2','template_only':True,'runtime_authorized':False,
       'workflow_sha':sha,'app_source_sha':base['source_sha'],
       'cp1_existing_auth':{'verified_at_utc':auth['finished_at_utc'],'host':auth['host'],'user':auth['user'],
            'controller_key_path':'/home/server01_ansible/.ssh/id_ed25519',
            'ca_path':auth['paths'][0]['path'],'ca_sha256':auth['ca_sha256'],'sa_uid':auth['api_get']['metadata']['uid'],
            'scope':'SSH + existing-user SA GET only; native broker, TokenRequest, TokenReview and Runner SA consumption remain unexecuted'},
       'runner_existing_auth_reference':'evidence PR208 delivery-inputs/03:13 Runner receipt; key p1_ansible_ed25519',
       'target_observation_reference':'p1-delivery-runner-20261013/cluster; earlier 03:10 observation, refresh before Deploy',
       'targets_observed':base['targets_observed'],
       'new_push_receipt':None,'deploy_request_id':None,'deploy_window':None,'deploy_approval_reference':None,
       'rollback_approved':False,
       'rollback_limit':'current previous digests restore the business-port /metrics exposure; no automatic security acceptance',
       'source_bundle':meta,'phase2_included':False}
(P/'DEPLOY_PREPARATION.pending.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[]
for d in sorted(P.glob('oid03-inventory-*')):
    x=json.loads((d/'stdout.json').read_text());r=json.loads((d/'receipt.json').read_text())
    assert r['rc']==0 and x['mutation'] is False and x['network_fetch'] is False
    assert not x['selected_rpm_cache']['bounded']
    packages={}
    for q in x['queries']:
        if q['name'].startswith('rpm-owner-') and q.get('rc')==0:
            parts=q['stdout'].strip().split('\t');assert len(parts)==4
            packages[parts[0]]={'version_release':parts[1],'arch':parts[2],'sourcerpm':parts[3]}
    units=next(q for q in x['queries'] if q['name']=='boot-units')
    assert units['rc']==0
    unit_rows=[]
    for block in units['stdout'].strip().split('\n\n'):
        values=dict(line.split('=',1) for line in block.splitlines() if '=' in line)
        unit_rows.append({k:values.get(k) for k in ('Id','LoadState','UnitFileState','ActiveState','SubState')})
    rows.append({'host':x['host'],'observed_at_utc':x['started_at_utc'],'boot_id':x['boot_id'],
        'packages':packages,'crictl':next(b for b in x['binaries'] if b['name']=='crictl'),
        'matching_cache_packages':len(x['selected_rpm_cache']['matches']),
        'cache_files_visited':x['selected_rpm_cache']['visited_files'],'units':unit_rows,
        'receipt':d.name+'/receipt.json','raw':d.name+'/stdout.json'})
assert len(rows)==6
summary={'schema':'P1-OID03-current-inventory-summary-1','hosts':rows,
    'current_installation_observed':True,'package_supply_archive_verified':False,
    'original_provenance_verified':False,'oid03_path_approved':False,
    'reboot_executed':False,'continuous_boot_protection_verified':False,
    'limits':['The named cache and filename prefixes are not every possible supply store.',
              'RPM database ownership/version is not verification of original package or binary bytes.',
              'Unit state/dependencies are not a continuous boot-time protection observation.']}
(P/'OID03_INVENTORY_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'bundle_sha256':meta['bundle_sha256'],'source_files':len(names),'cp1_read':'PASS','oid_hosts':len(rows),
    'rpm_cache_matches':[r['matching_cache_packages'] for r in rows],
    'crictl':{r['host']:r['crictl']['path'] for r in rows}}))
