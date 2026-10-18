"""Finalize already verified local outputs after Windows path-prefix failure.
No network, remote read, or modification of previously written evidence.
"""
import datetime as dt,hashlib,json,pathlib
D=pathlib.Path(__file__).absolute().parent
def extended(x):
 s=str(x);prefix=chr(92)*2+'?'+chr(92)
 return pathlib.Path(s if s.startswith(prefix) else prefix+s)
def sha(x):return hashlib.sha256(extended(x).read_bytes()).hexdigest()
def read(x):return json.loads(extended(x).read_bytes())
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
def put(name,value):
 data=value.encode() if isinstance(value,str) else (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 with extended(D/name).open('xb') as f:f.write(data)
a=read(D/'ANALYSIS.json');r=read(D/'READY.json')
assert a['status']=='PASS_SCOPED_CURRENT_OS_DNS_6' and a['commands_rc0']==66 and a['dns_query_commands_rc0']==30
assert sha(D/'ANALYSIS.json')==r['analysis_sha256']
assert sha(D/'CURRENT_FINDINGS.md')==r['findings_sha256']
for row in a['rows']:
 for stream in ['stdout','stderr']:
  name='stdout.json' if stream=='stdout' else 'stderr.txt'
  assert sha(D/row['host']/name)==row[stream+'_sha256']
put('LOCAL_ANALYSIS_RECEIPT.json',{'at_kst':now(),'analysis_and_ready_written':True,'all_analysis_assertions_completed_before_manifest':True,'initial_local_script_rc':1,'failure':'Manifest hashing prepended Windows extended-path prefix twice; no remote failure','failed_script_sha256':sha(D/'analyze_local.py'),'remedy':'Separate local finalizer verifies saved outputs and emits manifest without rewriting them','remote_retries':0})
root=extended(D)
files=[{'path':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(root.rglob('*')) if f.is_file()]
put('MANIFEST.json',{'at_kst':now(),'files':files,'count':len(files)})
for row in read(D/'MANIFEST.json')['files']:assert sha(D/row['path'])==row['sha256']
final={'at_kst':now(),'status':a['status'],'analysis_sha256':sha(D/'ANALYSIS.json'),'manifest_sha256':sha(D/'MANIFEST.json'),'manifest_files':len(files),'frozen':True,'remote_reads':6,'remote_retries':0,'local_finalization':'VERIFIED','github_written':False}
put('FINAL.json',final);put('FINAL.sha256',sha(D/'FINAL.json')+'  FINAL.json\n')
print(json.dumps(final));print('FINAL_SHA256='+sha(D/'FINAL.json'))
