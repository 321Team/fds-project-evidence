"""Project existing local evidence; no network, remote command, import of runtime tools."""
import base64, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/'deliverables/p1-cicd-ac09-preparation-20261015/runtime-1535'
for phase in ['r1','r2']:
    print('PHASE',phase)
    for name in [phase+'-post-one',phase+'-before-mon',phase+'-after-mon']:
        f=SRC/name/'stdout.json'
        if not f.exists():
            print(name,'MISSING'); continue
        obj=json.loads(f.read_bytes())
        if 'stdout' in obj:
            obj=json.loads(obj['stdout'])
        if 'requests' in obj:
            rows=[]
            for row in obj['requests']:
                d={k:row[k] for k in ['pod_name','pod_uid','host','port','path','status','error','started_utc','finished_utc'] if k in row}
                if 'body_b64' in row:
                    body=base64.b64decode(row['body_b64'],validate=True)
                    assert hashlib.sha256(body).hexdigest()==row['body_sha256']
                    if row['path']=='/metrics':
                        d['selected_lines']=[x for x in body.decode().splitlines() if x.startswith(('process_start_time_seconds ','transaction_save_','missing_client_ip_','fds_evaluated_','fds_evaluation_error_','fds_detected_total'))]
                    elif 'query' in row['path']:
                        d['up']=json.loads(body)
                rows.append(d)
            print(name,json.dumps(rows,ensure_ascii=False))
        else:
            if 'body_b64' in obj:
                obj['body']=json.loads(base64.b64decode(obj.pop('body_b64')))
            print(name,json.dumps(obj,ensure_ascii=False))
    for candidate in ([phase+'-state-1544',phase+'-stable-before-r2'] if phase=='r1' else [phase+'-state-1550',phase+'-stable-after-post']):
        f=SRC/candidate/'stdout.json'
        if f.exists():
            obj=json.loads(f.read_bytes())
            print(candidate,json.dumps({k:obj.get(k) for k in ['started_at_utc','finished_at_utc','deployments','pods']},ensure_ascii=False))
print('R2 candidate folders',[p.name for p in SRC.iterdir() if p.is_dir() and p.name.lower().startswith('r2')])
