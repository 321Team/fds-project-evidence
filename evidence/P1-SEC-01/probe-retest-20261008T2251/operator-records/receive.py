from pathlib import Path,PurePosixPath
import subprocess,shlex,tarfile,io,hashlib,json
root=Path(__file__).resolve().parent
cmd='sudo -n tar -C /root/sec01-probe-20261008t2245/receipt -cf - .'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','svc_ansible@10.1.93.102',cmd]
p=subprocess.run(['ssh','-o','BatchMode=yes','fds-ansible01',shlex.join(inner)],capture_output=True,timeout=60)
(root/'receive.stderr').write_bytes(p.stderr)
if p.returncode: raise SystemExit(p.returncode)
(root/'receipt-transfer.tar').write_bytes(p.stdout)
out=root/'received'
out.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(p.stdout)) as tf:
    seen=set()
    for m in tf.getmembers():
        name=PurePosixPath(m.name)
        assert not name.is_absolute() and '..' not in name.parts
        assert m.isdir() or m.isfile()
        if m.isdir(): continue
        assert str(name) not in seen
        seen.add(str(name))
        target=out.joinpath(*name.parts);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(tf.extractfile(m).read())
count=0
for line in (out/'SHA256SUMS').read_text().splitlines():
    sha,name=line.split('  ',1)
    assert hashlib.sha256((out/name).read_bytes()).hexdigest()==sha,name
    count+=1
for mode in ('precheck','run'):
    result=json.loads((out/mode/'result.json').read_bytes())
    print(mode,json.dumps(result))
print('RECEIVED_FILES_VERIFIED',count)
