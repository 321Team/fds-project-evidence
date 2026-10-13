"""Diagnose before issuance using already-staged, exact approved modules."""
import datetime,hashlib,json,os,pathlib,pwd,re,socket,stat,sys
assert socket.gethostname()=='k8s-control01' and pwd.getpwuid(os.getuid()).pw_name=='server02'
expected={'deploy_native_probe.py':'dec7e2aeb9b2706f8abdad234c755530f4b5655d95c658a8a9335720640e4091','deploy_cp1_access.py':'529490b0421c0b438be341eded8aa40a3374da680315bed3e896eaf1eacce1ca','deploy_binding.py':'9983b53890b9ac251328529726012168bea6b3fbc14667a719ccb87c1955aafb','deploy_credential.py':'f098b3525a466e1045eebb739af0560a4a4bfe0a708d5aba5e323e3095dfb967','deploy_transport.py':'7417327e92c59aadce5dadb983151db8cc6a7c3509e6ecefa40058776b4e9fa6','deploy_adapter.py':'24dcdaa3dc21720e4d2100dbfcb5ac77050a2b81f0a8435604f232aff3ce5684','delivery_gate.py':'bc9d178d6a6b6faa6a1d65e99b5511f1f0e19b7fb5a53cadcc846d3bd4184fd0'}
out={'host':socket.gethostname(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'token_request_called':False,'token_review_called':False,'resource_mutation':False,'source_commit':'2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7','scope':'existing NativeAccess config/SA/SelfSubjectAccessReview only; no issue() or review()'}
matches=[]
for d in pathlib.Path.home().glob('FDS_NativeProbeSource.*'):
    if d.is_symlink() or not d.is_dir():continue
    if d.stat().st_uid!=os.getuid() or stat.S_IMODE(d.stat().st_mode)!=0o700:continue
    if all((d/n).is_file() and not (d/n).is_symlink() and hashlib.sha256((d/n).read_bytes()).hexdigest()==h for n,h in expected.items()):matches.append(d)
out['matching_source_directories']=[str(d) for d in matches]
if matches:
    d=max(matches,key=lambda p:p.stat().st_mtime_ns);out['source_directory']=str(d)
    sys.dont_write_bytecode=True;sys.path.insert(0,str(d))
    import deploy_native_probe as n
    stage='constructor'
    try:
        access=n.NativeAccess('/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem','5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c')
        stage='preflight';out['sa_uid']=access.preflight();out['result']='PREISSUE_PREFLIGHT_PASS'
    except Exception as e:
        code=str(e);out.update(result='PREISSUE_PREFLIGHT_BLOCKED',stage=stage,error_code=code if re.fullmatch('[A-Z][A-Z0-9_]{1,90}',code) else 'DIAGNOSTIC_FAILED')
else:out['result']='NO_STAGED_SOURCE'
print(json.dumps(out,sort_keys=True))
