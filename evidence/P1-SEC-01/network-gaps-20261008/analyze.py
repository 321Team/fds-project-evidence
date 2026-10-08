import hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parent
def load(n):return json.loads((root/n).read_text(encoding='utf-8'))
def rules(s):
 return {m[3]:(int(m[1]),int(m[2])) for l in s.splitlines() if (m:=re.match(r'\[(\d+):(\d+)\] (.*)',l))}
def diff(a,b,prefix):
 a,b=rules(a),rules(b)
 return [{'rule':k,'before_packets':a[k][0],'after_packets':b[k][0],'delta_packets':b[k][0]-a[k][0]} for k in b if k in a and k.startswith('-A '+prefix+' ') and ' -j DROP' in k]
def structure(s):return [re.sub(r'\[\d+:\d+\]','[0:0]',l) for l in s.splitlines() if not l.startswith('#')]
pre,post=load('policy.json'),load('policy-post.json')
checks=[]
def check(name,value):checks.append({'name':name,'pass':bool(value)})
podmap={x['metadata']['uid']:x for q in pre['queries'] if q['projection']=='pod' for x in q['items']}
postpod={x['metadata']['uid']:x for q in post['queries'] if q['projection']=='pod' for x in q['items']}
check('all_44_pod_UIDs_preserved',set(podmap)==set(postpod) and len(podmap)==44)
check('Pod_IP_label_phase_preserved',all((x['status']['podIP'],x['status']['phase'],x['metadata'].get('labels'))==(postpod[u]['status']['podIP'],postpod[u]['status']['phase'],postpod[u]['metadata'].get('labels')) for u,x in podmap.items()))
for q in pre['queries']:
 peer=next(x for x in post['queries'] if x['command'][4]==q['command'][4]);check(q['command'][4]+'_post_query_rc0',peer['rc']==0)
 if q['projection'] in ('spec','endpoint','meta'):
  def clean(xs):
   xs=json.loads(json.dumps(xs))
   for x in xs:x['metadata'].pop('resourceVersion',None)
   return sorted(xs,key=lambda x:x['metadata']['uid'])
  check(q['command'][4]+'_unchanged',clean(q['items'])==clean(peer['items']))
 if q['projection']=='node':check('all_6_nodes_ready',len(peer['items'])==6 and all(any(c['type']=='Ready' and c['status']=='True' for c in n['conditions']) for n in peer['items']))
records=[]
for name in ['if03-positive','if03-negative','if13-control','if13-node105','if13-node107','if13-node108']:
 x=load(name+'.json');check(name+'_collector_rc0',x['rc']==0)
 check(name+'_rules_unchanged',structure(x['iptables_before']['stdout'])==structure(x['iptables_after']['stdout']))
 for c in x['cases']:
  d=json.loads(c['stdout']);d.update(record=name,pod_uid=c['pod_uid'],process_rc=c['rc']);records.append(d)
  check(name+'_'+c['pod_uid']+'_'+str(d['case']['source_port']),c['rc']==0 and d['actual']==d['case']['expect'])
for node in ('102','105','107','108'):
 a,b=load('node'+node+'-inventory.json'),load('node'+node+'-post.json')
 check(node+'_sandbox_pins_unchanged',sorted(a['pods'],key=lambda p:p['sandbox_id'])==sorted(b['pods'],key=lambda p:p['sandbox_id']))
 check(node+'_filter_rules_unchanged',structure(a['iptables']['stdout'])==structure(b['iptables']['stdout']))
if03=[];if13=[]
for node in ('105','107','108'):
 rt=json.loads(load('routes'+node+'.json')['stdout']);local={x['dst'].split('/')[0]:x['dev'] for x in rt if x.get('dev','').startswith('cali')}
 cap=load('capture-'+node+'.json');check(node+'_capture_rules_unchanged',structure(cap['before']['stdout'])==structure(cap['after']['stdout']))
 neg=next(c for c in records if c['record']=='if03-negative' and c['case']['destination'] in local)
 ip=neg['case']['destination'];changes=diff(cap['before']['stdout'],cap['after']['stdout'],'cali-tw-'+local[ip])
 syns=[l for l in cap['stdout'].splitlines() if '10.244.246.121.'+str(neg['case']['source_port'])+' > '+ip+'.' in l and 'Flags [S]' in l]
 row={'worker':cap['host'],'engine_ip':ip,'route_device':local[ip],'syn_header_rows':len(syns),'ingress_drop_rules':changes,'source_egress_only_explanation_excluded':len(syns)==3 and sum(d['delta_packets'] for d in changes)==3}
 if03.append(row);check(node+'_destination_drop_corroborated',row['source_egress_only_explanation_excluded'])
 trial=load('if13-node'+node+'.json')
 for e in trial['config']['sources']:
  ip=e['api_pod']['status']['podIP'];changes=diff(trial['iptables_before']['stdout'],trial['iptables_after']['stdout'],'cali-fw-'+local[ip])
  expected=sum(1 if c['protocol']=='UDP' else 3 for c in e['cases'] if c['expect']=='TIMEOUT')
  row={'pod':e['pin']['metadata'],'ip':ip,'device':local[ip],'egress_drop_rules':changes,'expected_probe_packets':expected,'observed_drop_packets':sum(c['delta_packets'] for c in changes)}
  if13.append(row)
  check(row['pod']['name']+'_egress_drop_matches_probe_count',row['observed_drop_packets']==expected)
out={'schema':'fds.sec-network-gap-observation.v1','checks':checks,'case_count':len(records),'cases':records,'if03_destination_corroboration':if03,'if13_egress_corroboration':if13,'scope_limits':['Host Python joined only pinned existing Pod network namespace; not application-client or container executable validation.','Counter intervals are aggregate; correlated with exact source/destination SYN headers for IF03, not per-packet kernel trace.','hostNetwork/HEP egress, IF05C firing-resolved, Probe injection NOT_RUN.','WEP API query failed (unsupported resource); route and kernel chain mapping used instead.','New collection does not retroactively validate earlier incomplete runs; independent review and AC acceptance pending.']}
(root/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('cases',len(records),'checks',sum(c['pass'] for c in checks),'/',len(checks));print([c for c in checks if not c['pass']])
raise SystemExit(0 if all(c['pass'] for c in checks) else 2)
