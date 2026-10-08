"""Read-only, offline correspondence verification of this failed trial."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
source=root/'server-originals'
receipt=json.loads((root/'RECEIPT.json').read_text())
checks={}
for name,meta in receipt['files'].items():
    data=(source/name).read_bytes()
    checks['hash:'+name]=hashlib.sha256(data).hexdigest()==meta['sha256'] and len(data)==meta['size']
pre=json.loads((source/'precheck.result.json').read_text())
run=json.loads((source/'run.result.json').read_text())
folder=next(p for p in source.glob('p1-sec01-ac06-probe-run-*') if p.is_dir())
summary=(folder/'99-summary-provisional.txt').read_text()
cleanup=(folder/'50-cleanup.txt').read_text()
post=json.loads((source/'post-readonly.json').read_text())
events=json.loads(post['commands'][0]['stdout'])['items']
image=json.loads((root/'drivers/imageread.json').read_text())['containers'][0]
checks.update(precheck_rc0=pre['rc']==0,run_rc3=run['rc']==3,
    no_T1_T2_T3=not any(folder.glob('T*-inject.*')),
    cleanup0='cleanup_failed=0' in summary,
    nodes_ready='nodes_post=6/6_Ready' in summary,
    baseline_unchanged='baseline_pods_diff_rc=0 baseline_endpointslices_diff_rc=0' in summary,
    both_gone=cleanup.count('NotFound 확인')==2,
    fresh_zero_objects=post['commands'][1]['rc']==0 and json.loads(post['commands'][1]['stdout'])['items']==[],
    post_queries_ok=all(c['rc']==0 for c in post['commands']),
    matching_failure_event=any(e['involvedObject']['uid']=='0c0491c7-fd89-45b4-b677-44dfc6f4bd9c' and
        '/venv/bin/python3' in e['message'] and 'no such file or directory' in e['message'] for e in events),
    same_image=image['image'].endswith('a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33'),
    real_exe=image['running_exe']=='/usr/local/bin/python3.12',
    old_path_absent=not image['candidates']['/venv/bin/python3']['lexists'])
assert all(checks.values()),[k for k,v in checks.items() if not v]
print(json.dumps({'passed':sum(checks.values()),'total':len(checks),'runtime_rc':run['rc'],'AC':'NOT_EVALUATED'},indent=2))
