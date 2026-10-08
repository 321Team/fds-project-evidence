import ast,json,pathlib
root=pathlib.Path(__file__).resolve().parent
prior=root.parent/'sec-if03-20261008-0344/build-probes.py'
if not prior.exists():prior=root.parent/'network-gaps-20261008/build-probes.py'
tree=ast.parse(prior.read_text(encoding='utf-8'))
child=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='child' for t in n.targets))
policy=json.loads((root/'policy-before.json').read_text())
pods={x['metadata']['uid']:x for q in policy['queries'] if q['projection']=='pod' for x in q['items']}
runner=r'''import datetime,hashlib,json,os,pathlib,socket,subprocess,sys,time
CONFIG=__CONFIG__
CHILD=__CHILD__
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity():
 p=CONFIG['pin'];v=pathlib.Path('/proc')/str(p['pid'])
 assert v.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==p['starttime'],'PID_CHANGED'
 assert os.readlink(v/'ns/net')==p['netns'],'NETNS_CHANGED'
 assert v.joinpath('cgroup').read_text()==p['cgroup'],'CGROUP_CHANGED'
 assert (p['netns']==os.readlink('/proc/1/ns/net'))==CONFIG['host_network'],'NETWORK_KIND_CHANGED'
def table():
 p=subprocess.run(['iptables-save','-c','-t','filter'],capture_output=True,timeout=8)
 assert p.returncode==0,p.stderr.decode(errors='replace')
 return p.stdout.decode()
def chain_snapshot():
 raw=table();chain=CONFIG['egress_chain']
 return {'utc':now(),'raw_filter_sha256':hashlib.sha256(raw.encode()).hexdigest(),'chain':chain,'lines':[l for l in raw.splitlines() if '-A '+chain+' ' in l] if chain else []}
r={'host':socket.gethostname(),'source_sha256':os.environ['COLLECTOR_SHA256'],'started_utc':now(),'config':CONFIG,'cases':[]};rc=0;fd=None;begin=time.monotonic()
try:
 assert os.geteuid()==0 and socket.gethostname().split('.')[0]==CONFIG['host'];identity()
 r['filter_before']=table()
 if CONFIG['egress_chain']:assert 'GlobalNetworkPolicy fds-k8s-host-'+CONFIG['host']+' egress' in r['filter_before']
 fd=os.open('/proc/%d/ns/net'%CONFIG['pin']['pid'],os.O_RDONLY);assert os.readlink('/proc/self/fd/%d'%fd)==CONFIG['pin']['netns'];identity()
 for c in CONFIG['cases']:
  assert time.monotonic()-begin<90,'TIME_BUDGET';identity();before=chain_snapshot()
  cmd=['nsenter','--net=/proc/self/fd/%d'%fd,'--','python3','-I','-B','-c',CHILD,json.dumps(c)]
  p=subprocess.run(cmd,capture_output=True,timeout=7,pass_fds=(fd,))
  r['cases'].append({'command':cmd,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace'),'before':before,'after':chain_snapshot()})
  identity();assert p.returncode==0,'UNEXPECTED_RESULT_STOP'
except Exception as e:r['stop']=type(e).__name__+':'+str(e);rc=2
finally:
 if fd is not None:os.close(fd)
 try:r['filter_after']=table()
 except Exception as e:r['post_error']=str(e);rc=2
 r['finished_utc']=now();r['rc']=rc;print(json.dumps(r,indent=2))
sys.exit(rc)
'''
for n in ('102','105','107','108'):
 inv=json.loads((root/('inventory'+n+'.json')).read_text())
 p=next(x for x in inv['pods'] if x['metadata']['name'].startswith('node-exporter' if n!='102' else 'coredns-589f44dc88-f8l54'))
 pod=pods[p['metadata']['uid']];hn=n!='102'
 assert bool(pod['spec'].get('hostNetwork'))==hn and pod['status']['phase']=='Running'
 assert any(c['type']=='Ready' and c['status']=='True' for c in pod['status']['conditions'])
 ip=pod['status']['podIP'];assert not hn or ip=='10.1.93.'+n
 def case(protocol,dest,port,expect,i):return {'protocol':protocol,'source_ip':ip,'source_port':56101+i,'destination':dest,'port':port,'expect':expect,'qname':'example.com'}
 if hn:
  gnp=next(x for q in policy['queries'] if q['command'][4]=='globalnetworkpolicies.crd.projectcalico.org' for x in q['items'] if x['metadata']['name']=='fds-k8s-host-'+inv['host'])
  assert gnp['spec']['egress'][-1]['action']=='Deny'
  for proto in ('TCP','UDP'):
   assert any(x.get('protocol')==proto and x.get('action')=='Allow' and x.get('destination')=={'nets':['10.1.93.52/32','10.1.93.53/32'],'ports':[53]} for x in gnp['spec']['egress'])
  lines=[l for l in inv['iptables']['stdout'].splitlines() if 'GlobalNetworkPolicy fds-k8s-host-'+inv['host']+' egress' in l];assert len(lines)==1
  chain=lines[0].split(' -A ')[1].split()[0]
  cases=[case('UDP',ip,53,'DNS_REPLY',i) for i,ip in enumerate(('10.1.93.52','10.1.93.53'))]
  cases += [case('TCP',ip,53,'CONNECTED',i+2) for i,ip in enumerate(('10.1.93.52','10.1.93.53'))]
  cases += [case('UDP','8.8.8.8',53,'TIMEOUT',4),case('TCP','1.1.1.1',443,'TIMEOUT',5)]
 else:
  chain='';cases=[case('UDP','8.8.8.8',53,'DNS_REPLY',6),case('TCP','1.1.1.1',443,'CONNECTED',7)]
 config={'host':inv['host'],'pin':p,'api_pod':pod,'host_network':hn,'egress_chain':chain,'cases':cases}
 source=runner.replace('__CONFIG__',repr(config)).replace('__CHILD__',repr(child));compile(source,'probe'+n,'exec')
 (root/('probe'+n+'.py')).write_text(source,encoding='utf-8',newline='\n')
print('STATIC: pinned 3 hostNetwork sources / 18 cases and 2 external controls; no configuration writes')
