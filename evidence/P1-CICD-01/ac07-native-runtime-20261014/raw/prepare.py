import concurrent.futures
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
REPO = ROOT/'phase1-work-20261013/cicd-ac07-rbac-20261014'
MERGE = '9fb2e2dcac8682a89c4b7c267c833ae8d9aaeb18'
HEAD = 'db8230d7580820c55ab388680a1e87fc3e45db0a'

def save(path, obj):
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode())

def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args])

def main():
    files = {}
    binding = []
    names = ['deploy_native_probe.py','deploy_cp1_access.py','deploy_binding.py',
             'deploy_credential.py','deploy_transport.py','deploy_adapter.py','delivery_gate.py']
    source = OUT/'source'
    source.mkdir(exist_ok=False)
    for name in names + ['transfer_native_probe.py']:
        path = 'tools/delivery/'+name
        raw = git('show',MERGE+':'+path)
        assert raw == git('show',HEAD+':'+path)
        blob = git('rev-parse',MERGE+':'+path).decode().strip()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == blob
        compile(raw,path,'exec')
        (source/name).write_bytes(raw)
        binding.append({'name':name,'git_blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),
                        'reviewed_head_bytes_equal':True})
        if name in names:
            files[name]={'git_blob':blob,'content':raw.decode()}
    bundle = (json.dumps({'schema':'P1-CICD-native-probe-source-1','source_sha':MERGE,
                          'files':files},ensure_ascii=True,sort_keys=True,separators=(',',':'))+'\n').encode()
    assert bundle.count(b'\n') == 1 and len(bundle)<1024*1024
    (OUT/'native-source.json').write_bytes(bundle)
    save(OUT/'SOURCE_BINDING.json',{'reviewed_head':HEAD,'merge':MERGE,'files':binding,
                                   'bundle_sha256':hashlib.sha256(bundle).hexdigest()})
    path = ROOT/'deliverables/phase1-deploy-after-push-20261013-2244/collect.py'
    spec = importlib.util.spec_from_file_location('collect_ac07',path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    key='/home/server01_ansible/.ssh/p1_ansible_ed25519'
    old=ROOT/'deliverables/p1-delivery-runner-20261013'
    tasks=[('rbac-before','10.1.93.102','svc_ansible',key,True,OUT/'read_rbac.py',[]),
           ('cp1-auth-before','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,old/'auth_path_read.py',['cp1']),
           ('runner-auth-before','10.250.10.20','server01_cicd-runner',key,False,old/'auth_path_read.py',['runner']),
           ('app-before','10.1.93.102','svc_ansible',key,True,REPO/'tools/trivy/capture_app_state.py',[]),
           ('runner-before','10.250.10.20','server01_cicd-runner',key,False,ROOT/'deliverables/p1-cicd-scan-negative-execution-20261014/runner_read.py',[])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(mod.remote,tasks))
    save(OUT/'READ_PRECHECK_RESULTS.json',results)
    print(json.dumps(results))
    assert all(r['rc']==0 and r['stderr_bytes']==0 for r in results)

if __name__ == '__main__':
    main()
