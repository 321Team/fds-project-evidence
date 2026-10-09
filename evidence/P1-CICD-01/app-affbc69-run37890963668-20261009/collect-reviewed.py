import hashlib,json,os,pathlib,subprocess,tempfile
os.umask(0o077)
home=pathlib.Path('/home/server01_cicd-runner')
checkout=home/'actions-runner/_work/infra-cicd/infra-cicd/cicd-app-37890963668-1'
head='c9eff5fb2e50a690818a3e67347ab4a1bfc88f51'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout).decode().strip()==head
assert subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=checkout)==b''
expected=dict(workflow_sha=head,source_sha='affbc69beef9967f7977d09a6fec14f7fb6c0e94',run_id='37890963668',attempt=1,input_sha256='72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3',source_repository='321Team/fds-msa')
folder=pathlib.Path(tempfile.mkdtemp(prefix='app-evidence-37890963668-',dir=home))
ep=folder/'expected.json';ep.write_text(json.dumps(expected,indent=2)+'\n')
cmd=['/usr/bin/python3','-B','tools/delivery/app_evidence.py','collect','--run-dir',str(home/'FDS_CICD_AppWorkflow.57rithja'),'--output-dir',str(folder/'collection'),'--expected',str(ep)]
r=subprocess.run(cmd,cwd=checkout,capture_output=True)
(folder/'collect.stdout').write_bytes(r.stdout);(folder/'collect.stderr').write_bytes(r.stderr);(folder/'collect.rc').write_text(str(r.returncode)+'\n')
print(json.dumps(dict(folder=str(folder),rc=r.returncode)))
print(r.stdout.decode())
assert r.returncode==0,'COLLECT_FAILED'
