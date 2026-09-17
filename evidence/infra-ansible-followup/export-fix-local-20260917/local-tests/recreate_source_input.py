#!/usr/bin/env python3
"""Restore input JSON from an already-authorized local Git object database; no fetch."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

base=Path(__file__).resolve().parent
repo=Path(sys.argv[1]).resolve()
mapping=json.loads((base/'source-map.json').read_text())
target=base/'source-input.json'
if target.exists():raise SystemExit('STOP: source-input.json already exists')
entries=[]
for row in mapping['entries']:
    mode_blob=subprocess.check_output(['git','-C',str(repo),'ls-tree',row['ref'],'--',row['path']])
    assert mode_blob.split()[0].decode()==row['mode'],row['path']
    assert mode_blob.split()[2].decode()==row['sha'],row['path']
    data=subprocess.check_output(['git','-C',str(repo),'cat-file','blob',row['sha']])
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert actual==row['sha'],row['path']
    entries.append(dict(row,content=data.decode('utf-8')))
with target.open('x') as stream:
    json.dump({'heads':mapping['heads'],'entries':entries},stream)
    stream.write('\n')
print('RESTORED_VERIFIED_SOURCE_FILES='+str(len(entries)))

