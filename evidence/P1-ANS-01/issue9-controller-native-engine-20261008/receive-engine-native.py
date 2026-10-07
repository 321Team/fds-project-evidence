import base64,hashlib,io,json,pathlib,shlex,subprocess,tarfile
P=pathlib.Path(__file__).resolve().parent;D=P/'engine-native-result'
report=json.loads((D/'remote.stdout').read_bytes());root=report['evidence_root']
assert root=='/home/server01_ansible/issue9-native-engine-2rz3_9f4/evidence'
code='''import hashlib,io,pathlib,sys,tarfile
p=pathlib.Path('/home/server01_ansible/issue9-native-engine-2rz3_9f4/evidence')
for line in (p/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);f=p/n
 assert f.is_file() and not f.is_symlink() and '/' not in n
 assert hashlib.sha256(f.read_bytes()).hexdigest()==h
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as t:
 for f in sorted(p.iterdir()):
  assert f.is_file() and not f.is_symlink()
  t.add(f,arcname=f.name,recursive=False)
raw=buf.getvalue()
archive=p.parent/'engine-native-evidence.tar.gz'
assert not archive.exists()
archive.write_bytes(raw)
(p.parent/'engine-native-evidence.tar.gz.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  engine-native-evidence.tar.gz\\n')
sys.stderr.write(hashlib.sha256(raw).hexdigest()+'\\n');sys.stdout.buffer.write(raw)
'''
cmd=shlex.join(['python3','-I','-B','-c',code])
r=subprocess.run(['ssh','-o','BatchMode=yes','fds-ansible01',cmd],capture_output=True,check=True,timeout=30)
actual=hashlib.sha256(r.stdout).hexdigest();assert r.stderr.decode().strip()==actual
(D/'engine-native-evidence.tar.gz').write_bytes(r.stdout)
(D/'engine-native-evidence.tar.gz.sha256').write_text(actual+'  engine-native-evidence.tar.gz\n')
original=D/'original';original.mkdir()
with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and '/' not in m.name and m.size<1024*1024
  (original/m.name).write_bytes(t.extractfile(m).read())
for line in (original/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);assert hashlib.sha256((original/n).read_bytes()).hexdigest()==h
assert json.loads((original/'REPORT.json').read_bytes())==report
print(json.dumps(dict(archive_sha256=actual,members=len(list(original.iterdir())),manifest_items=len((original/'SHA256SUMS').read_text().splitlines()),server_receiver_match=True)))
for f in sorted(original.glob('*.stdout')):
 print(f.name+': '+f.read_text().splitlines()[0] if f.stat().st_size else f.name+': EMPTY')
print((original/'gate0-selected-syntax.stderr').read_text())
