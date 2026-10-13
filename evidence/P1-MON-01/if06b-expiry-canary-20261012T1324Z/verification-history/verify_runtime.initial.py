from pathlib import Path,PurePosixPath
import datetime as dt,hashlib,io,json,re,tarfile
root=Path(__file__).resolve().parent
load=lambda n:json.loads((root/n).read_text(encoding='utf-8'))
inner=lambda n:json.loads(load(n)['stdout'])
KST=dt.timezone(dt.timedelta(hours=9))
def unpack(data):
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
        result={}
        for m in tar.getmembers():
            if m.isdir():continue
            assert m.isfile() and not PurePosixPath(m.name).is_absolute() and '..' not in PurePosixPath(m.name).parts
            assert m.name not in result
            result[m.name]=tar.extractfile(m).read()
        return result
def check_nested(data):
    files=unpack(data);flat={PurePosixPath(k).name:v for k,v in files.items()}
    assert len(flat)==len(files)
    for line in flat['SHA256SUMS'].decode().splitlines():
        sha,n=line.split('  ',1);assert hashlib.sha256(flat[n]).hexdigest()==sha
    receipt=json.loads(flat['receipt.json']);assert receipt['collection_rc']==0
    assert all(q['rc']==0 for q in receipt['queries'])
    return flat,receipt
def parsed_time(s):return dt.datetime.fromisoformat(s.strip())
caps={};host_results={}
for role,points in [('gateway',['gateway-in','gateway-out']),('monitor',['monitor-in'])]:
    file=root/(role+'-fetch.tar.gz');files=unpack(file.read_bytes())
    for line in files['field/SHA256SUMS'].decode().splitlines():
        sha,n=line.split('  ',1);key='field/'+n.split('/field/',1)[1];assert hashlib.sha256(files[key]).hexdigest()==sha
    assert files['field/post-collection.rc'].strip()==b'0'
    pre,pre_r=check_nested(files['field/pre.tar.gz']);post,post_r=check_nested(files['field/post.tar.gz'])
    names=['active-zones.stdout','links.stdout','routes.stdout','routing-rules.stdout','ip-forward.stdout'] if role=='gateway' else ['addresses.stdout','route-worker03.stdout','listeners.stdout','runtime-zones.stdout','permanent-zones.stdout']
    if role=='gateway':names += [f'{p}-{mode}-{kind}.stdout' for p in ['before','after'] for mode in ['runtime','permanent'] for kind in ['policy','zones','policies']]
    comparison={n:pre[n]==post[n] for n in names}
    if role=='gateway':
        norm=lambda b:re.sub(rb'counter packets \d+ bytes \d+',b'counter packets N bytes N',b)
        for p in ['before','after']:comparison[p+'-nft']=norm(pre[p+'-nft.stdout'])==norm(post[p+'-nft.stdout'])
    assert all(comparison.values()),comparison
    host_results[role]={'post_collection_rc':post_r['collection_rc'],'query_count':len(post_r['queries']),'configuration_unchanged':comparison,'archive_sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    if role=='monitor':
        hb=float(json.loads(post['heartbeat-age.stdout'])['data']['result'][0]['value'][1]);alerts=json.loads(post['watchdog-alerts.stdout'])['data']['alerts']
        assert hb<60 and not alerts
        host_results[role]['post_heartbeat_seconds']=hb;host_results[role]['post_alerts']=alerts
    for point in points:
        prefix='field/'+point+'/'
        caps[point]={n:files[prefix+n].decode() for n in ['cap-start.txt','cap-end.txt','cap-rc.txt','cap-stats.txt','cap.txt']}
worker=inner('worker03-export.json')['files']
for n,item in worker.items():assert hashlib.sha256(item['text'].encode()).hexdigest()==item['sha256'],n
caps['worker-out']={n:worker['worker-out/'+n]['text'] for n in ['cap-start.txt','cap-end.txt','cap-rc.txt','cap-stats.txt','cap.txt']}
cap_summary={}
for point,f in caps.items():
    assert f['cap-rc.txt'].strip()=='rc=0' and '0 packets dropped by kernel' in f['cap-stats.txt'] and 'listening on' in f['cap-stats.txt'],point
    cap_summary[point]={'start_kst':parsed_time(f['cap-start.txt']).astimezone(KST).isoformat(),'end_kst':parsed_time(f['cap-end.txt']).astimezone(KST).isoformat(),'rc':0,'dropped':0}
start=max(parsed_time(c['start_kst']) for c in cap_summary.values());end=min(parsed_time(c['end_kst']) for c in cap_summary.values())
requests={}
for action,prefix in [('443','t443'),('8443','t8443'),('post-deny','post-deny')]:
    r=inner('worker03-'+action+'.json');when=parsed_time(worker['worker/'+prefix+'.time']['text'])
    assert start<=when and when+dt.timedelta(seconds=10 if action=='443' else 8)<=end
    assert r['rc']==(0 if action=='443' else 28),r
    if action=='443':assert r['out'].strip()=='http=404 remote=10.250.10.30:443 local=10.1.93.108:45143 ssl_verify=0'
    requests[action]={'count':1,'start_kst':when.astimezone(KST).isoformat(),'rc':r['rc'],'output':r['out'].strip(),'error':r['err'].strip()}
positive={};negative={}
for point,f in caps.items():
    text=f['cap.txt'];forward=[l for l in text.splitlines() if '10.1.93.108.45143 > 10.250.10.30.443:' in l];back=[l for l in text.splitlines() if '10.250.10.30.443 > 10.1.93.108.45143:' in l]
    syn=[l for l in text.splitlines() if '10.1.93.108.45843 > 10.250.10.30.8443:' in l and 'Flags [S]' in l]
    assert forward and back,point
    positive[point]={'forward_packets':len(forward),'return_packets':len(back)};negative[point]={'syn_packets':len(syn),'lines':syn}
assert negative['worker-out']['syn_packets']>0 and negative['gateway-in']['syn_packets']>0
assert negative['gateway-out']['syn_packets']==negative['monitor-in']['syn_packets']==0
# Match the single post-deny curl's time range to a new SYN tuple at worker03.
post_time=parsed_time(requests['post-deny']['start_kst']);post_syn=[]
for line in caps['worker-out']['cap.txt'].splitlines():
    match=re.match(r'(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+) IP 10\.1\.93\.108\.(\d+) > 10\.250\.10\.30\.443: Flags \[S\]',line)
    if match:
        when=dt.datetime.fromisoformat(match[1]).replace(tzinfo=KST)
        if post_time<=when<=post_time+dt.timedelta(seconds=8):post_syn.append((match[2],line))
assert post_syn and len({port for port,line in post_syn})==1 and post_syn[0][0] not in ['45143','45843']
post_port=post_syn[0][0]
assert all('10.1.93.108.'+post_port+' > 10.250.10.30.443:' not in caps[p]['cap.txt'] for p in ['gateway-in','gateway-out','monitor-in'])
control_data=(root/'control01-evidence.tar.gz').read_bytes();control=unpack(control_data)
for line in control['EXPORT_SHA256SUMS'].decode().splitlines():
    sha,n=line.split('  ',1);assert hashlib.sha256(control[n]).hexdigest()==sha,n
journal=[json.loads(l) for l in control['journal/journal.jsonl'].splitlines()]
events=[r['event'] for r in journal]
assert events.count('CREATE_INTENT')==events.count('DELETE_INTENT')==1 and events[-1]=='ABSENT',events
supervisor=[json.loads(l) for l in control['evidence/supervisor.jsonl'].splitlines()]
created=next(r for r in supervisor if r['step']=='CREATE');trigger=next(r for r in supervisor if r['step']=='TRIGGER');final=supervisor[-1]
assert created['action']=='OWNED' and trigger['trigger']=='expiry' and final['disposition']=='ABSENT_BASELINE_UNVERIFIED'
assert final['evidence_complete_before_write'] and final['terminal_recorded']
arm=supervisor[0];assert trigger['mono']>=arm['expires_mono'] and final['mono']<arm['cleanup_deadline_mono']
delete=next(r for r in journal if r['event']=='DELETE_INTENT')
preconditions=delete['payload']['body']['preconditions']
assert preconditions['uid']==created['uid'] and preconditions['resourceVersion']==created['resource_version']
watch=inner('control01-canary-run-watch.json')['watch'];assert watch['rc']==0 and json.loads(watch['out'])['handoff_required'] is False
pre=inner('control01-policy-pre.json');post=inner('control01-policy-post.json')
policy={'all_gnp':pre['all_gnp']==post['all_gnp'],**{k:pre['objects'][k]['info']==post['objects'][k]['info'] for k in ['hep','hostgnp']}}
assert all(policy.values())
baseline={}
for phase in ['pre','during','post']:
    d=load('control01-mon-portforward-'+phase+'-remaining-read.json');raw=json.loads(d['observation']['commands'][0]['stdout']);assert raw['forwarder_stopped']
    values={q['name']:json.loads(q['raw'])['data']['result'][0]['value'][1] for q in raw['queries']}
    assert values=={'target_count':'23','target_up':'23','rw_failed_15m':'0'};baseline[phase]=values
cleanup=inner('control01-credential-cleanup.json');assert len(cleanup['objects'])==3 and all(r['readback']=='NotFound' for r in cleanup['objects']) and cleanup['token_path_absent']
out={'at_kst':dt.datetime.now(KST).isoformat(),'session_id':'20261012T2220-mon02','scope':'Phase 1 single MON IF06B canary','runtime':'PASS_WITHIN_OBSERVED_SCOPE','canary_create_count':1,'delete_intent_count':1,'manual_delete_count':0,'automatic_trigger':'expiry','created_kst':parsed_time(created['utc']).astimezone(KST).isoformat(),'absent_kst':parsed_time(final['utc']).astimezone(KST).isoformat(),'uid':created['uid'],'resource_version':created['resource_version'],'delete_preconditions':preconditions,'cleanup_after_expiry_seconds':final['mono']-arm['expires_mono'],'supervisor_disposition':final['disposition'],'baseline_after_verified_separately':True,'common_capture_window':{'start_kst':start.isoformat(),'end_kst':end.isoformat()},'captures':cap_summary,'requests':requests,'443_positive':positive,'8443_gateway_drop_evidence':negative,'post_deny':{'worker_syn_packets':len(post_syn),'source_port':post_port,'gateway_ingress_seen':False,'new_connection_blocked_after_reclaim':True},'host_post_reads':host_results,'control_policy_unchanged':policy,'baseline':baseline,'credential_cleanup':cleanup,'control_archive_sha256':hashlib.sha256(control_data).hexdigest(),'review':'EVIDENCE_REVIEW_PENDING','publication':'NOT_PUBLISHED','AC':'NOT_DECIDED','limitations':['One authorized expiry path, not every failure path or reboot recovery','Heartbeat and MON API values are sampled, not continuous monitoring','loopback MON API reads are baseline evidence only; path evidence uses four packet captures']}
(root/'RUNTIME_RESULT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['runtime','canary_create_count','automatic_trigger','created_kst','absent_kst','cleanup_after_expiry_seconds','common_capture_window','AC']},ensure_ascii=False))
