"""Synthetic archive checks only; never server evidence."""
import copy,io,json,tarfile,tempfile
from pathlib import Path
from verify_archive import digest,refs_for,verify

def raw(x):return json.dumps(x,separators=(',',':')).encode()
def fixture(name='kube-controllers',arch='amd64'):
 layer=b'synthetic-layer';config=raw({'os':'linux','architecture':arch,'rootfs':{'type':'layers','diff_ids':[digest(layer)]}})
 def descriptor(b,media):return {'digest':digest(b),'size':len(b),'mediaType':media}
 c=descriptor(config,'application/vnd.docker.container.image.v1+json');l=descriptor(layer,'application/vnd.docker.image.rootfs.diff.tar.gzip')
 mf=raw({'schemaVersion':2,'mediaType':'application/vnd.docker.distribution.manifest.v2+json','config':c,'layers':[l]});m=descriptor(mf,'application/vnd.docker.distribution.manifest.v2+json')
 content={digest(mf):mf,digest(config):config,digest(layer):layer};top=m
 if name=='coredns':
  child=dict(m,platform={'os':'linux','architecture':'amd64'})
  idx=raw({'schemaVersion':2,'mediaType':'application/vnd.docker.distribution.manifest.list.v2+json','manifests':[child,{'digest':'sha256:'+'a'*64,'size':123,'mediaType':m['mediaType'],'platform':{'os':'linux','architecture':'arm64'}}]})
  top=descriptor(idx,'application/vnd.docker.distribution.manifest.list.v2+json');content[digest(idx)]=idx
 im={'name':name,'approved_top_digest':top['digest'],'linux_amd64_manifest_digest':m['digest'],'index_digest':top['digest'] if name=='coredns' else None,'top_media_type':top['mediaType'],'config':c,'layers':[l]}
 root={'schemaVersion':2,'mediaType':'application/vnd.oci.image.index.v1+json','manifests':[dict(top,annotations={'io.containerd.image.name':r}) for r in sorted(refs_for(im))]}
 members=[('oci-layout',raw({'imageLayoutVersion':'1.0.0'})),('index.json',raw(root))]+[('blobs/sha256/'+k[7:],v) for k,v in content.items()]
 return im,members
def archive(path,members):
 with tarfile.open(path,'w') as tf:
  for name,b in members:
   m=tarfile.TarInfo(name);m.size=len(b)
   if name=='SYMLINK':m.type=tarfile.SYMTYPE;m.linkname='/tmp/target';m.size=0;tf.addfile(m)
   else:tf.addfile(m,io.BytesIO(b))
cases=[]
with tempfile.TemporaryDirectory(prefix='oid-archive-mock-') as d:
 for name in ['kube-controllers','coredns']:
  im,m=fixture(name);p=Path(d)/(name+'.tar');archive(p,m);verify(im,p);cases.append(name+'-valid')
 base,members=fixture()
 bad=[('corrupt',members[:-1]+[(members[-1][0],b'broken')]),('missing',members[:-1]),('duplicate',members+[members[-1]]),('traversal',members+[('../x',b'x')]),('symlink',members+[('SYMLINK',b'')]),('extra',members+[('extra.txt',b'x')]),('wrong-ref',[(n,raw({'schemaVersion':2,'mediaType':'application/vnd.oci.image.index.v1+json','manifests':[]})) if n=='index.json' else (n,b) for n,b in members])]
 for label,m in bad:
  p=Path(d)/(label+'.tar');archive(p,m)
  try:verify(base,p)
  except ValueError:cases.append(label+'-rejected')
  else:raise AssertionError(label)
 im,m=fixture(arch='arm64');p=Path(d)/'wrong-platform.tar';archive(p,m)
 try:verify(im,p)
 except ValueError as e:assert str(e)=='CONFIG_PLATFORM';cases.append('wrong-platform-rejected')
 else:raise AssertionError('wrong-platform')
result={'kind':'MOCK_SYNTHETIC_ONLY','passed':len(cases),'cases':cases,'server_execution':False}
Path(__file__).with_name('MOCK_VERIFICATION.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
