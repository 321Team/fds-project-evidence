from pathlib import Path
import base64,contextlib,hashlib,io,json
import control_runtime as r
body='''import base64,hashlib,io,tarfile
ses=Path(SES);tok=Path(TOK)
assert not tok.exists(),'TOKEN_STILL_PRESENT'
files={}
for folder in ['results','journal','evidence']:
 for p in sorted((ses/folder).rglob('*')):
  assert not p.is_symlink()
  if p.is_file():
   assert p.stat().st_size<2097152
   files[p.relative_to(ses).as_posix()]=p.read_bytes()
files['input.json']=(ses/'input.json').read_bytes()
assert any(n.startswith('journal/') for n in files) and 'evidence/supervisor.jsonl' in files
hashes={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}
files['EXPORT_SHA256SUMS']=''.join(h+'  '+n+'\\n' for n,h in sorted(hashes.items())).encode()
stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for n,v in files.items():
  info=tarfile.TarInfo(n);info.size=len(v);info.mode=0o600;tar.addfile(info,io.BytesIO(v))
data=stream.getvalue()
print(json.dumps({'archive_base64':base64.b64encode(data).decode(),'archive_sha256':hashlib.sha256(data).hexdigest(),'files':hashes,'excluded':'token file was deleted; no credentials included'}))
'''.replace('Path(SES)','Path('+repr(r.SES)+')').replace('Path(TOK)','Path('+repr(r.TOK)+')')
with contextlib.redirect_stdout(io.StringIO()):row=r.run('control01-evidence-export',body,timeout=30)
assert row['rc']==0,row['stderr']
d=json.loads(row['stdout']);data=base64.b64decode(d.pop('archive_base64'));assert hashlib.sha256(data).hexdigest()==d['archive_sha256']
(r.ROOT/'control01-evidence.tar.gz').write_bytes(data)
(r.ROOT/'control01-evidence-manifest.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'archive_sha256':d['archive_sha256'],'files':len(d['files']),'credential_exports':0}))
