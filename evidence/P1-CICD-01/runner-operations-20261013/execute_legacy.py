"""Execute only the user-confirmed legacy packet cleanup; no credential read/issue."""
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('receipts',HERE/'ops_api.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oldspec=importlib.util.spec_from_file_location('old_read',HERE.parent/'p1-runner81-execution-20261013/collect_final.py')
old=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(old)
assert not (HERE/'legacy-execute.receipt.json').exists(), 'NO_BLIND_RERUN'
approval={'recorded_at_utc':m.now(),'user_reply':'허용 — 28개 미사용·동시 변경 배제 후 삭제',
          'scope':'exact 28 paths in LEGACY_FRESH_METADATA; no reading or copying token values'}
(HERE/'LEGACY_AUTHORIZATION.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for status in ('queued','in_progress','requested','waiting','pending'):
    runs=m.api('legacy-regression-'+status,f'repos/{m.REPO}/actions/workflows/ansible-regression.yml/runs?status={status}&per_page=100')
    assert runs['total_count']==0 and runs['workflow_runs']==[], 'ACTIVE_REGRESSION'
runners=m.api('legacy-runners',f'repos/{m.REPO}/actions/runners?per_page=100')
assert runners['total_count']==0 and runners['runners']==[], 'RUNNER_PRESENT'
containers=json.loads(old.remote('cd /tmp && sudo -n -u ansible-verify env HOME=/home/ansible-verify XDG_RUNTIME_DIR=/run/user/1001 podman ps -a --format json','svc_ansible'))
proc='''import json,subprocess
r=subprocess.run(['sudo','-n','pgrep','-u','1001','-f','runner.py'],capture_output=True)
assert r.returncode in (0,1)
print(json.dumps({'runner_process_present':r.returncode==0}))'''
process=json.loads(old.remote(shlex.join(['python3','-I','-B','-c',proc]),'svc_ansible'))
preflight={'at_utc':m.now(),'registered_runners':runners['total_count'],'containers_count':len(containers),**process}
(HERE/'LEGACY_EXECUTION_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n')
assert containers==[] and process['runner_process_present'] is False
source=(HERE/'legacy_cleanup.py').read_text()
cmd=old.SSH+[shlex.join(['python3','-I','-B','-c',source,'--execute'])]
started=m.now()
p=subprocess.run(cmd,input=(HERE/'LEGACY_FRESH_METADATA.json').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
(HERE/'legacy-execute.stdout.jsonl').write_bytes(p.stdout)
(HERE/'legacy-execute.stderr.txt').write_bytes(p.stderr)
(HERE/'legacy-execute.receipt.json').write_text(json.dumps({'started_at_utc':started,'ended_at_utc':m.now(),'rc':p.returncode,
    'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'execute_flag':True,
    'input_sha256':hashlib.sha256((HERE/'LEGACY_FRESH_METADATA.json').read_bytes()).hexdigest()},indent=2)+'\n')
expected=json.loads((HERE/'LEGACY_FRESH_METADATA.json').read_text())
paths=[r['path'] for r in expected['packets']]
post='''import datetime,json,os,pathlib,socket
paths=TARGET_PATHS
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),
 'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'targets':[{'path':p,'present':os.path.lexists(p)} for p in paths],
 'other_packet_path_count':len(list(pathlib.Path('/home/server01_ansible').glob('ansible-runner-token-*.json*')))}))'''.replace('TARGET_PATHS',repr(paths))
(HERE/'legacy-post-collector.py').write_text(post)
raw=old.remote(shlex.join(['python3','-I','-B','-c',post]))
(HERE/'LEGACY_POST_OBSERVATION.json').write_bytes(raw)
post_data=json.loads(raw)
rows=[json.loads(line) for line in p.stdout.splitlines()]
assert p.returncode==0 and rows[0]=={'status':'ALL_TARGETS_MATCH','count':28,'execute':True}
assert rows[-1]=={'status':'ALL_TARGETS_ABSENT','count':28}
assert [r['path'] for r in rows if r['status']=='DELETED']==paths
assert post_data['host']==expected['host'] and post_data['boot']==expected['boot']
assert not any(r['present'] for r in post_data['targets'])
result={'status':'28_EXACT_PATHS_DELETED_AND_ABSENCE_VERIFIED','at_utc':m.now(),'deleted_count':28,
        'other_packet_path_count_observed':post_data['other_packet_path_count'],'token_contents_read':False,'server_side_token_revocation':'NOT_PERFORMED_OR_VERIFIED',
        'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
(HERE/'LEGACY_CLEANUP_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
