from pathlib import Path
import hashlib,io,json,re,tarfile
root=Path(__file__).resolve().parent
def unpack(path):
 with tarfile.open(path,'r:gz') as t:
  files={Path(m.name).name:t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
 for line in files['SHA256SUMS'].decode().splitlines():
  sha,name=line.split('  ',1);assert hashlib.sha256(files[name]).hexdigest()==sha
 assert json.loads(files['receipt.json'])['collection_rc']==0
 return files
out={}
for role in ['gateway','monitor']:
 now=unpack(root/(role+'-pre.tar.gz'));old=unpack(root.parent/(role+'-post2-receipt')/'capture.tar.gz')
 names=['active-zones.stdout','links.stdout','routes.stdout','routing-rules.stdout','ip-forward.stdout','before-runtime-policy.stdout','before-permanent-policy.stdout','before-runtime-zones.stdout','before-permanent-zones.stdout','before-runtime-policies.stdout','before-permanent-policies.stdout'] if role=='gateway' else ['addresses.stdout','route-worker03.stdout','listeners.stdout','runtime-zones.stdout','permanent-zones.stdout']
 checks={n:now[n]==old[n] for n in names}
 if role=='gateway':
  norm=lambda b:re.sub(rb'counter packets \d+ bytes \d+',b'counter packets N bytes N',b)
  checks['nft']=norm(now['before-nft.stdout'])==norm(old['before-nft.stdout'])
 assert all(checks.values()),checks
 out[role]=checks
 if role=='monitor':
  heartbeat=float(json.loads(now['heartbeat-age.stdout'])['data']['result'][0]['value'][1]);alerts=json.loads(now['watchdog-alerts.stdout'])['data']['alerts']
  assert heartbeat<60 and not alerts
  out['monitor_baseline']={'heartbeat':heartbeat,'alerts':alerts}
mon=json.loads((root/'control01-mon-portforward-pre-remaining-read.json').read_text())
raw=json.loads(mon['observation']['commands'][0]['stdout'])
values={q['name']:json.loads(q['raw'])['data']['result'][0]['value'][1] for q in raw['queries']}
assert values=={'target_count':'23','target_up':'23','rw_failed_15m':'0'},values
out['control_baseline']=values
new=json.loads(json.loads((root/'control01-policy-pre.json').read_text())['stdout'])
old=json.loads(json.loads((root.parent/'control01-policy-post.json').read_text())['stdout'])
assert new['all_gnp']==old['all_gnp']
for obj in ['hep','hostgnp']:assert new['objects'][obj]['info']==old['objects'][obj]['info']
out['control_policy_matches_previous']=True
(root/'PRECONDITIONS_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
