import datetime,hashlib,json,os,pathlib,socket,subprocess,sys
root=pathlib.Path('/root/sec01-probe-20261008-98hudpso')
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-control01'
os.umask(0o077)
now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat('2026-10-08T00:35:00+00:00'),'START_WINDOW_EXPIRED'
pre=json.loads((root/'precheck.result.json').read_text());assert pre['rc']==0
assert (now-datetime.datetime.fromisoformat(pre['finished_utc'])).total_seconds()<300,'STALE_PRECHECK'
assert not (root/'run.once').exists() and not (root/'run-launch.json').exists(),'ALREADY_STARTED'
for proc in pathlib.Path('/proc').glob('[0-9]*'):
 try: raw=(proc/'cmdline').read_bytes()
 except OSError: continue
 assert not (b'/probe.sh\0' in raw or b'/backup.sh\0' in raw),'EXISTING_TEST_PROCESS'
q=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=root/'source',capture_output=True,timeout=10);assert q.returncode==0
with (root/'run-launch.stdout').open('xb') as out,(root/'run-launch.stderr').open('xb') as err:
 p=subprocess.Popen([sys.executable,str(root/'job.py'),'run'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
result={'pid':p.pid,'utc':now.isoformat(),'root':str(root),'window_comment':'https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6049479655','job_sha256':hashlib.sha256((root/'job.py').read_bytes()).hexdigest()};(root/'run-launch.json').write_text(json.dumps(result));print(json.dumps(result))
