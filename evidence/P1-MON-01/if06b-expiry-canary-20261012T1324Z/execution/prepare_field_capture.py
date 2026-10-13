from pathlib import Path
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parent
bundle=root/'field-inputs';bundle.mkdir()
remote='/home/server01_ansible/if06b-field-auth-20261012T2220'
for role,target in [('gateway','server01_mgmt-gw@10.1.93.58'),('monitor','server01_monitor@10.250.10.30')]:
 dest=bundle/role;dest.mkdir()
 code=(root/'auth-inputs'/role/'collect.py').read_bytes()
 (dest/'collect.py').write_bytes(code)
 (dest/'field-remote.sh').write_bytes((root/'field-remote.sh').read_bytes())
 (dest/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256((dest/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in ['collect.py','field-remote.sh']))
 script='''#!/usr/bin/env bash
set -euo pipefail
set +x
umask 077
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
test "$(hostname -s)" = ansible01
sha256sum -c SHA256SUMS
mkdir execution-claim || exit 97
TARGET=__TARGET__
SOCKET=$PWD/ssh-control
SSH=(-o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ControlPath="$SOCKET")
finish() { ssh "${SSH[@]}" -O exit "$TARGET" >/dev/null 2>&1 || true; }
trap finish EXIT
ssh "${SSH[@]}" -o ControlMaster=yes -o ControlPersist=600 -Nf "$TARGET"
SSH+=(-o BatchMode=yes)
REMOTE=$(ssh "${SSH[@]}" "$TARGET" 'umask 077; mktemp -d /tmp/if06b-field.XXXXXXXX')
[[ "$REMOTE" =~ ^/tmp/if06b-field\.[A-Za-z0-9]+$ ]] || exit 2
printf '%s\\n' "$REMOTE" > remote-stage.txt
scp "${SSH[@]}" collect.py field-remote.sh SOURCE_SHA256SUMS "$TARGET:$REMOTE/"
set +e
ssh -t "${SSH[@]}" "$TARGET" "bash '$REMOTE/field-remote.sh' '$REMOTE' __ROLE__"
rc=$?
set -e
printf '%s\\n' "$rc" > remote.rc
scp "${SSH[@]}" "$TARGET:$REMOTE/capture.tar.gz" "$TARGET:$REMOTE/capture.tar.gz.sha256" .
sha256sum -c capture.tar.gz.sha256
date -Is > completed.time
exit "$rc"
'''.replace('__TARGET__',target).replace('__ROLE__',role)
 (dest/'run.sh').write_text(script,encoding='utf-8',newline='\n')
 (dest/'SHA256SUMS').write_text(''.join(hashlib.sha256((dest/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in ['collect.py','field-remote.sh','SOURCE_SHA256SUMS','run.sh']))
 launch='''@echo off
title MON IF06B __ROLE__ capture - keep open
echo Enter existing SSH and sudo passwords. This window captures for 300 seconds.
"C:\\Windows\\System32\\OpenSSH\\ssh.exe" -tt -o StrictHostKeyChecking=yes -o ConnectTimeout=8 fds-ansible01 /bin/bash __REMOTE__/__ROLE__/run.sh
echo Collection finished, rc=%ERRORLEVEL%.
pause
'''.replace('__REMOTE__',remote).replace('__ROLE__',role)
 (root/('OPEN_FIELD_'+role.upper()+'.cmd')).write_text(launch,encoding='ascii',newline='\r\n')
files={p.relative_to(bundle).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in bundle.rglob('*') if p.is_file()}
(root/'field-preparation.json').write_text(json.dumps({'remote_stage':remote,'files':files},indent=2)+'\n')
for p in bundle.rglob('*.sh'):
 q=subprocess.run(['C:/Program Files/Git/bin/bash.exe','-n',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stderr
# Reuse the same new-path-only staging method with separate input/receipt names.
stage=(root/'stage_auth_collection.py').read_text().replace('auth-stage-receipt.json','field-stage-receipt.json').replace('auth-preparation.json','field-preparation.json').replace("root/'auth-inputs'","root/'field-inputs'")
exec(compile(stage,str(root/'stage_auth_collection.py'),'exec'),{'__file__':str(root/'stage_auth_collection.py'),'__name__':'__main__'})
print('FIELD_CAPTURE_CARDS_STAGED; no capture started')
