import pathlib,subprocess
r=pathlib.Path(__file__).resolve().parent
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01','python3 -'],input=(r/'p4-remote.py').read_bytes(),capture_output=True,timeout=750)
for ext,data in [('stdout',p.stdout),('stderr',p.stderr),('rc',str(p.returncode).encode()+b'\n')]: (r/('p4-transport.'+ext)).write_bytes(data)
print(p.stdout.decode());print(p.stderr.decode());print('transport_rc',p.returncode)
