import base64,hashlib,json,pathlib,subprocess
p=pathlib.Path('/root/if05c-20261008-oo0o4gd4');assert (p/'status.json').exists(),'STILL_RUNNING'
status=json.loads((p/'status.json').read_text());assert status['restore']=='CONFIRMED','RESTORE_NOT_CONFIRMED'
launch=json.loads((p/'launch.json').read_text());proc=pathlib.Path('/proc')/str(launch['pid'])
if proc.exists():
 stat=proc.joinpath('stat').read_text().rsplit(')',1)[1].split();assert stat[19]!=launch['starttime'] or stat[0]=='Z','PROCESS_STILL_RUNNING'
unit='if05c-recover-'+p.name.replace('if05c-','')
q=subprocess.run(['systemctl','show',unit+'.timer',unit+'.service','-p','LoadState','-p','ActiveState','-p','SubState','-p','Result'],capture_output=True,timeout=10)
files={}
for f in p.iterdir():
 if f.is_file() and not f.is_symlink():
  b=f.read_bytes();files[f.name]={'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode(),'mode':oct(f.stat().st_mode & 0o777),'size':len(b)}
print(json.dumps({'path':str(p),'status':status,'recovery_unit':{'command':q.args,'rc':q.returncode,'stdout':q.stdout.decode(),'stderr':q.stderr.decode()},'files':files}))
