from pathlib import Path
import subprocess,json,datetime as dt,hashlib
r=Path(__file__).resolve().parent/'phase1-short-load-window-20261014-1415'/'governance-snapshot'
r.mkdir(exist_ok=False)
items={
 'decision-v2':'repos/321Team/fds-project-baseline/issues/comments/5885861552',
 'g3-approval':'repos/321Team/fds-project-baseline/issues/comments/5886568007',
 'window-plan':'repos/321Team/fds-project-baseline/issues/comments/6161231492',
 'window-confirmed':'repos/321Team/fds-project-baseline/issues/comments/6161260119',
 'app-pr33':'repos/321Team/fds-msa/pulls/33',
 'app-pr33-reviews':'repos/321Team/fds-msa/pulls/33/reviews',
}
receipts=[]
for name,route in items.items():
 p=subprocess.run(['gh','api',route],capture_output=True,check=True)
 json.loads(p.stdout)
 (r/(name+'.json')).write_bytes(p.stdout)
 receipts.append({'name':name,'route':route,'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'sha256':hashlib.sha256(p.stdout).hexdigest()})
(r/'RECEIPTS.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'read_only_snapshots':len(receipts)}))
