from pathlib import Path
import json,collections
p=Path(__file__).resolve().parent
s=json.loads((p/'probe-before-drain/stdout.json').read_bytes());b=json.loads((p/'baseline-mark/stdout.json').read_bytes())['epoch']
assert s['process_exists'] and s['result'] is None and s['non200']==0 and s['max_late']<=.2
assert s['last_sched']-b>=61 and s['first_sched']<=b
ticks=collections.defaultdict(list)
for line in s['probe_log'].splitlines():
 r=line.split()
 if b<=float(r[1])<=s['last_sched']-.5:ticks[int(r[0])].append(r[3])
assert ticks
assert all(sorted(ticks[t])==['10.1.93.105','10.1.93.107','10.1.93.108'] for t in range(min(ticks),max(ticks)+1))
print(json.dumps({'baseline_seconds':s['last_sched']-b,'ticks':len(ticks),'missing':0,'non200':s['non200'],'max_late':s['max_late']}))
