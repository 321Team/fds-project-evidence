RAW=b'{\n  "session_id": "w02-20261013T024523-85942d67",\n  "source_sha": "0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea",\n  "sha256": "ce6295bcc88b8129003f50cb4cbd4be36d18c32413bbcf46e9926a552a1ea5b2",\n  "path": "/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions/w02-20261013T024523-85942d67/original-resolver.json",\n  "captured_at": "2026-10-12T17:53:49.015060+00:00",\n  "verified_worker_receipt": "backup-read/receipt.json"\n}\n'
DEST='/home/server01_ansible/p1-worker02-dns-20261013-r1/PINNED_BACKUP.json'
import hashlib,json,os,pathlib
assert os.uname().nodename=='ansible01' and os.geteuid()==1000
fd=os.open(DEST,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'wb') as f:f.write(RAW);f.flush();os.fsync(f.fileno())
assert pathlib.Path(DEST).read_bytes()==RAW
print(json.dumps({'status':'PIN_PRESERVED','path':DEST,'sha256':hashlib.sha256(RAW).hexdigest()}))
