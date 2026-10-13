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
out['interface']=interface;out['connection']=connection
out['success']=all(x['rc']==0 for x in out['commands'])
print(json.dumps(out,indent=2));raise SystemExit(0 if out['success'] else 2)
