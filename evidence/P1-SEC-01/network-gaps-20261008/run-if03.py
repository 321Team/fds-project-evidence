import concurrent.futures,datetime,hashlib,json,pathlib,shlex,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
def transport(src,node):
 payload=(root/src).read_bytes();sha=hashlib.sha256(payload).hexdigest()
 inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.'+node,'sudo -n env COLLECTOR_SHA256='+sha+' python3 -']
 return payload,['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)],sha
assert not (root/'if03-positive.json').exists()
p=subprocess.run([sys.executable,str(root/'transport-node.py'),'if03-positive.py','108','if03-positive'])
assert p.returncode==0,'POSITIVE_FAILED_STOP'
captures=[]
try:
 for node in ('105','107','108'):
  payload,cmd,sha=transport('capture-if03.py',node)
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  p.stdin.write(payload);p.stdin.close()
  captures.append((node,p,cmd,sha,datetime.datetime.now(datetime.timezone.utc).isoformat()))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  lines=list(pool.map(lambda x:x[1].stdout.readline(),captures))
 assert all(x==b'CAPTURE_READY\n' for x in lines),repr(lines)
 print('3 captures ready',flush=True)
 q=subprocess.run([sys.executable,str(root/'transport-node.py'),'if03-negative.py','102','if03-negative'])
finally:
 for node,p,cmd,sha,start in captures:
  out=p.stdout.read();err=p.stderr.read();p.wait(timeout=35)
  (root/('capture-'+node+'.json')).write_bytes(out)
  (root/('capture-'+node+'.stderr')).write_bytes(err)
  (root/('capture-'+node+'-invocation.json')).write_text(json.dumps({'command':cmd,'rc':p.returncode,'source_sha256':sha,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n',encoding='utf-8')
  print('capture',node,'rc',p.returncode,'bytes',len(out))
