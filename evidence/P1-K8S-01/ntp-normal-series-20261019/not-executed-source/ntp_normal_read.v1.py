"""Local one-shot controller: memory-only, numeric chronyc observations."""
import ast
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

O=Path(__file__).resolve().parent
A=O.parent/'resume-execution-20261018-1853/Ansible/ntp-normal-series-preparation-20261019-1215'
KST=dt.timezone(dt.timedelta(hours=9))
ENV={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'}

def now():return dt.datetime.now(KST).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

NODE_CODE=r'''
import datetime,hashlib,json,os,pathlib,pwd,socket,subprocess,time
P=pathlib.Path
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity():
 return {'host':socket.gethostname(),'machine_id':P('/etc/machine-id').read_text().strip(),
         'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),
         'uid':os.getuid(),'euid':os.geteuid(),'account':pwd.getpwuid(os.geteuid()).pw_name,
         'sudo_user':os.environ.get('SUDO_USER')}
def guard(v):
 return (v['host']==REQUEST['host'] and v['machine_id']==REQUEST['machine_id'] and
         v['boot_id']==REQUEST['boot_id'] and v['uid']==v['euid']==0 and
         v['account']=='root' and v['sudo_user']=='svc_ansible')
def observe(argv):
 start=now();mono=time.monotonic_ns()
 p=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'})
 timed_out=False;term=False;outstanding=False
 try:out,err=p.communicate(timeout=5)
 except subprocess.TimeoutExpired:
  timed_out=True;p.terminate();term=True
  try:out,err=p.communicate(timeout=2)
  except subprocess.TimeoutExpired as e:
   out=e.output or b'';err=e.stderr or b'';outstanding=True
 return {'argv':argv,'pid':p.pid,'started_utc':start,'started_monotonic_ns':mono,
         'finished_utc':now(),'finished_monotonic_ns':time.monotonic_ns(),
         'rc':p.returncode,'timeout':timed_out,'normal_term_requested':term,'unreaped':outstanding,
         'stdout':out[:65536].decode('utf-8','replace'),'stderr':err[:65536].decode('utf-8','replace'),
         'stdout_bytes':len(out),'stderr_bytes':len(err),'stdout_sha256':hashlib.sha256(out).hexdigest(),
         'stderr_sha256':hashlib.sha256(err).hexdigest(),'truncated':len(out)>65536 or len(err)>65536}
result={'run':REQUEST['run'],'sample':REQUEST['sample'],'at_utc':now(),'read_only':True,'commands':[]}
try:
 result['identity_before']=identity()
 if not guard(result['identity_before']):raise ValueError('IDENTITY_MISMATCH_BEFORE')
 not_before=REQUEST['not_before_monotonic_ns']
 remaining=max(0,(not_before-time.monotonic_ns())/1e9)
 if remaining>61:raise ValueError('WAIT_BOUND_EXCEEDED')
 if remaining:time.sleep(remaining)
 result['identity_at_sample']=identity()
 if not guard(result['identity_at_sample']):raise ValueError('IDENTITY_MISMATCH_AT_SAMPLE')
 for argv in [['/usr/bin/chronyc','-n','tracking'],['/usr/bin/chronyc','-n','sources','-a']]:
  r=observe(argv);result['commands'].append(r)
  if r['rc']!=0 or r['timeout'] or r['unreaped'] or r['truncated']:raise ValueError('COMMAND_FAILED_OR_INCOMPLETE')
 result['identity_after']=identity()
 if not guard(result['identity_after']):raise ValueError('IDENTITY_MISMATCH_AFTER')
 result['status']='SAMPLE_READ_COMPLETE_NOT_ACCEPTANCE'
except Exception as exc:
 result['status']='HOLD_NO_RETRY';result['error']=str(exc)
result['finished_utc']=now()
print(json.dumps(result,separators=(',',':')))
raise SystemExit(0 if result['status']=='SAMPLE_READ_COMPLETE_NOT_ACCEPTANCE' else 2)
'''

RELAY_CODE=r'''
import concurrent.futures,datetime,json,os,pathlib,pwd,socket,subprocess,time
def ident():
 return {'host':socket.gethostname(),'uid':os.getuid(),'euid':os.geteuid(),
         'account':pwd.getpwuid(os.geteuid()).pw_name,
         'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
def valid(i):return (i['host']=='ansible01' and i['uid']==i['euid']==1000 and
                    i['account']=='server01_ansible' and i['boot_id']==EXPECTED_RELAY_BOOT)
out={'relay_before':ident(),'results':[],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if not valid(out['relay_before']):
 out['status']='RELAY_IDENTITY_MISMATCH';print(json.dumps(out));raise SystemExit(2)
def one(job):
 p=subprocess.Popen(job['argv'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  stdout,stderr=p.communicate(job['payload'].encode('utf-8'),timeout=85)
  return {'host':job['host'],'ssh_pid':p.pid,'ssh_rc':p.returncode,'stdout':stdout.decode('utf-8','replace'),
          'stderr':stderr.decode('utf-8','replace'),'process_returned':True}
 except subprocess.TimeoutExpired as e:
  return {'host':job['host'],'ssh_pid':p.pid,'ssh_rc':p.returncode,
          'stdout':(e.output or b'').decode('utf-8','replace'),'stderr':(e.stderr or b'').decode('utf-8','replace'),
          'process_returned':False,'error':'RELAY_SSH_RETURN_UNCONFIRMED_NO_RETRY_OR_FORCE'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:out['results']=list(pool.map(one,JOBS))
out['relay_after']=ident();out['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
out['status']='RELAY_RETURNED' if valid(out['relay_after']) and all(r['process_returned'] for r in out['results']) else 'HOLD_NO_RETRY'
print(json.dumps(out,separators=(',',':')))
raise SystemExit(0 if out['status']=='RELAY_RETURNED' else 2)
'''

def parse_sample(sample,host):
    assert sample['status']=='SAMPLE_READ_COMPLETE_NOT_ACCEPTANCE'
    cmds=sample['commands'];assert len(cmds)==2
    assert [x['argv'] for x in cmds]==[['/usr/bin/chronyc','-n','tracking'],['/usr/bin/chronyc','-n','sources','-a']]
    for x in cmds:assert x['rc']==0 and not any(x[k] for k in ['timeout','unreaped','truncated'])
    text=cmds[0]['stdout']
    def field(pattern):
        values=re.findall(pattern,text,re.M);assert len(values)==1,('tracking_field_count',pattern,len(values));return values[0].strip()
    leap=field(r'^Leap status\s*:\s*([^\r\n]+)$')
    number=r'([+\-0-9.eE]+)'
    last=float(field(r'^Last offset\s*:\s*'+number+r'\s+seconds\s*$'))
    current=float(field(r'^System time\s*:\s*'+number+r'\s+seconds\s+(?:fast|slow) of NTP time\s*$'))
    stratum=int(field(r'^Stratum\s*:\s*([0-9]+)\s*$'))
    assert leap=='Normal' and 1<=stratum<=15,'LEAP_OR_STRATUM'
    assert all(math.isfinite(x) and abs(x)<=0.1 for x in [last,current]),'OFFSET_OUTSIDE_100MS'
    sources=[]
    for line in cmds[1]['stdout'].splitlines():
        m=re.match(r'^([\^=#])([*+\-?x~])\s+(\S+)\s+',line)
        if m:sources.append({'mode':m[1],'state':m[2],'source':m[3]})
    selected=[s for s in sources if s['state']=='*'];assert len(selected)==1,'SELECTED_SOURCE_COUNT'
    if host=='k8s-control01':
        assert len(sources)==2 and {s['source'] for s in sources}=={'162.159.200.1','162.159.200.123'},'SOURCE_LAYOUT_CHANGED'
        assert all(s['mode']=='^' for s in sources),'SOURCE_MODE_CHANGED'
    else:assert sources==[{'mode':'^','state':'*','source':'10.1.93.102'}],'CLIENT_SOURCE_CHANGED'
    return {'leap':leap,'stratum':stratum,'last_offset_ms':last*1000,'system_time_ms':current*1000,
            'sources':sources,'tracking_started_monotonic_ns':cmds[0]['started_monotonic_ns'],
            'tracking_started_utc':cmds[0]['started_utc']}

def prepare():
    assert not (O/'NTP_PREPARED.json').exists()
    transport=load(A/'TRANSPORT_BINDING.json')
    assert len(transport['nodes'])==6 and len({x['host'] for x in transport['nodes']})==6
    assert all(x['expected_auth_account']=='svc_ansible' and x['expected_process_euid']==0 for x in transport['nodes'])
    assert transport['outer_argv'][-1]=='-'
    compile(NODE_CODE,'ntp_node','exec');compile(RELAY_CODE,'ntp_relay','exec')
    assert all(s not in NODE_CODE for s in ['makestep','systemctl','write_text','write_bytes','os.remove','kill(','SIGKILL','-Q','iburst'])
    valid={'status':'SAMPLE_READ_COMPLETE_NOT_ACCEPTANCE','commands':[
      {'argv':['/usr/bin/chronyc','-n','tracking'],'rc':0,'timeout':False,'unreaped':False,'truncated':False,
       'stdout':'Stratum : 3\nLast offset : +0.0002 seconds\nSystem time : 0.0001 seconds slow of NTP time\nLeap status : Normal\n','started_monotonic_ns':123,'started_utc':'LOCAL_SELF_CHECK_NOT_RUNTIME'},
      {'argv':['/usr/bin/chronyc','-n','sources','-a'],'rc':0,'timeout':False,'unreaped':False,'truncated':False,
       'stdout':'^* 10.1.93.102 2 6 377 4 +10us[+2us] +/- 10ms\n'}]}
    import copy
    assert parse_sample(valid,'k8s-worker01')['last_offset_ms']==0.2
    rejected=[]
    for label,change in [
        ('duplicate_field',lambda d:d['commands'][0].update(stdout=d['commands'][0]['stdout']+'Leap status : Normal\n')),
        ('nonfinite',lambda d:d['commands'][0].update(stdout=d['commands'][0]['stdout'].replace('+0.0002','1e999'))),
        ('offset_limit',lambda d:d['commands'][0].update(stdout=d['commands'][0]['stdout'].replace('+0.0002','0.10001'))),
        ('source_changed',lambda d:d['commands'][1].update(stdout=d['commands'][1]['stdout'].replace('10.1.93.102','10.1.93.103'))),
        ('missing_source',lambda d:d['commands'][1].update(stdout='')),
        ('command_failed',lambda d:d['commands'][0].update(rc=1))]:
        bad=copy.deepcopy(valid);change(bad)
        try:parse_sample(bad,'k8s-worker01')
        except (AssertionError,ValueError):rejected.append(label)
        else:raise AssertionError('LOCAL_PARSER_FAILED_TO_REJECT_'+label)
    save(O/'NTP_PREPARED.json',{'at_kst':now(),'source_sha256':sha(Path(__file__).read_bytes()),
        'transport_sha256':sha((A/'TRANSPORT_BINDING.json').read_bytes()),'plan_sha256':sha((A/'MINIMUM_READ_PLAN.md').read_bytes()),
        'node_code_sha256':sha(NODE_CODE.encode()),'relay_code_sha256':sha(RELAY_CODE.encode()),
        'local_parser_checks':{'normal_case':1,'rejected':rejected},'runtime':'NOT_RUN','remote_files_created':0,
        'scope':'Normal chronyc observation only; no packets/egress/role apply/sync-loss/reboot/fullAC acceptance'})
    print(json.dumps({'prepared':True,'local_parser_checks':7,'runtime':'NOT_RUN'}))

def execute():
    prep=load(O/'NTP_PREPARED.json');assert sha(Path(__file__).read_bytes())==prep['source_sha256']
    assert sha((A/'TRANSPORT_BINDING.json').read_bytes())==prep['transport_sha256']
    transport=load(A/'TRANSPORT_BINDING.json');nodes=transport['nodes'];outer=transport['outer_argv']
    assert not (O/'NTP_ACTION_INTENT.json').exists(),'Prior read intent exists; inspect results, do not replay'
    save(O/'NTP_ACTION_INTENT.json',{'at_kst':now(),'source_sha256':prep['source_sha256'],'outer_argv':outer,
        'hosts':[n['host'] for n in nodes],'max_rounds':6,'max_chronyc_commands':72,'automatic_retry':False,
        'authority':'Current user instruction, existing approved read-only paths and original60s-six-point criterion',
        'remote_file_supply':0,'service_or_setting_changes':0})
    start=time.monotonic();samples={n['host']:[] for n in nodes};last={n['host']:0 for n in nodes};rounds=[];status='HOLD_NO_RETRY';error=None
    try:
      for index in range(6):
        assert time.monotonic()-start<420,'LOCAL_TOTAL_BUDGET_EXCEEDED'
        jobs=[]
        for n in nodes:
            request={k:n[k] for k in ['host','machine_id','boot_id']}
            request.update(run=O.name,sample=index,not_before_monotonic_ns=last[n['host']]+60_000_000_000 if index else 0)
            jobs.append({'host':n['host'],'argv':n['inner_argv'],'payload':'REQUEST='+repr(request)+'\n'+NODE_CODE})
        relay='EXPECTED_RELAY_BOOT='+repr(transport['relay_expected']['boot_id'])+'\nJOBS='+repr(jobs)+'\n'+RELAY_CODE
        compile(relay,'literal_relay_round','exec')
        send={'at_kst':now(),'monotonic_ns':time.monotonic_ns(),'sample':index,'relay_sha256':sha(relay.encode())}
        save(O/f'NTP_ROUND{index}_INTENT.json',send)
        p=subprocess.Popen(outer,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:out,err=p.communicate(relay.encode(),timeout=110)
        except subprocess.TimeoutExpired:
            save(O/f'NTP_ROUND{index}_UNCERTAIN.json',{'at_kst':now(),'outer_pid':p.pid,'status':'OUTER_RETURN_UNCONFIRMED_NO_NEW_REQUESTS','force_termination':False})
            raise ValueError('OUTER_RETURN_UNCONFIRMED')
        (O/f'NTP_ROUND{index}.stdout.json').write_bytes(out);(O/f'NTP_ROUND{index}.stderr').write_bytes(err)
        receipt={'at_kst':now(),'monotonic_ns':time.monotonic_ns(),'sample':index,'pid':p.pid,'actual_rc':p.returncode,
                 'stdout_sha256':sha(out),'stderr_sha256':sha(err),'returned':True}
        save(O/f'NTP_ROUND{index}_RECEIPT.json',receipt);rounds.append(receipt)
        assert p.returncode==0,'OUTER_OR_RELAY_READ_FAILED'
        data=json.loads(out);assert data['status']=='RELAY_RETURNED'
        assert len(data['results'])==6 and {r['host'] for r in data['results']}==set(samples),'NODE_SET_MISMATCH'
        pending={}
        for result in data['results']:
            assert result['ssh_rc']==0 and result['process_returned'],('INNER_READ_FAILED',result['host'])
            sample=json.loads(result['stdout']);assert sample['sample']==index and sample['run']==O.name
            parsed=parse_sample(sample,result['host'])
            prior=last[result['host']]
            if index:assert parsed['tracking_started_monotonic_ns']-prior>=60_000_000_000,'SAMPLE_INTERVAL_BELOW60S'
            pending[result['host']]={'raw':sample,'parsed':parsed}
        for host,rec in pending.items():samples[host].append(rec);last[host]=rec['parsed']['tracking_started_monotonic_ns']
        save(O/f'NTP_ROUND{index}_VERIFIED.json',{'at_kst':now(),'sample':index,'parsed':{h:v['parsed'] for h,v in pending.items()},'status':'ROUND_OBSERVED_SCOPED_NOT_FULL_AC'})
        print(json.dumps({'sample':index,'nodes':6,'offsets_ms':{h:round(v['parsed']['last_offset_ms'],6) for h,v in pending.items()},'read_only':True}),flush=True)
      status='NORMAL_SERIES_OBSERVED_SCOPED'
    except Exception as exc:error=str(exc)
    perhost={}
    for host,records in samples.items():
        stamps=[r['parsed']['tracking_started_monotonic_ns'] for r in records]
        perhost[host]={'samples':len(records),'tracking_interval_seconds':[(b-a)/1e9 for a,b in zip(stamps,stamps[1:])],
                       'tracking_span_seconds':(stamps[-1]-stamps[0])/1e9 if len(stamps)>1 else None,
                       'parsed':[r['parsed'] for r in records]}
    save(O/'NTP_RESULT.json',{'at_kst':now(),'status':status,'error':error,'rounds_returned':len(rounds),'per_host':perhost,
        'total_elapsed_seconds':time.monotonic()-start,'remote_files_created':0,'setting_service_changes':0,
        'network_egress_approval_or_sync_loss_or_reboot_or_full_AC':'NOT_ESTABLISHED_BY_THIS_OBSERVATION',
        'original300s_scope_only':True,'automatic_retry':False,'new_human_approval':False})
    print(json.dumps({'status':status,'error':error,'rounds_returned':len(rounds),'new_setting_changes':0}),flush=True)
    if error:raise SystemExit(2)

if __name__=='__main__':{'prepare':prepare,'execute':execute}[sys.argv[1]]()
