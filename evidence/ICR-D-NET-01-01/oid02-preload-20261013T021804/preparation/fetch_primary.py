from pathlib import Path
import base64,hashlib,json,subprocess
P=Path(__file__).resolve().parent/'primary-reference';P.mkdir(exist_ok=True)
rev='1294c24a7da8e5a793ed378161673abe94118892'
records=[]
for name in ['cmd/ctr/commands/images/export.go','cmd/ctr/commands/images/import.go','client/import.go','core/images/archive/exporter.go','core/images/archive/importer.go']:
 p=subprocess.run(['gh','api',f'repos/containerd/containerd/contents/{name}?ref={rev}'],capture_output=True,check=True)
 o=json.loads(p.stdout);raw=base64.b64decode(o['content']);dest=P/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 records.append({'path':name,'revision':rev,'git_blob':o['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'url':f'https://github.com/containerd/containerd/blob/{rev}/{name}'})
(P/'SOURCES.json').write_bytes((json.dumps(records,indent=2)+'\n').encode())
print('Fetched 5 pinned primary source files, read-only GitHub access')
