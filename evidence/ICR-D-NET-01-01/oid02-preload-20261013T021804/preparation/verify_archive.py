"""Read-only OCI tar closure verification for one fixed OID image and amd64.
No extraction, execution, server access, or output files. Config values are not emitted.
Usage: python3 verify_archive.py OBSERVED_SUPPLY.json IMAGE_NAME ARCHIVE.tar
"""
import hashlib,json,re,sys,tarfile
from pathlib import Path,PurePosixPath

def require(value,message):
 if not value:raise ValueError(message)
def digest(raw):return 'sha256:'+hashlib.sha256(raw).hexdigest()
def no_duplicates(pairs):
 result={}
 for k,v in pairs:
  require(k not in result,'DUPLICATE_JSON_KEY');result[k]=v
 return result
def decode(raw):return json.loads(raw,object_pairs_hook=no_duplicates)
def refs_for(im):
 if im['name']=='kube-controllers':return {'quay.io/calico/kube-controllers@'+im['approved_top_digest']}
 if im['name']=='coredns':return {'registry.k8s.io/coredns/coredns:v1.14.2','registry.k8s.io/coredns/coredns@'+im['approved_top_digest']}
 raise ValueError('UNKNOWN_IMAGE')
def verify(im,path):
 path=Path(path);require(path.is_file() and not path.is_symlink(),'ARCHIVE_NOT_REGULAR')
 require(1024<=path.stat().st_size<=128*1024*1024,'ARCHIVE_SIZE_LIMIT')
 initial=path.stat();members={};documents={};blobs={}
 doc_digests={im['approved_top_digest'],im['linux_amd64_manifest_digest'],im['config']['digest']}
 required=doc_digests|{x['digest'] for x in im['layers']}
 with tarfile.open(path,mode='r:') as tf:
  for count,m in enumerate(tf,1):
   require(count<=64,'MEMBER_LIMIT')
   name=m.name.rstrip('/') if m.isdir() else m.name
   require(name not in members and '\\' not in name and PurePosixPath(name).as_posix()==name and '..' not in PurePosixPath(name).parts and not name.startswith('/'),'UNSAFE_OR_DUPLICATE_MEMBER')
   if m.isdir():
    require(name in ['blobs','blobs/sha256'] and m.size==0,'UNEXPECTED_DIRECTORY');members[name]={'type':'directory'};continue
   require(m.isfile() and not m.issym() and not m.islnk(),'UNEXPECTED_MEMBER_TYPE')
   blob=re.fullmatch(r'blobs/sha256/([0-9a-f]{64})',name)
   require(name in ['index.json','oci-layout'] or blob,'UNEXPECTED_MEMBER')
   require(0<m.size<=64*1024*1024,'MEMBER_SIZE_LIMIT')
   key='sha256:'+blob[1] if blob else name
   if blob:require(key in required,'UNEXPECTED_BLOB')
   keep=key in doc_digests or not blob
   require(not keep or m.size<=4*1024*1024,'JSON_SIZE_LIMIT')
   h=hashlib.sha256();parts=[];n=0
   with tf.extractfile(m) as stream:
    while True:
     b=stream.read(1024*1024)
     if not b:break
     n+=len(b);h.update(b)
     if keep:parts.append(b)
   require(n==m.size,'SHORT_MEMBER')
   observed='sha256:'+h.hexdigest();members[name]={'size':n,'sha256':h.hexdigest()}
   if blob:require(observed==key,'BLOB_HASH_MISMATCH');blobs[key]=n
   if keep:documents[key]=decode(b''.join(parts))
 require(set(blobs)==required,'MISSING_CLOSURE_BLOB')
 require(documents.get('oci-layout')=={'imageLayoutVersion':'1.0.0'},'OCI_LAYOUT')
 root=documents['index.json'];require(root.get('schemaVersion')==2 and root.get('mediaType')=='application/vnd.oci.image.index.v1+json','ROOT_INDEX')
 exported=[]
 for d in root['manifests']:
  require(d['digest']==im['approved_top_digest'] and d['size']==blobs[d['digest']] and d['mediaType']==im['top_media_type'],'TOP_DESCRIPTOR')
  exported.append(d.get('annotations',{}).get('io.containerd.image.name'))
 require(len(exported)==len(set(exported)) and set(exported)==refs_for(im),'REFERENCE_SET')
 if im['index_digest']:
  top=documents[im['index_digest']];require(top.get('schemaVersion')==2 and top.get('mediaType')==im['top_media_type'],'TOP_INDEX')
  selected=[d for d in top['manifests'] if d.get('platform',{}).get('os')=='linux' and d.get('platform',{}).get('architecture')=='amd64' and d.get('platform',{}).get('variant') in [None,'']]
  require(len(selected)==1 and selected[0]['digest']==im['linux_amd64_manifest_digest'] and selected[0]['size']==blobs[selected[0]['digest']],'PLATFORM_SELECTION')
 mf=documents[im['linux_amd64_manifest_digest']]
 require(mf.get('schemaVersion')==2,'MANIFEST_SCHEMA')
 for actual,expected in [(mf['config'],im['config'])]+list(zip(mf['layers'],im['layers'])):
  require(all(actual[k]==expected[k] for k in ['digest','size','mediaType']),'CONTENT_DESCRIPTOR')
  require(blobs[actual['digest']]==actual['size'],'CONTENT_SIZE')
 require(len(mf['layers'])==len(im['layers']),'LAYER_COUNT')
 cfg=documents[im['config']['digest']]
 require(cfg.get('os')=='linux' and cfg.get('architecture')=='amd64','CONFIG_PLATFORM')
 require(cfg.get('rootfs',{}).get('type')=='layers' and len(cfg['rootfs']['diff_ids'])==len(im['layers']),'CONFIG_ROOTFS')
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 final=path.stat();require((initial.st_dev,initial.st_ino,initial.st_size,initial.st_mtime_ns)==(final.st_dev,final.st_ino,final.st_size,final.st_mtime_ns),'ARCHIVE_CHANGED')
 return {'status':'ARCHIVE_CLOSURE_VERIFIED','image':im['name'],'archive_sha256':h.hexdigest(),'archive_size_bytes':final.st_size,'platform':'linux/amd64','top_digest':im['approved_top_digest'],'manifest_digest':im['linux_amd64_manifest_digest'],'references':sorted(exported),'blob_count':len(blobs),'layer_count':len(im['layers']),'members':members,'historical_supply_provenance_verified':False,'all_platform_content_verified':False,'import_executed':False}

if __name__=='__main__':
 try:
  supply=decode(Path(sys.argv[1]).read_bytes());im=next(x for x in supply['images'] if x['name']==sys.argv[2])
  print(json.dumps(verify(im,sys.argv[3]),indent=2))
 except Exception as e:print(json.dumps({'status':'STOP','error':type(e).__name__+':'+str(e)}));raise SystemExit(2)
