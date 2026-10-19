"""Record the single measured timeout. No additional remote calls."""
from datetime import datetime,timezone,timedelta
import hashlib,json
from pathlib import Path
D=Path('\\\\?\\'+str(Path(__file__).resolve().parent));RAW=D/'RAW'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    with (D/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
task=load(D/'CURRENT_TASK.json');v=load(RAW/'PUBLIC_CA_TLS.stdout.json');rec=load(RAW/'RECEIPT.json')
assert rec['outer_rc']==0 and v['HTTP_attempts']==1
assert v['request']['rc']==28 and v['request']['observed']['http_code']=='000'
assert v['request']['observed']['num_connects']==0
assert v['CA_unchanged_after_GET'] is True and v['certificate_candidate_count']==11
assert v['identity_before']==v['identity_before_GET']==v['identity_after_GET']
for ref in task['references']:assert sha(Path(ref['path']))==ref['sha256']
at=datetime.now(timezone(timedelta(hours=9))).isoformat()
save('RESULT.json',dict(at_kst=at,status='PUBLIC_CA_BOUND_SINGLE_CONNECT_TIMEOUT_NO_TLS_HTTP_ESTABLISHED',
    STATIC='SOURCE_COMPILED_AND_EXACT_EXISTING_TRANSPORT_BOUND',
    RUNTIME=dict(collector='COMPLETE_RC0',identity='ROOT_SUDO_USER_HOST_MACHINE_BOOT_MATCH',public_CA='PIN_MATCH_UNCHANGED',
       GET_invocations=1,curl_rc=28,HTTP_code='000',connected_sockets=0,TLS_handshake='NOT_ESTABLISHED',
       SSL_verify_result_zero_meaning='NOT_TLS_SUCCESS_WITHOUT_CONNECTION'),
    worker_identity=v['identity_before'],CA=v['selected_CA'],CA_unchanged=True,
    certificate_candidate_count=11,public_certificates_read=1,FileNotFound=10,PermissionError=0,
    request=v['request'],
    GW_correlation=dict(source='USER_CONSOLE_2026-10-19T12:30:58+09:00',
       host='mgmt-gw01',machine='6720cbd7c6494f48b7991d25f2fc1a2a',boot='7144f978-8f70-43ac-98bc-6502885ee47b',
       same_as_prior_0941_0943=True,GW_SSH_calls=0,continuous_boot_through_request='NOT_MEASURED'),
    actual_local_remote_ips='EMPTY_NO_CONNECTED_SOCKET',requested_source='10.1.93.108',requested_network_destination='10.250.10.30:443',
    TLS_server_identity_requested='10.1.93.54',network_success=False,HTTP_delivery_confirmed=False,
    specific_drop_rule_or_failure_location='NOT_ATTRIBUTED',
    retry=False,new_trust_import=False,temporary_trust_files=0,server_mutations=0,
    private_keys_or_auth_configuration_reads=0,credential_API_or_health_requests=0,
    APP_MON_retests=0,GitHub_common_status_writes=0,full_AC18_19_acceptance=False,owner_approval=False,
    allowance='Single root GET invocation consumed; no automatic rerun',report='RESULT.md'))
files=[p for p in D.rglob('*') if p.is_file() and p.name!='FINAL_BINDING.json']
save('FINAL_BINDING.json',dict(at_kst=at,status='MEASURED_NEGATIVE_RESULT_RETURN_COMPLETE',
    files=[dict(path=p.relative_to(D).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)],
    primary_references_rechecked=True,original_files_modified=False,GET_invocations=1,retry=False))
print(json.dumps(dict(status='MEASURED_NEGATIVE_RESULT_RETURN_COMPLETE',curl_rc=28,HTTP='000',
    GET_invocations=1,retry=False,report=str(D/'RESULT.md')),ensure_ascii=False))
