import ast,datetime as dt,hashlib,json,pathlib,subprocess
D=pathlib.Path(__file__).absolute().parent
W=D.parents[4]
BINDING=D.parent/'ntp-paired-precheck-preparation/EXACT_BINDING.json'
HARBOR_BOUND=D.parent.parent/'Harbor/operational-transition/actual-bound-request'
OLD=W/'reviews/shutdown-readiness-20261018/app-k8s/shutdown-execution-integration-0305'
def p(path):return pathlib.Path(chr(92)*2+'?'+chr(92)+str(path))
def b(path):return p(path).read_bytes()
def j(path):return json.loads(b(path))
def sha(path):return hashlib.sha256(b(path)).hexdigest()
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
def put(path,v):
 raw=v if isinstance(v,bytes) else (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
 with p(path).open('xb') as f:f.write(raw)
packet=j(OLD/'PACKET.json');route=packet['transport'];binding=j(BINDING)
assert len(binding['targets'])==6 and len({h['host'] for h in binding['targets']})==6
paired_refs=[]
for host in binding['targets']:
 assert packet['nodes'][host['host']]['ip']==host['ip'], 'TRANSPORT_IP_DRIFT'
 for phase in ['before','after']:
  reference=D.parent/'ntp-paired-precheck-review/files'/phase/(host['host']+'.json')
  observed=j(reference)
  assert all(observed[k]==host[k] for k in ['host','machine_id','boot_id']), 'PAIRED_IDENTITY_DRIFT'
  assert observed['matches'] and observed['boot_stable'], 'PAIRED_IDENTITY_NOT_ACCEPTED'
  paired_refs.append({'path':str(reference),'sha256':sha(reference)})
# Extract only the already-used transport string and pure render function. No
# shutdown/execution module import, action dispatch, install or former claim.
tree=ast.parse(b(OLD/'dispatch_once.py'))
bridge_body=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='BRIDGE_BODY' for x in n.targets))
body=b(D/'node_read.py').decode();ast.parse(body)
claim={'at_kst':now(),'authorization':'Central delegated one bounded current6 OS/DNS read; same paired boot, strict existing SSH, first error no retry, no configuration/service/package/tmp/engine/Harbor changes','binding_sha256':sha(BINDING),'node_reader_sha256':sha(D/'node_read.py'),'baseline_sha256':sha(D/'BASELINE.json'),'harbor_bound_path':str(HARBOR_BOUND),'retry':False}
put(D/'READ_CLAIM.json',claim)
put(D/'PAIRED_IDENTITY_CHECK.json',{'at_kst':now(),'matched_targets':6,'originals':paired_refs,'current_runtime_identity_check_required':True})
rows=[]
for host in binding['targets']:
 if p(HARBOR_BOUND).exists():
  put(D/'HARBOR_STOP.json',{'at_kst':now(),'reason':'Harbor bound request exists; stop before new node read','path':str(HARBOR_BOUND),'actual_mutation_inferred':False});break
 node=packet['nodes'][host['host']]
 expected={k:host[k] for k in ['host','machine_id','boot_id']}
 source='EXPECTED='+repr(expected)+'\n'+body;ast.parse(source)
 inner=route['inner_argv'][:-2]+['svc_ansible@'+node['ip'],route['inner_argv'][-1]]
 bridge=('INNER='+repr(inner)+'\nPAYLOAD='+repr(source.encode())+'\n'+bridge_body).encode()
 folder=D/host['host'];p(folder).mkdir()
 put(folder/'SOURCE.py',source.encode())
 put(folder/'BRIDGE.py',bridge)
 put(folder/'INTENT.json',{'at_kst':now(),'outer':route['outer_argv'],'inner':inner,'expected':expected,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'retry':False})
 with p(folder/'stdout.json').open('xb') as out,p(folder/'stderr.txt').open('xb') as err:
  q=subprocess.Popen(route['outer_argv'],stdin=subprocess.PIPE,stdout=out,stderr=err,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
  put(folder/'SPAWN.json',{'pid':q.pid});q.stdin.write(bridge);q.stdin.close();rc=q.wait()
 receipt={'at_kst':now(),'host':host['host'],'rc':rc,'stdout_sha256':sha(folder/'stdout.json'),'stderr_sha256':sha(folder/'stderr.txt'),'retry':False}
 if rc==0:
  result=j(folder/'stdout.json');assert result['status']=='PASS_SCOPED_CURRENT_OS_DNS_READ'
  receipt.update(status=result['status'],commands=len(result['commands']))
 else:receipt['status']='READ_FAILED_NO_RETRY'
 put(folder/'RECEIPT.json',receipt);rows.append(receipt)
 print(json.dumps(receipt),flush=True)
 if rc!=0:break
put(D/'READ_RESULT.json',{'at_kst':now(),'expected_hosts':6,'attempted':len(rows),'rows':rows,'configuration_mutations':0,'cli_or_role_invocations':0,'full_issue7_rerun':False,'harbor_stop':p(D/'HARBOR_STOP.json').exists()})
