import sys
import control_runtime as r
action=sys.argv[1];assert action in ['capture','capture2','443','8443','post-deny','read','read2','export']
body='''import hashlib,time
base=Path('/home/svc_ansible/if06b-20261012T2220-mon02');action=ACTION
ca='/etc/pki/ca-trust/source/anchors/fds-root-ca.crt'
if action in ['capture','capture2']:
 if action=='capture':base.mkdir(mode=0o700,exist_ok=False)
 else:assert base.is_dir() and base.stat().st_uid==0
 work=base/('worker' if action=='capture' else 'worker-pre2');work.mkdir()
 cap=base/('worker-out' if action=='capture' else 'worker-out-2');cap.mkdir()
 for label,argv in [('route-pre',['ip','-4','route','get','10.250.10.30']),('ports-pre',['ss','-H','-tan','( sport = :45143 or sport = :45843 )'])]:
  p=subprocess.run(argv,capture_output=True,text=True);(work/(label+'.out')).write_text(p.stdout);(work/(label+'.rc')).write_text(str(p.returncode))
  assert p.returncode==0
  if label=='route-pre':assert 'src 10.1.93.108' in p.stdout and 'dev ens160' in p.stdout
  else:assert not p.stdout.strip(),'SOURCE_PORT_BUSY'
 assert hashlib.sha256(Path(ca).read_bytes()).hexdigest()=='20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f'
 (work/'ca-sha.txt').write_text(hashlib.sha256(Path(ca).read_bytes()).hexdigest()+'  '+ca+'\\n')
 (cap/'cap-start.txt').write_text(dt.datetime.now(dt.timezone.utc).isoformat())
 with (cap/'cap.txt').open('x') as out,(cap/'cap-stats.txt').open('x') as err:
  p=subprocess.Popen(['timeout','--signal=INT','--preserve-status','300','tcpdump','-nn','-tttt','-l','-i','ens160','(host 10.1.93.108 and host 10.250.10.30) and ((tcp and (port 443 or port 8443)) or icmp)'],stdout=out,stderr=err)
  (cap/'cap-pid.txt').write_text(str(p.pid))
  rc=p.wait(timeout=310)
 (cap/'cap-rc.txt').write_text('rc='+str(rc)+'\\n');(cap/'cap-end.txt').write_text(dt.datetime.now(dt.timezone.utc).isoformat())
 print(json.dumps({'action':action,'rc':rc,'stats':(cap/'cap-stats.txt').read_text()}))
elif action=='export':
 import hashlib
 assert (base/'worker-out/cap-end.txt').exists()
 print(json.dumps({'files':{p.relative_to(base).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text':p.read_text()} for p in base.rglob('*') if p.is_file()}}))
elif action in ['read','read2']:
 cap=base/('worker-out' if action=='read' else 'worker-out-2')
 print(json.dumps({p.name:p.read_text() for p in cap.iterdir() if p.is_file()}))
else:
 work=base/'worker';prefix='t'+action if action!='post-deny' else action
 assert work.is_dir() and not (work/(prefix+'.time')).exists(),'REQUEST_ALREADY_SENT'
 assert hashlib.sha256(Path(ca).read_bytes()).hexdigest()=='20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f'
 (work/(prefix+'.time')).write_text(dt.datetime.now(dt.timezone.utc).isoformat())
 args=['curl','--disable','--cacert',ca,'--noproxy','*','--connect-timeout','5','--max-time','10' if action=='443' else '8','--retry','0']
 if action in ['443','8443']:args+=['--local-port','45143' if action=='443' else '45843']
 args+=['-sS','-o','/dev/null','-w','http=%{http_code} remote=%{remote_ip}:%{remote_port} local=%{local_ip}:%{local_port} ssl_verify=%{ssl_verify_result}\\n',
        'https://10.250.10.30:8443/' if action=='8443' else 'https://10.250.10.30/']
 p=subprocess.run(args,capture_output=True,text=True,timeout=15)
 (work/(prefix+'.out')).write_text(p.stdout);(work/(prefix+'.err')).write_text(p.stderr);(work/(prefix+'.rc')).write_text(str(p.returncode)+'\\n')
 print(json.dumps({'action':action,'rc':p.returncode,'out':p.stdout,'err':p.stderr}))
'''.replace('action=ACTION','action='+repr(action))
r.run('worker03-'+action,body,timeout=330 if action in ['capture','capture2'] else 30,target='worker')
