import datetime,json,os,pathlib,subprocess
assert os.uname().nodename=='k8s-worker02','WRONG_HOST'
def cmd(argv):
 r=subprocess.run(argv,capture_output=True,text=True,timeout=15)
 return {'argv':argv,'rc':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':os.uname().nodename,'uid':os.getuid(),'scope':'read-only DNS/service preparation; no backup creation or NM mutation','commands':[]}
routes=cmd(['ip','-j','route','show','default']);out['commands'].append(routes)
assert routes['rc']==0
interfaces=sorted({r['dev'] for r in json.loads(routes['stdout']) if 'dev' in r});assert len(interfaces)==1
interface=interfaces[0]
c=cmd(['nmcli','--get-values','GENERAL.CONNECTION','device','show',interface]);out['commands'].append(c);assert c['rc']==0
connection=c['stdout'].strip();assert connection and connection!='--'
for args in [['nmcli','--get-values','ipv4.dns,ipv4.dns-search,ipv4.ignore-auto-dns','connection','show',connection],['nmcli','--get-values','IP4.DNS','device','show',interface],['systemctl','is-active','NetworkManager','kubelet','containerd'],['getenforce']]:out['commands'].append(cmd(args))
out['resolv_conf_selected']=[s for s in pathlib.Path('/etc/resolv.conf').read_text().splitlines() if s.split() and s.split()[0] in {'nameserver','search','domain'}]
out['boot']=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
out['addresses']=cmd(['ip','-j','-4','address','show',interface])
for args in [['getent','ahostsv4','k8s-api.fds.internal'],['getent','ahostsv4','k8s-api'],['getent','ahostsv4','github.com'],['dig','+time=2','+tries=1','+short','@10.1.93.52','k8s-api.fds.internal','A'],['dig','+time=2','+tries=1','+short','@10.1.93.53','k8s-api.fds.internal','A']]:out['commands'].append(cmd(args))
import socket,stat,hashlib
with socket.create_connection(('10.1.93.109',6443),timeout=3):out['api_tcp_6443']=True
out['state_paths']=[]
for name in ['/var/lib/fds-change','/var/lib/fds-change/CR-P1-ANS-01-01','/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions']:
 p=pathlib.Path(name)
 if os.path.lexists(p):
  s=p.lstat();out['state_paths'].append({'path':name,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'symlink':p.is_symlink(),'xattrs':os.listxattr(p,follow_symlinks=False)})
 else:out['state_paths'].append({'path':name,'exists':False})
out['interface']=interface;out['connection']=connection
out['success']=all(x['rc']==0 for x in out['commands'])
print(json.dumps(out,indent=2));raise SystemExit(0 if out['success'] else 2)
