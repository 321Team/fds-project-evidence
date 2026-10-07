import base64,datetime,json,pathlib,shlex,subprocess
P=pathlib.Path(__file__).resolve().parent
D=P/'engine-native-result';D.mkdir(exist_ok=False)
script=(P/'engine-native-stage.py').read_bytes()
code='import base64;exec(compile(base64.b64decode('+repr(base64.b64encode(script).decode())+'),"engine-native-stage.py","exec"))'
cmd=shlex.join(['python3','-I','-B','-c',code])
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',cmd],input=(P/'ansible-engine-da4e273e.bundle').read_bytes(),capture_output=True,timeout=240)
(D/'remote.stdout').write_bytes(r.stdout);(D/'remote.stderr').write_bytes(r.stderr)
(D/'invocation.json').write_text(json.dumps(dict(started_at=started,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),rc=r.returncode),indent=2)+'\n')
print(r.stdout.decode(errors='replace'));print('RC',r.returncode)
if r.returncode:print(r.stderr.decode(errors='replace'))
