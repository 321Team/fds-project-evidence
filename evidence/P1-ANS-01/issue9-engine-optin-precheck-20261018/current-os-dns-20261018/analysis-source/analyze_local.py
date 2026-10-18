"""Verify the single read's local originals; no network or remote calls."""
import ast, datetime as dt, hashlib, ipaddress, json, os, pathlib
D=pathlib.Path(__file__).absolute().parent
def p(x):return pathlib.Path(chr(92)*2+'?'+chr(92)+os.path.abspath(x))
def raw(x):return p(x).read_bytes()
def sha(x):return hashlib.sha256(raw(x)).hexdigest()
def j(x):return json.loads(raw(x))
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
def put(x,v):
 b=v.encode() if isinstance(v,str) else (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
 with p(x).open('xb') as f:f.write(b)
claim=j(D/'READ_CLAIM.json'); batch=j(D/'READ_RESULT.json'); baseline=j(D/'BASELINE.json')
binding_path=D.parent/'ntp-paired-precheck-preparation/EXACT_BINDING.json'
binding=j(binding_path)
assert sha(binding_path)==claim['binding_sha256']
assert sha(D/'node_read.py')==claim['node_reader_sha256']
assert sha(D/'BASELINE.json')==claim['baseline_sha256']
assert batch['attempted']==6 and batch['expected_hosts']==6 and not batch['harbor_stop']
for ref in j(D/'PAIRED_IDENTITY_CHECK.json')['originals']:assert sha(ref['path'])==ref['sha256']
for ref in baseline['references']:assert sha(D/'references'/ref['path'])==ref['sha256']
accepted=baseline['accepted_issue7_report'];assert sha(accepted['source'])==accepted['sha256']
assert j(accepted['source'])['overall']==accepted['overall']=='PASS_READONLY_SCOPE'
rows=[]; command_count=0; query_count=0; paired=D.parent/'ntp-paired-precheck-review/files'
for expected,receipt in zip(binding['targets'],batch['rows'],strict=True):
 host=expected['host'];folder=D/host
 assert receipt==j(folder/'RECEIPT.json') and receipt['host']==host and receipt['rc']==0
 assert sha(folder/'stdout.json')==receipt['stdout_sha256'] and sha(folder/'stderr.txt')==receipt['stderr_sha256']
 intent=j(folder/'INTENT.json');assert sha(folder/'SOURCE.py')==intent['source_sha256']
 assert raw(folder/'SOURCE.py')==('EXPECTED='+repr({k:expected[k] for k in ['host','machine_id','boot_id']})+'\n').encode()+raw(D/'node_read.py')
 ast.parse(raw(folder/'SOURCE.py')); bridge=ast.parse(raw(folder/'BRIDGE.py'))
 payload=next(ast.literal_eval(n.value) for n in bridge.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
 assert payload==raw(folder/'SOURCE.py')
 x=j(folder/'stdout.json')
 assert x['status']=='PASS_SCOPED_CURRENT_OS_DNS_READ' and x['boot_after']==x['boot_id']
 assert x['uid']==x['euid']==0 and x['configuration_mutations']==0 and x['retry'] is False
 for phase in ['before','after']:
  old=j(paired/phase/(host+'.json'))
  assert all(x[k]==old[k]==expected[k] for k in ['host','machine_id','boot_id'])
 assert x['os']['ID']=='centos' and x['os']['VERSION_ID']=='10'
 assert x['selinux_enforce']=='1' and len(x['swaps']['raw'].splitlines())==1
 assert all(x['modules'].values()) and all(v=='1' for v in x['sysctl'].values())
 assert dict(line.split('=',1) for line in x['time_properties'].splitlines())=={'Timezone':'Asia/Seoul','NTPSynchronized':'yes'}
 assert x['dns_profile']['servers']==baseline['expected']['dns']
 assert x['dns_profile']['search']==baseline['expected']['search'] and x['dns_profile']['ignore_auto']=='yes'
 assert x['files']['/etc/resolv.conf']['observed']==['search fds.internal','nameserver 10.1.93.52','nameserver 10.1.93.53']
 os_file=x['files']['/etc/os-release'];assert hashlib.sha256(os_file['observed'].encode()).hexdigest()==os_file['sha256']
 commands={c['name']:c for c in x['commands']}
 assert len(commands)==len(x['commands'])==11
 for c in commands.values():
  assert c['rc']==0 and not c['timed_out'] and c['retry'] is False
  for stream in ['stdout','stderr']:assert hashlib.sha256(c[stream].encode()).hexdigest()==c[stream+'_sha256']
  assert not c['stderr']
  command_count+=1
 route=json.loads(commands['management_route']['stdout']);assert route[0]['gateway']=='10.1.93.58'
 answers={}
 for server in baseline['expected']['dns']:
  c=commands['direct_'+server];assert c['stdout'].splitlines()==['10.1.93.109']
  answers['@'+server]=c['stdout'].splitlines();query_count+=1
 for name in ['k8s-api.fds.internal','k8s-api','github.com']:
  c=commands['system_'+name];ips=sorted({line.split()[0] for line in c['stdout'].splitlines()})
  assert ips and all(ipaddress.ip_address(ip).version==4 for ip in ips)
  if name!='github.com':assert ips==['10.1.93.109']
  answers[name]=ips;query_count+=1
 transport=[json.loads(line.split(' ',1)[1]) for line in raw(folder/'stderr.txt').decode().splitlines() if line.startswith('BRIDGE_TRANSPORT ')]
 assert any(t['phase']=='RETURNED' and t['returned'] and t['actual_rc']==0 for t in transport)
 rows.append({'host':host,'started_at_kst':x['started_at_kst'],'ended_at_kst':x['ended_at_kst'],'machine_id':x['machine_id'],'boot_id':x['boot_id'],'same_paired_boot':True,'status':x['status'],'commands':11,'dns_query_commands':5,'answers':answers,'os':x['os'],'dns_profile':x['dns_profile'],'nss_hosts':x['files']['/etc/nsswitch.conf']['observed'],'public_file_hashes':{k:v['sha256'] for k,v in x['files'].items()},'stdout_sha256':receipt['stdout_sha256'],'stderr_sha256':receipt['stderr_sha256']})
ntp_path=D.parent/'ntp-paired-precheck-review/ANALYSIS.json'
frozen=D.parent/'ntp-evidence-publication-candidate/FINAL.json'
assert sha(frozen)=='e6689b1c36a8f89b463ab439f7c2938f0afe7c98a34c0b980213e1c87273b2b6'
analysis={'at_kst':now(),'status':'PASS_SCOPED_CURRENT_OS_DNS_6','window_kst':[min(r['started_at_kst'] for r in rows),max(r['ended_at_kst'] for r in rows)],'read_batches':1,'targets':6,'matching_paired_identities':6,'commands_rc0':command_count,'dns_query_commands_rc0':query_count,'automatic_retries':0,'configuration_service_package_changes':0,'remote_temp_installs':0,'token_or_credential_actions':0,'github_writes':0,'baseline_head':baseline['references'][0]['head'],'baseline_report_sha256':accepted['sha256'],'read_claim_sha256':sha(D/'READ_CLAIM.json'),'read_result_sha256':sha(D/'READ_RESULT.json'),'paired_identity_check_sha256':sha(D/'PAIRED_IDENTITY_CHECK.json'),'rows':rows,'reused_chronyd_evidence':{'path':str(ntp_path),'sha256':sha(ntp_path),'time':'2026-10-18 19:56 KST','fresh_service_query':False},'frozen_publication_candidate':{'path':str(frozen),'sha256':sha(frozen),'modified':False},'prior_turn_remote_actions_before_current_rebind':0,'excluded':['Full issue7 CLI/hardening/API-listener rerun','Role/engine execution or global engine transition','Package inventory or directory scan','Harbor credentials/Pull and policy/service change','Whole issue9 final acceptance and human review'],'remaining':['Central may link this current scoped OS/DNS result as supplement without changing frozen candidate','Original17 human reading/verification response','Final operating caller/Collection/target selection and acceptance; no new production change required solely for this check']}
put(D/'ANALYSIS.json',analysis)
lines=['# OS/DNS 6대 현재 기준 대조 결과','',f"기준 시각: {analysis['window_kst'][0]} ~ {analysis['window_kst'][1]}",'','**판정: 제한된 OS/DNS 현재 조회 6/6 통과.** 기존 NTP paired 전후와 hostname·machine-id·boot-id가 모두 일치한다. 기존 #6/#7 기준과 현재 상태의 연결 공백을 이 범위에서 해소했다.','', '| 항목 | 실제 결과 |','|---|---|','| 조회 | 1묶음, 6대, 명령 66건 rc0, 자동 재시도 0 |','| OS 전제 | CentOS Stream 10, SELinux Enforcing, Asia/Seoul·시간 동기화, swap 0, 기존 모듈·sysctl·관리 복귀 경로 일치 |','| DNS 설정 | 10.1.93.52 → 10.1.93.53, search fds.internal, ignore-auto-dns=yes |','| 내부 응답 | DNS 두 서버 직접 조회와 FQDN·짧은 이름 조회 모두 10.1.93.109 |','| 외부 응답 | github.com IPv4 조회 성공; 주소는 관측값으로만 보존 |','| nsswitch | 6대 모두 hosts: files dns myhostname 관측. 별도 새로운 AC로 삼지 않음 |','', '원본은 각 호스트의 stdout.json·stderr.txt·INTENT.json·RECEIPT.json에 있으며 명령·시각·종료 코드·대상·SHA를 연결했다. stdout/stderr 원본 해시와 내부 명령 출력 해시를 대조했다. resolv/nsswitch는 필요한 행만 보존했으므로 전체 파일 바이트를 반출했다고 주장하지 않는다.','', '이번 실제 서버 행위는 기존 strict SSH와 sudo 경로의 한정 읽기뿐이다. 설정·서비스·패키지·원격 임시 설치·토큰·credential 변경 0. 잘못 언급했던 과거 PR87 인증·공급은 실행하지 않았고 재결속 전 실제 서버 행위도 0이었다.','', '19:56 chronyd 상태는 기존 증적을 재사용했다. 이 결과는 #7 전체 CLI·하드닝·API listener 재시험, Ansible 엔진 실제 전환, 전체 #9 인수 완료가 아니다. 기준은 기존 성공한 combined-20260914-review 및 코드 357965058cdcaa129b14c29a09b3e4e19215195f에 연결했다.','', '20:09에 동결한 발행 후보는 수정하지 않았다. 이 디렉터리를 별도 보충 증적으로 중앙에 제공한다. GitHub·공통 기록 갱신은 중앙 담당이다. 원본17 사람 열람 회신과 최종 운영 caller·Collection·대상 선택/인수는 별도로 남는다. 이번 조회를 이유로 정상 서비스의 apply/rollback 시험을 추가할 필요는 없다.','']
put(D/'CURRENT_FINDINGS.md','\n'.join(lines))
put(D/'READY.json',{'at_kst':now(),'status':analysis['status'],'analysis_path':str(D/'ANALYSIS.json'),'analysis_sha256':sha(D/'ANALYSIS.json'),'findings_path':str(D/'CURRENT_FINDINGS.md'),'findings_sha256':sha(D/'CURRENT_FINDINGS.md'),'remote_work_complete':True,'next':'Central consume supplemental evidence; no further server reads or actions in this task','human_review_complete':False,'whole_issue9_acceptance':False,'github_written':False})
manifest=[{'path':str(f.relative_to(p(D))).replace(chr(92),'/'),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(p(D).rglob('*')) if f.is_file()]
put(D/'MANIFEST.json',{'at_kst':now(),'files':manifest,'count':len(manifest)})
final={'at_kst':now(),'status':analysis['status'],'analysis_sha256':sha(D/'ANALYSIS.json'),'manifest_sha256':sha(D/'MANIFEST.json'),'manifest_files':len(manifest),'frozen':True}
put(D/'FINAL.json',final);put(D/'FINAL.sha256',sha(D/'FINAL.json')+'  FINAL.json\n')
print(json.dumps(final));print('FINAL_SHA256='+sha(D/'FINAL.json'))
