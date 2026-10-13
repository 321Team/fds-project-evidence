from read_transport import run
source='''import datetime,hashlib,json,os,pathlib,shutil,socket
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
roots=['/usr/bin','/usr/sbin','/usr/local/bin','/usr/local/sbin','/opt/bin','/opt/fds/bin','/root/bin']
out={'host':socket.gethostname(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path_lookup':shutil.which('crictl'),'roots':[]}
for root in roots:
 p=pathlib.Path(root)
 row={'root':root,'exists':p.is_dir(),'matches':[]}
 if p.is_dir():
  for x in p.iterdir():
   if 'crictl' in x.name.lower():
    st=x.stat();row['matches'].append({'path':str(x),'resolved':str(x.resolve()),'mode':oct(st.st_mode),'uid':st.st_uid,'size':st.st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest() if x.is_file() and st.st_size<100000000 else None})
 out['roots'].append(row)
out['status']='COLLECTED_REVIEW_REQUIRED';print(json.dumps(out))
'''
run('control01-cri-path-read','10.1.93.102',source)
