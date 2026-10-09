import json,pathlib,shlex,subprocess,tarfile
R=pathlib.Path(__file__).resolve().parent
with tarfile.open(R.parents[1]/'phase1-work-20261009/private/app-affbc69-run-20261009/app-evidence.tar.gz','r:gz') as t:expected=json.load(t.extractfile('manifest.json'))['payloads']
(R/'raw-expected.json').write_bytes(json.dumps(expected,indent=2).encode())
script=(R/'export-app-raw-template.py').read_text(encoding='utf8').replace('EXPECTED_JSON',repr(json.dumps(expected)))
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','server01_cicd-runner@10.250.10.20','python3 -I -B -']
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(inner)],input=script.encode(),capture_output=True,timeout=300)
(R/'app-raw-export.stdout').write_bytes(r.stdout);(R/'app-raw-export.stderr').write_bytes(r.stderr)
print('RC',r.returncode)
if r.returncode==0:print(r.stdout.decode())
else:print(r.stderr.decode(errors='replace'))
