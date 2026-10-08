
import datetime,hashlib,json,os,pathlib,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if not ('2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'):raise SystemExit('STOP window')
if socket.gethostname()!='edge01':raise SystemExit('STOP host/euid')
out={'schema':'fds.app-metrics.readonly.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],'files':[],'containers':[],'no_config_change':True,'euid':os.geteuid(),'execution_account':'svc_ansible (unprivileged HTTP only)'}

code="\nimport datetime,hashlib,http.client,json,socket,time\ntargets=[('10.1.93.105', 30080, '/metrics'), ('10.1.93.105', 30080, '/readyz'), ('10.1.93.107', 30080, '/metrics'), ('10.1.93.107', 30080, '/readyz'), ('10.1.93.108', 30080, '/metrics'), ('10.1.93.108', 30080, '/readyz'), ('10.1.93.50', 80, '/metrics'), ('10.1.93.50', 80, '/readyz')]\nrows=[]\nfor host,port,path in targets:\n t=time.monotonic();row={'target':host,'port':port,'path':path,'method':'GET','started_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'proxy_used':False,'redirect_followed':False}\n c=http.client.HTTPConnection(host,port,timeout=4)\n try:\n  c.request('GET',path,headers={'User-Agent':'fds-readonly-evidence/20261009','Connection':'close'})\n  r=c.getresponse();body=r.read(262145)\n  row.update(status=r.status,content_type=r.getheader('Content-Type'),body_bytes_read=len(body),truncated=len(body)>262144,body_sha256=hashlib.sha256(body).hexdigest(),help_lines=sum(line.startswith(b'# HELP ') for line in body.splitlines()),type_lines=sum(line.startswith(b'# TYPE ') for line in body.splitlines()))\n except Exception as e:row.update(error=type(e).__name__+': '+str(e))\n finally:c.close()\n row['elapsed_seconds']=round(time.monotonic()-t,6);rows.append(row)\nprint(json.dumps({'requests':rows}))\n"
p=subprocess.run(['python3','-I','-c',code],capture_output=True,timeout=60)
out['queries'].append({'label':'edge-direct-and-nginx','command':['python3','-I','-c',code],'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
out['finished_at_kst']=now();print(json.dumps(out))
