"""Derive timing intervals without turning snapshot uncertainty into proof."""
import base64,datetime as dt,json,math,re
import runtime as r
def txt(c):
 raw=base64.b64decode(c['stdout_b64']);assert r.sha(raw)==c['stdout_sha256'] and c['rc']==0
 return raw.decode()
hosts={}
for h in ['runner','control01','worker01','worker02','worker03','edge01']:
 a=r.load(r.O/'clocks-before-r1'/h/'stdout.json');b=r.load(r.O/'clocks-after-finish'/h/'stdout.json')
 estimates=[];refs=[];leaps=[]
 for v in [a,b]:
  t=txt(v['commands'][0]);fields={k.strip():z.strip() for k,z in (line.split(':',1) for line in t.splitlines() if ':' in line)}
  def number(k):
   m=re.fullmatch(r'([+\-0-9.]+) seconds(?: (?:slow|fast) of NTP time)?',fields[k]);assert m,k
   n=float(m[1]);assert math.isfinite(n);return n
  estimates.append(abs(number('System time'))+number('Root dispersion')+abs(number('Root delay'))/2)
  refs.append(fields['Reference ID']);leaps.append(fields['Leap status'])
  assert fields['Leap status']=='Normal'
  for c in v['commands']:txt(c)
 wall=(b['started']['unix_ns']-a['started']['unix_ns'])/1e9
 mono=(b['started']['monotonic_raw_ns']-a['started']['monotonic_raw_ns'])/1e9
 hosts[h]={'before_E_snapshot_seconds':estimates[0],'after_E_snapshot_seconds':estimates[1],'same_boot_id':a['boot_id']==b['boot_id'],'same_chrony_service_metadata':txt(a['commands'][2])==txt(b['commands'][2]),'references':refs,'leap_status':leaps,'wall_elapsed_seconds':wall,'monotonic_raw_elapsed_seconds':mono,'elapsed_difference_seconds':wall-mono,'E_interval_seconds':'UNPROVEN','reason':'Two snapshots and elapsed agreement do not establish a strict continuous error bound; no clock history covering the whole interval was collected.'}
parse=dt.datetime.fromisoformat
p=r.load(r.O/'P_FIRST_ORIGINAL.json');r2=r.load(r.O/'R2_FIRST_PATCH_INTERVAL.json');rec=r.load(r.O/'RECOVERY_HTTP_CONFIRMED.json');last=r.load(r.O/'r2-state-1550/stdout.json');absent=r.load(r.O/'R2_CURRENT_PODS.json')
out={'TIMING_METHOD':'ACCEPTED_6185621755','ORIGINAL_COMPLETENESS':'R1_R2_CLAIM_AND_8_CHECKPOINTS_EACH_PLUS_6_HOST_BEFORE_AFTER_CLOCKS','TIMING_PROOF':'시한 미입증 / SEC 사후 검토','P_exact':'NOT_MEASURED','R2_first_PATCH_exact':'NOT_MEASURED','last_old_terminated_exact':'NOT_MEASURED','p_lower_original_kst':p['p_lower_original_kst'],'r2_first_applied_upper_original_kst':r2['first_applied_upper_original_kst'],'recovery_observed_upper_kst':parse(rec['recovery_observation_upper_utc']).astimezone(r.START.tzinfo).isoformat(),'last_old_present_interval_start_utc':last['started_at_utc'],'last_old_absent_interval_end_utc':absent['first_all_old_absent_observed_utc'],'raw_unadjusted_seconds':{'r2_first_applied_minus_p':(parse(r2['first_applied_upper_original_kst'])-parse(p['p_lower_original_kst'])).total_seconds(),'recovery_observed_minus_p':(parse(rec['recovery_observation_upper_utc'])-parse(p['p_lower_original_kst'])).total_seconds()},'raw_interval_is_strict_proof':False,'actual_wall_clock_overrun':'NOT_OBSERVED','residual_old_exposure':'NONE_OBSERVED_BY_155137','hosts':hosts}
for phase in ['r1','r2']:
 j=r.load(r.O/(phase+'-journal-final')/phase/'stdout.json');assert j['chain_binding']=='MATCHED_CAPTURED_FILES' and len(j['checkpoint_files'])==8
 final=j['checkpoint_files'][-1]['data']['receipt'];assert final['ROLLOUT']=='READY' and final['error_code']=='NONE' and final['ROLLBACK']=='NOT_EXECUTED'
 out[phase+'_journal']={'run':final['execution']['run_id'],'final_sequence':8,'ROLLOUT':'READY','error':'NONE','automatic_rollback':'NOT_EXECUTED','writer_stop_basis':'Exact GitHub job completed; final-runner Worker0; own sockets absent; collector alone does not establish stop'}
r.save(r.O/'TIMING_ASSESSMENT.json',out)
print(json.dumps({'timing':out['TIMING_PROOF'],'unadjusted':out['raw_unadjusted_seconds'],'snapshots':{h:[v['before_E_snapshot_seconds'],v['after_E_snapshot_seconds']] for h,v in hosts.items()}},ensure_ascii=False))
