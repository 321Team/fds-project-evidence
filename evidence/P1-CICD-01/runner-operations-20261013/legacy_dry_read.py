import datetime as dt
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
HERE=Path(__file__).resolve().parent
source=(HERE/'legacy_cleanup.py').read_text()
assert not (HERE/'legacy-dry-run.stdout.jsonl').exists()
cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8',
     'fds-ansible01',shlex.join(['python3','-I','-B','-c',source])]
started=dt.datetime.now(dt.timezone.utc).isoformat()
p=subprocess.run(cmd,input=(HERE/'LEGACY_FRESH_METADATA.json').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40)
(HERE/'legacy-dry-run.stdout.jsonl').write_bytes(p.stdout)
(HERE/'legacy-dry-run.stderr.txt').write_bytes(p.stderr)
(HERE/'legacy-dry-run.receipt.json').write_text(json.dumps({'started_at_utc':started,'rc':p.returncode,
    'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'execute_flag':False,'input_sha256':hashlib.sha256((HERE/'LEGACY_FRESH_METADATA.json').read_bytes()).hexdigest()},indent=2)+'\n')
assert p.returncode==0
assert json.loads(p.stdout)=={'status':'ALL_TARGETS_MATCH','count':28,'execute':False}
print(p.stdout.decode())
