import datetime as dt
import json
import os
import pwd
import socket
from pathlib import Path
assert socket.gethostname() == 'cicd-runner01' and pwd.getpwuid(os.getuid()).pw_name == 'server01_cicd-runner'
out = {'classification': 'PREPARATION', 'observed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
       'host': socket.gethostname(), 'user': 'server01_cicd-runner', 'processes': [], 'mutation': False}
for p in Path('/proc').iterdir():
    if not p.name.isdigit():
        continue
    try:
        name = (p / 'comm').read_text().strip()
        if name in ('Runner.Listener', 'Runner.Worker'):
            out['processes'].append({'pid': int(p.name), 'name': name, 'uid': p.stat().st_uid})
    except (FileNotFoundError, PermissionError):
        pass
print(json.dumps(out, sort_keys=True))
