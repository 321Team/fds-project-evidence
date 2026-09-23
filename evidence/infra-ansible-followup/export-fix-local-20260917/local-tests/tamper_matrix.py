#!/usr/bin/env python3
"""Synthetic mutation tests of existing manifest/collector and proposed binding helper."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
from unittest.mock import patch

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from offline_guard import install
from prepare_and_run import verify
from review_binding import check
install()
sys.path.insert(0,str(BASE/'candidate/tools/ansible-runner'))
import common,launch

def manifest_case(name):
    root=BASE/'results/tamper/manifest'/name
    root.mkdir(parents=True)
    files={'one.json':b'{"value":1}\n','logs/two.log':b'SYNTHETIC LOG\n'}
    for p,b in files.items():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    rows=[hashlib.sha256(b).hexdigest()+'  '+p+'\n' for p,b in files.items()]
    (root/'SHA256SUMS').write_text(''.join(rows))
    if name=='changed-byte':(root/'one.json').write_bytes(b'{"value":2}\n')
    elif name=='missing-file':(root/'one.json').unlink()
    elif name=='extra-file':(root/'extra').write_bytes(b'extra')
    elif name=='duplicate-row':(root/'SHA256SUMS').write_text(''.join(rows)+rows[0])
    elif name=='missing-row':(root/'SHA256SUMS').write_text(rows[0])
    elif name=='wrong-hash':(root/'SHA256SUMS').write_text('0'*64+'  one.json\n'+rows[1])
    elif name=='traversal':(root/'SHA256SUMS').write_text('0'*64+'  ../escape\n')
    elif name=='absolute':(root/'SHA256SUMS').write_text('0'*64+'  /escape\n')
    elif name=='noncanonical':(root/'SHA256SUMS').write_text(rows[0].replace('one.json','./one.json')+rows[1])
    elif name=='symlink-file':
        (root/'one.json').unlink();(root/'one.json').symlink_to('logs/two.log')
    elif name=='symlink-directory':(root/'linked').symlink_to('logs',target_is_directory=True)
    elif name=='hardlink':os.link(root/'one.json',root/'hardlink')
    elif name=='fifo':os.mkfifo(root/'pipe',0o600)
    error=None
    try:common.manifest(root);accepted=True
    except Exception as exc:accepted=False;error=type(exc).__name__
    return {'implementation':'existing common.manifest','case':name,'accepted':accepted,
            'passed':accepted==(name=='control'),'error':error}

def tar_case(name):
    root=BASE/'results/tamper/collector'/name
    run=root/'run';run.mkdir(parents=True)
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as tar:
        entries=[('evidence/HOST_RUN_RESULT.json',b'{"status":"FAIL"}')]
        if name=='missing-result':entries=[('other',b'{}')]
        if name=='duplicate-result':entries*=2
        if name=='invalid-json':entries=[('evidence/HOST_RUN_RESULT.json',b'{')]
        if name=='oversize-result':entries=[('evidence/HOST_RUN_RESULT.json',b'x'*32768)]
        if name=='too-many-members':entries += [(f'x{i}',b'') for i in range(100)]
        for member,data in entries:
            info=tarfile.TarInfo(member);info.mode=0o600;info.size=len(data)
            if name=='linked-result':
                info.type=tarfile.SYMTYPE;info.linkname='/outside';info.size=0
                tar.addfile(info)
            else:tar.addfile(info,io.BytesIO(data))
    raw=out.getvalue()
    if name=='corrupt-gzip':raw=b'not-gzip'
    archive=run/common.ARCHIVE;archive.write_bytes(raw)
    sidecar=run/(common.ARCHIVE+'.sha256')
    sidecar.write_text(hashlib.sha256(raw).hexdigest()+'  '+common.ARCHIVE+'\n')
    if name=='wrong-sidecar-hash':sidecar.write_text('0'*64+'  '+common.ARCHIVE+'\n')
    elif name=='wrong-sidecar-name':sidecar.write_text(hashlib.sha256(raw).hexdigest()+'  wrong.tar.gz\n')
    elif name=='linked-archive':
        original=run/'original';archive.rename(original);archive.symlink_to(original.name)
    error=None
    try:
        with patch.object(launch,'UID',os.getuid()):
            result=launch.copy_original(run,root/'collected')
        accepted=True
        assert result=={'status':'FAIL'}
    except Exception as exc:accepted=False;error=type(exc).__name__
    return {'implementation':'existing launch.copy_original (bounded host-result reader, not full archive verifier)',
            'case':name,'accepted':accepted,'passed':accepted==(name=='control'),'error':error}

def bindings():
    expected={'source':'a'*40,'pr':99,'run':101,'attempt':2,'job':201,'conclusion':'success',
        'ci_status':'PASS','runner_id':7,'runner_name':'ansible-ci-'+'b'*32,
        'repository':'321Team/infra-ansible','bundle_sha256':'c'*64,'image_id':'sha256:'+'d'*64}
    status={'status':'completed','conclusion':'success','head_sha':expected['source']}
    receipt={'pr':{'number':99,'head':{'sha':expected['source']}},
        'run':dict(status,id=101,run_attempt=2),
        'job':dict(status,id=201,run_id=101,run_attempt=2,runner_id=7,runner_name=expected['runner_name']),
        'check':dict(status,id=201),
        'ci':{'status':'PASS','source_commit':expected['source'],'github':{
            'GITHUB_RUN_ID':'101','GITHUB_RUN_ATTEMPT':'2','RUNNER_NAME':expected['runner_name'],
            'GITHUB_REPOSITORY':expected['repository']}},
        'host':{'runner':{'agentId':7,'agentName':expected['runner_name']},
            'bundle_sha256':expected['bundle_sha256'],'image_id':expected['image_id'],
            'cleanup':dict.fromkeys(['runner','proxy','workspace'],'REMOVED')},
        'pagination_complete':True,'runners':{'total_count':0,'runners':[]}}
    cases=[('positive-control',copy.deepcopy(receipt),expected,True)]
    negative=copy.deepcopy(receipt)
    for k in ['run','job','check']:negative[k]['conclusion']='failure'
    negative['ci']['status']='FAIL'
    neg_expected=dict(expected,conclusion='failure',ci_status='FAIL')
    cases.append(('expected-negative-control',negative,neg_expected,True))
    changes=[
        (['pr','head','sha'],'b'*40),(['run','head_sha'],'b'*40),(['job','head_sha'],'b'*40),
        (['check','head_sha'],'b'*40),(['ci','source_commit'],'b'*40),
        (['pr','number'],98),(['run','id'],102),(['job','run_id'],102),
        (['run','run_attempt'],1),(['job','run_attempt'],1),(['job','id'],202),(['check','id'],202),
        (['ci','github','GITHUB_RUN_ID'],'102'),(['ci','github','GITHUB_RUN_ATTEMPT'],'1'),
        (['ci','github','GITHUB_REPOSITORY'],'different/repo'),(['ci','github','RUNNER_NAME'],'different'),
        (['job','runner_id'],8),(['host','runner','agentId'],8),(['host','runner','agentId'],True),
        (['host','runner','agentName'],'different'),(['host','bundle_sha256'],'e'*64),
        (['host','image_id'],'sha256:'+'e'*64),(['host','cleanup','runner'],'FAILED'),
        (['host','cleanup','proxy'],'FAILED'),(['host','cleanup','workspace'],'FAILED'),
        (['pagination_complete'],False),(['pagination_complete'],1),(['runners','total_count'],1),
        (['run','status'],'queued'),(['check','conclusion'],'failure'),(['ci','status'],'FAIL'),
    ]
    for path,value in changes:
        clone=copy.deepcopy(receipt);target=clone
        for k in path[:-1]:target=target[k]
        target[path[-1]]=value
        cases.append(('.'.join(path)+'='+str(value),clone,expected,False))
    for name,row in [('id-present',{'id':7,'name':'other'}),('name-present',{'id':8,'name':expected['runner_name']})]:
        clone=copy.deepcopy(receipt);clone['runners']={'total_count':1,'runners':[row]}
        cases.append((name,clone,expected,False))
    result=[]
    for name,received,exp,wanted in cases:
        error=None
        try:accepted=check(received,exp)
        except Exception as exc:accepted=False;error=str(exc)
        result.append({'implementation':'NEW proposed review_binding.py; synthetic model, not deployed',
            'case':name,'accepted':accepted,'passed':accepted==wanted,'error':error})
    return result

if __name__=='__main__':
    manifest_names=['control','changed-byte','missing-file','extra-file','duplicate-row','missing-row',
        'wrong-hash','traversal','absolute','noncanonical','symlink-file','symlink-directory','hardlink','fifo']
    tar_names=['control','missing-result','duplicate-result','invalid-json','oversize-result',
        'too-many-members','linked-result','corrupt-gzip','wrong-sidecar-hash','wrong-sidecar-name','linked-archive']
    rows=[manifest_case(n) for n in manifest_names]+[tar_case(n) for n in tar_names]+bindings()
    verify()
    (BASE/'results/TAMPER_MATRIX.json').write_text(json.dumps({
        'scope':'synthetic fixtures only; original uploaded evidence not altered or reaccepted',
        'cases':rows,'source_unchanged':True},indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'passed':sum(r['passed'] for r in rows),
        'existing_code_cases':len(manifest_names)+len(tar_names),'proposed_binding_cases':len(rows)-25}))

