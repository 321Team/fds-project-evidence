"""Approved one-run TBS controller; no workflow, token, or host configuration changes."""
import base64, datetime as dt, hashlib, json, pathlib, shlex, subprocess, sys
OUT=pathlib.Path(__file__).parent
SHA='147f760298dd4a683ea58f2a887483769352b97d'
REPO='321Team/infra-cicd'
WF='app-test-build-scan.yml'
SSH=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01']
INNER=['/usr/bin/ssh','-F','/dev/null','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ControlPath=none','-o','UpdateHostKeys=no','server01_cicd-runner@10.250.10.20']
def now(): return dt.datetime.now(dt.timezone.utc)
def save(name,data):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f: f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def api(path): return json.loads(subprocess.check_output(['gh','api',path],timeout=35))
def remote(label,source):
    dest=OUT/label;dest.mkdir(exist_ok=False)
    (dest/'collector.py').write_bytes(source)
    argv=INNER+[shlex.join(['/usr/bin/python3','-B','-I','-S','-'])]
    bridge=('import subprocess,sys\np=subprocess.run('+repr(argv)+',input='+repr(source)+',capture_output=True,timeout=45)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    start=now().isoformat()
    p=subprocess.run(SSH+['/usr/bin/python3 -B -I -S -'],input=bridge,capture_output=True,timeout=55)
    (dest/'stdout.json').write_bytes(p.stdout);(dest/'stderr.txt').write_bytes(p.stderr)
    save(label+'/receipt.json',{'started_at_utc':start,'finished_at_utc':now().isoformat(),'rc':p.returncode,'argv':SSH+['/usr/bin/python3 -B -I -S -'],'inner_argv':argv,'collector_sha256':hashlib.sha256(source).hexdigest(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()})
    assert p.returncode==0, 'REMOTE_FAILED_NO_EXECUTION'
    return json.loads(p.stdout)
def github_precheck():
    main=api('repos/'+REPO+'/commits/main')['sha']; assert main==SHA,'MAIN_CHANGED'
    runners=api('repos/'+REPO+'/actions/runners')['runners']
    selected=[r for r in runners if r['name']=='cicd-runner01'];assert len(selected)==1
    runner=selected[0];assert runner['status']=='online' and runner['busy'] is False,'RUNNER_BUSY'
    assert {'self-hosted','Linux','X64','p1-cicd','onprem','podman'}<={x['name'] for x in runner['labels']}
    runs=api('repos/'+REPO+'/actions/workflows/'+WF+'/runs?per_page=10')['workflow_runs']
    assert all(r['status']=='completed' for r in runs),'TBS_ACTIVE'
    files=[]
    for expected in json.loads((OUT/'PREPARATION_READBACK.json').read_text())['files']:
        obj=api('repos/'+REPO+'/contents/'+expected['path']+'?ref='+SHA)
        digest=hashlib.sha256(base64.b64decode(obj['content'])).hexdigest()
        assert digest==expected['sha256'],'SOURCE_CHANGED'
        files.append({'path':expected['path'],'sha256':digest,'git_blob':obj['sha']})
    secrets=api('repos/'+REPO+'/actions/secrets')['secrets']
    assert 'CICD_APP_SOURCE_READ_TOKEN' in {s['name'] for s in secrets},'SOURCE_SECRET_MISSING'
    ci=api('repos/'+REPO+'/actions/runs/38393360302')
    assert ci['head_sha']==SHA and ci['conclusion']=='success'
    return {'as_of_utc':now().isoformat(),'main':main,'runner':{'name':runner['name'],'busy':runner['busy'],'status':runner['status']},'files':files,'source_secret_registered':True,'ci':'SUCCESS','recent_run_ids':[r['id'] for r in runs]}
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='github':
        data=github_precheck();save(sys.argv[2],data);print(json.dumps(data))
    elif mode=='remote':
        print(json.dumps(remote(sys.argv[2],(OUT/sys.argv[3]).read_bytes())))
    elif mode=='dispatch':
        auth=json.loads((OUT/'USER_AUTHORIZATION.json').read_text(encoding='utf-8'))
        assert auth['workflow_sha']==SHA and auth['max_new_runs']==1 and auth['push_deploy_authorized'] is False
        assert not (OUT/'DISPATCH_INTENT_NO_RETRY.json').exists(), 'QUOTA_ALREADY_CONSUMED'
        assert api('repos/'+REPO+'/actions/secrets/CICD_APP_SOURCE_READ_TOKEN')['updated_at']==auth['source_secret_updated_at'], 'SOURCE_SECRET_METADATA_CHANGED'
        assert dt.datetime.fromisoformat(auth['window_start_kst'])<=now()<dt.datetime.fromisoformat(auth['job_start_deadline_kst'])
        remote_data=json.loads((OUT/sys.argv[2]/'stdout.json').read_text())
        assert remote_data['ready'] is True and (now()-dt.datetime.fromisoformat(remote_data['finished_at_utc'])).total_seconds()<150
        data=github_precheck();save('DISPATCH_PRECHECK.json',data)
        assert dt.datetime.fromisoformat(auth['window_start_kst'])<=now()<dt.datetime.fromisoformat(auth['job_start_deadline_kst'])
        save('DISPATCH_INTENT_NO_RETRY.json',{'at_utc':now().isoformat(),'sha':SHA,'prior_run_ids':data['recent_run_ids'],'quota_consumed_on_attempt':True})
        p=subprocess.run(['gh','workflow','run',WF,'--repo',REPO,'--ref','main'],capture_output=True,timeout=35)
        save('DISPATCH_RESPONSE.json',{'at_utc':now().isoformat(),'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')})
        print(json.dumps({'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}))
    else: raise SystemExit('Unsupported mode')
