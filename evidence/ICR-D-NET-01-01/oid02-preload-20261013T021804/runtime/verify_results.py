"""Read-only verification of received OID receipts. No SSH or server mutation."""
from pathlib import Path
import hashlib,json,sys
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=[]
for p in sorted(R.glob('*/receipt.json')):
 d=read(p);assert d['rc']==0,p
 for n,k in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(p.parent/n)==d[k],str(p.parent/n)
 out=read(p.parent/'stdout.json');assert out['status'] in ['STEP_VERIFIED','TRANSFER_VERIFIED','CLUSTER_BINDING_VERIFIED'],p
 receipts.append({'path':p.parent.name,'rc':d['rc'],'status':out['status']})
assert len(receipts)==44,len(receipts)
auth=read(R/'USER_AUTHORIZATION.json');assert auth['current_cache_adopted'] and auth['maximum_image_node_imports']==8
exports={n:read(R/('export-k8s-control01-'+n)/'stdout.json') for n in ['kube-controllers','coredns']}
imports=[]
for p in sorted(R.glob('import-*/stdout.json')):
 d=read(p);im=d['archive']['image'];e=exports[im]
 assert d['archive']==e['archive']
 assert all(k in d['refs_after'] and d['refs_after'][k]==v for k,v in d['refs_before'].items())
 assert len(d['store_content_verified'])==d['archive']['blob_count']
 assert all(x['digest']=='sha256:'+d['archive']['members']['blobs/sha256/'+x['digest'].split(':')[1]]['sha256'] and x['size']==d['archive']['members']['blobs/sha256/'+x['digest'].split(':')[1]]['size'] for x in d['store_content_verified'])
 imports.append({'host':d['host'],'image':im,'started_at_utc':d['started_at_utc'],'finished_at_utc':d['finished_at_utc'],'added_refs':d['added_refs'],'archive_sha256':d['archive']['archive_sha256'],'content_blobs_verified':len(d['store_content_verified'])})
assert len(imports)==8 and len({(x['host'],x['image']) for x in imports})==8
before=read(R/'cluster-before/stdout.json');final=read(R/'cluster-final/stdout.json')
for p in R.glob('cluster-*/stdout.json'):
 d=read(p);assert sorted(d['pods'],key=lambda x:x['uid'])==sorted(before['pods'],key=lambda x:x['uid']);assert d['deployments']==before['deployments'];assert d['nodes']==before['nodes']
finals=[read(p) for p in sorted(R.glob('final-*/stdout.json'))];assert len(finals)==6
archives=[]
for n,e in exports.items():
 a=e['archive'];assert e['refs_before']==e['refs_after']
 copies=[]
 for d in finals:
  for f in d['private_files']:
   if f['name']==n+'-linux-amd64.oci.tar':
    assert f['sha256']==a['archive_sha256'] and f['size']==a['archive_size_bytes'] and f['mode']=='0600';copies.append(d['host'])
 assert len(copies)==(6 if n=='kube-controllers' else 4)
 relay=read(R/'source-to-relay/stdout.json');rr=next(x for x in relay['commands'] if x['path'].endswith(n+'-linux-amd64.oci.tar'));assert rr['sha256']==a['archive_sha256'] and rr['size']==a['archive_size_bytes']
 archives.append({'image':n,'sha256':a['archive_sha256'],'size':a['archive_size_bytes'],'blob_count':a['blob_count'],'layer_count':a['layer_count'],'top_digest':a['top_digest'],'manifest_digest':a['manifest_digest'],'hosts':copies,'private_path':'/root/p1-oid02-20261013-r1/'+n+'-linux-amd64.oci.tar','relay_path':rr['path']})
result={'status':'OID02_EXPORT2_IMPORT8_VERIFIED','receipt_count':len(receipts),'receipts':receipts,'authorization':auth,'archives':archives,'imports':imports,'node_ready':6,'system_pod_ready':3,'app_pod_ready':6,'pods_uid_node_restarts_unchanged':True,'deployment_uid_spec_unchanged':True,'old_image_refs_unchanged_on_all6':True,'final_at_utc':final['at_utc'],'started_at_utc':read(R/'stage-k8s-control01/stdout.json')['started_at_utc'],'archive_root_mode':'0700','archive_mode':'0600','platform':'linux/amd64','original_historical_supply_provenance_verified':False,'actual_cri_reboot_use_test':False,'ac_accepted':False,'image_store_creation_timestamp_collected':False,'creation_time_evidence':'observed absence-before / import command interval / presence-after only'}
print(json.dumps(result,ensure_ascii=False,indent=2))
