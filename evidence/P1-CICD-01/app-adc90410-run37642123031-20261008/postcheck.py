import datetime,json,os,pathlib,subprocess
base=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow._6zedcc5')
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_dir':str(base),'retained_raw_evidence':True}
active=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  if p.stat().st_uid!=1000 or int(p.name)==os.getpid():continue
  args=(p/'cmdline').read_bytes().split(b'\0')
  if any(a.endswith((b'app_workflow.py',b'build_scan.py',b'scan_images.py')) for a in args):active.append(p.name)
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
lock=base.parent/'FDS_CICD_AppWorkflow.lock'
inode=str(lock.stat().st_ino)
rows=[s for s in pathlib.Path('/proc/locks').read_text().splitlines() if any(x.endswith(':'+inode) for x in s.split())]
out['active_app_pids']=active;out['workflow_lock_held']=bool(rows)
r=subprocess.run(['podman','ps','-a','--format','json'],capture_output=True)
out['default_store_ps_rc']=r.returncode
out['default_store_containers']=json.loads(r.stdout) if r.returncode==0 else None
print(json.dumps(out,indent=2));assert not active and not rows and r.returncode==0
