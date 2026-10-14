from pathlib import Path
p=Path(__file__).resolve().parent
prefix=(p/'recovery_template.remote.py').read_text(encoding='utf-8').split('\ntry:\n')[0]
prefix=prefix.replace('__APP__',repr('fds-engine')).replace('__MON_SOURCE__',repr((p.parent/'current-mon/collector.py').read_bytes()))
suffix='''
prior=json.loads((P/'fds-engine-recovery.json').read_bytes())
assert prior['status']=='STOP' and prior['error']=='AssertionError:MON_TIMEOUT'
assert prior['readiness'][-1]['ready'] and prior['ready_epoch']-datetime.datetime.fromisoformat(ev['finished_at_utc']).timestamp()<120
pods=prior['readiness'][-1]['pods'];expected={(p['app'],p['ip']+(':'+str(9091 if p['app']=='transaction-api' else 9090))) for p in pods}
valid=[]
for m in prior['monitoring']:
 up=json.loads(m['raw']['queries'][0]['raw'])['data']['result'];apps=[x for x in up if x['metric'].get('job') in images]
 if len(up)==23 and all(x['value'][1]=='1' for x in up) and {(x['metric']['job'],x['metric']['instance']) for x in apps}==expected:valid.append(m['epoch'])
assert valid and min(valid)-prior['ready_epoch']<=90
out.update(correction='Observer expected absent pod label. Existing originals show job/instance matching the current Pod IP and dedicated port; no runtime retry.',original_result='fds-engine-recovery.json',ready_epoch=prior['ready_epoch'],mon_first_valid_epoch=min(valid),original_mon_observations=len(prior['monitoring']),original_mon_correctly_matched=len(valid))
uids={p['uid'] for p in pods};until=time.monotonic()+30
try:
 while True:
  s=snap();m=mon(s['pods']);out['stability'].append({'state':s,'monitoring':m})
  assert s['ready'] and m['healthy'] and {x['uid'] for x in s['pods']}==uids,'STABILITY_FAILED'
  if time.monotonic()>=until:break
  time.sleep(5)
 out['status']='READY_MON_STABLE';out['final_counts']=s['counts']
except Exception as e:out['status']='STOP';out['error']=type(e).__name__+':'+str(e)
out['finished_epoch']=time.time()
with (P/'fds-engine-recovery-supplement.json').open('x') as f:json.dump(out,f)
print(json.dumps(out))
raise SystemExit(0 if out['status']=='READY_MON_STABLE' else 2)
'''
source=prefix+suffix;compile(source,'observer-supplement','exec');(p/'engine-observer-supplement.remote.py').write_text(source,encoding='utf-8')
