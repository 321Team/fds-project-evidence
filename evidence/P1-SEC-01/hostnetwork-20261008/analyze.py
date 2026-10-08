import hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parent
def load(n):return json.loads((root/n).read_text(encoding='utf-8'))
def structure(s):return [re.sub(r'\[\d+:\d+\]','[0:0]',l) for l in s.splitlines() if not l.startswith('#')]
def count(lines):return sum(int(l[1:].split(':')[0]) for l in lines if l.endswith(' -j DROP'))
checks=[]
def ck(n,v):checks.append({'name':n,'pass':bool(v)})
pre,post=load('policy-before.json'),load('policy-after.json')
for a,b in zip(pre['queries'],post['queries']):
 ck(a['command'][4]+'_queries_rc0',a['rc']==b['rc']==0)
 if a['projection'] in ('spec','endpoint','meta'):
  def clean(xs):
   v=json.loads(json.dumps(xs))
   for x in v:x['metadata'].pop('resourceVersion',None)
   return sorted(v,key=lambda x:x['metadata']['uid'])
  ck(a['command'][4]+'_unchanged',clean(a['items'])==clean(b['items']))
 elif a['projection']=='pod':
  def ids(q):return {x['metadata']['uid']:[x['metadata'].get('labels'),x['status']['podIP'],x['status']['phase']] for x in q['items']}
  ck('44_pods_UID_IP_labels_phase_preserved',len(a['items'])==44 and ids(a)==ids(b))
 elif a['projection']=='node':ck('six_nodes_ready',len(b['items'])==6 and all(any(c['type']=='Ready' and c['status']=='True' for c in n['conditions']) for n in b['items']))
for n in ('102','105','107','108'):
 a,b=load('inventory'+n+'.json'),load('post'+n+'.json')
 ck(n+'_pins_unchanged',sorted(a['pods'],key=lambda x:x['sandbox_id'])==sorted(b['pods'],key=lambda x:x['sandbox_id']))
 ck(n+'_filter_structure_unchanged',structure(a['iptables']['stdout'])==structure(b['iptables']['stdout']))
rows=[]
for name in ('control','host105','host105-continuation','host107-continuation','host108-continuation'):
 r=load(name+'.json');ck(name+'_expected_collector_exit',r['rc']==(2 if name=='host105' else 0))
 ck(name+'_filter_structure_unchanged',structure(r['filter_before'])==structure(r['filter_after']))
 for c in r['cases']:
  d=json.loads(c['stdout']);delta=count(c['after']['lines'])-count(c['before']['lines'])
  row={'record':name,'host':r['host'],'pod_uid':r['config']['pin']['metadata']['uid'],'result':d,'process_rc':c['rc'],'drop_counter_delta':delta,'runtime_guard':c.get('corroborated')}
  if name=='host105' and d['actual']=='ERROR':
   row['assessment']='EPERM_AND_HEP_DROP_PLUS1; INITIAL_TOOL_STOP_PRESERVED; syscall stage not recorded'
   ck('initial_stop_error_and_drop_preserved',c['rc']==3 and d['error']=='PermissionError:[Errno 1] Operation not permitted' and delta==1)
  else:ck(name+'_'+str(d['case']['source_port']),c['rc']==0 and (d['case']['expect']!='BLOCKED' or c['corroborated']))
  rows.append(row)
ck('20_observations',len(rows)==20)
ck('10_guard_mock_cases',all(load('guard-mock.json').values()) and len(load('guard-mock.json'))==10)
for n in ('mon-history','mon-flags','mon-preparation'):
 r=load(n+'.json');ck(n+'_forward_reaped',r['forward_reaped'] and 'error' not in r)
 if 'queries' in r:ck(n+'_API_queries_success',all(x['rc']==0 and x['api_status']=='success' for x in r['queries']))
sources={hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')}
invocations=list(root.glob('*-invocation.json'));ck('all_execution_source_hashes_present',all(load(p.name)['source_sha256'] in sources for p in invocations))
out={'checks':checks,'observations':rows,'counts':{'external_controls':2,'host_allowed':12,'host_denial_observations':6,'initial_collector_stop':1},'limits':['host-network L3/L4 observation; not node-exporter application/UID validation','HEP counters include other host traffic; Worker03 TCP DROP +10 is not all attributable to 3 test SYNs','first UDP denial lacks syscall-stage field; original rc3/collector rc2 preserved','IF05C historical queries empty, no new alert injection/delivery proof','independent REVIEW and AC acceptance pending']}
(root/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('checks',sum(x['pass'] for x in checks),'/',len(checks),'observations',len(rows),'source bindings',len(invocations));print([x for x in checks if not x['pass']]);assert all(x['pass'] for x in checks)
