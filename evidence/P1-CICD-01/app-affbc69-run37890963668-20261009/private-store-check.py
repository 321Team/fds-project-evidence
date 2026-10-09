import datetime,json,os,pathlib,re,subprocess
base=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.57rithja/build-scan')
env={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin','HOME':str(base/'home'),'XDG_RUNTIME_DIR':'/run/user/1000','XDG_CACHE_HOME':str(base/'home/cache')}
cmd=['/usr/bin/podman','--remote=false','--root',str(base/'storage'),'--runroot',str(base/'runroot'),'--storage-driver','vfs','--tmpdir',str(base/'podman-tmp'),'--events-backend','none','ps','-a','--format','json']
r=subprocess.run(cmd,env=env,capture_output=True,timeout=30)
out=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,rc=r.returncode,containers=json.loads(r.stdout) if r.returncode==0 else None,raw_and_image_store='RETAINED_FOR_EVIDENCE_AND_LATER_HANDOFF')
out['test_summary_lines']={}
for name in ['fds-engine-unit-0.log','transaction-api-contract-0.log','fds-engine-contract-0.log']:
 out['test_summary_lines'][name]=[s for s in (base/name).read_text().splitlines() if re.search(r'\b\d+ passed\b',s)]
print(json.dumps(out,indent=2));assert r.returncode==0 and out['containers']==[]
