"""Pin reviewed source locally and collect bounded read-only prerequisites."""
import concurrent.futures,hashlib,importlib.util,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
REPO=ROOT/'phase1-work-20261013/cicd-ac07-rbac-20261014'
MERGE='c373f1d7a8e6e84548180839098c34e9a1262eef'
HEAD='4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70'
def save(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def main():
    names=['deploy_token_lifecycle.py','deploy_native_probe.py','deploy_cp1_access.py',
           'deploy_binding.py','deploy_credential.py','deploy_transport.py','deploy_adapter.py','delivery_gate.py']
    source=OUT/'source';source.mkdir(exist_ok=False)
    files={};binding=[]
    for name in names+['transfer_native_probe.py']:
        path='tools/delivery/'+name;raw=git('show',MERGE+':'+path)
        assert raw==git('show',HEAD+':'+path)
        blob=git('rev-parse',MERGE+':'+path).decode().strip()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
        compile(raw,path,'exec');(source/name).write_bytes(raw)
        binding.append({'name':name,'git_blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'reviewed_head_bytes_equal':True})
        if name in names:files[name]={'git_blob':blob,'content':raw.decode()}
    bundle=(json.dumps({'schema':'P1-CICD-token-lifecycle-source-1','source_sha':MERGE,'files':files},
                      sort_keys=True,separators=(',',':'))+'\n').encode()
    assert bundle.count(b'\n')==1 and len(bundle)<1024*1024
    (OUT/'lifecycle-source.json').write_bytes(bundle)
    save(OUT/'SOURCE_BINDING.json',{'reviewed_head':HEAD,'merge':MERGE,'files':binding,'bundle_sha256':hashlib.sha256(bundle).hexdigest()})
    s=importlib.util.spec_from_file_location('collect',OUT.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
    key='/home/server01_ansible/.ssh/p1_ansible_ed25519';old=OUT.parent/'p1-delivery-runner-20261013'
    tasks=[('rbac-before','10.1.93.102','svc_ansible',key,True,OUT.parent/'p1-cicd-ac07-execution-20261014/read_rbac.py',[]),
           ('cp1-auth-before','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,old/'auth_path_read.py',['cp1']),
           ('runner-auth-before','10.250.10.20','server01_cicd-runner',key,False,old/'auth_path_read.py',['runner']),
           ('app-before','10.1.93.102','svc_ansible',key,True,REPO/'tools/trivy/capture_app_state.py',[]),
           ('runner-before','10.250.10.20','server01_cicd-runner',key,False,OUT.parent/'p1-cicd-scan-negative-execution-20261014/runner_read.py',[])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(m.remote,tasks))
    save(OUT/'READ_PRECHECK_RESULTS.json',results);print(json.dumps(results))
    assert all(r['rc']==0 and r['stderr_bytes']==0 for r in results)
if __name__=='__main__':main()
