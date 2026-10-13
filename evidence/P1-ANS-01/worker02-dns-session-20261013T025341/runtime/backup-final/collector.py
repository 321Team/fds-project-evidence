EXPECTED={'path': '/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions/w02-20261013T024523-85942d67/original-resolver.json', 'session_id': 'w02-20261013T024523-85942d67', 'sha256': 'ce6295bcc88b8129003f50cb4cbd4be36d18c32413bbcf46e9926a552a1ea5b2', 'snapshot_written': True, 'source_sha': '0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea'}
import hashlib,json,os,pathlib,stat,datetime
assert os.uname().nodename=='k8s-worker02' and os.geteuid()==0
p=pathlib.Path(EXPECTED['path']);st=p.lstat();raw=p.read_bytes();d=json.loads(raw)
assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600
assert hashlib.sha256(raw).hexdigest()==EXPECTED['sha256'] and d['session_id']==EXPECTED['session_id'] and d['source_sha']==EXPECTED['source_sha']
assert stat.S_IMODE(p.parent.stat().st_mode)==0o700 and p.parent.stat().st_uid==0
assert set(os.listxattr(p,follow_symlinks=False))<= {'security.selinux'}
assert d['original']=={'interface':'ens160','connection':'fds-k8s-worker02','ipv4_dns':'10.1.93.52,10.1.93.53','ipv4_dns_search':'fds.internal','ipv4_ignore_auto_dns':'yes'}
print(json.dumps({'status':'BACKUP_BYTES_METADATA_VERIFIED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':EXPECTED['sha256'],'path':str(p),'size':len(raw),'uid':st.st_uid,'gid':st.st_gid,'mode':'0600','parent_mode':'0700','selinux_context':os.getxattr(p,'security.selinux').decode().rstrip('\0'),'data':d,'raw_utf8':raw.decode()}))
