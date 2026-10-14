from pathlib import Path
import base64,hashlib,importlib.util,json,subprocess,datetime
R=Path(__file__).resolve().parent;W=R.parent.parent
SHA='61fbf0bf1ace1fa3a5eb983c002de2a0ddac856a'
def gh(path):return json.loads(subprocess.check_output(['gh','api',path]))
pr=gh('repos/321Team/fds-msa/pulls/30');reviews=gh('repos/321Team/fds-msa/pulls/30/reviews')
assert pr['merged'] and pr['head']['sha']==SHA
assert any(r['state']=='APPROVED' and r['commit_id']==SHA and r['user']['login']=='hayeounglee' for r in reviews)
x=gh('repos/321Team/fds-msa/contents/tools/regression/rg.py?ref='+SHA);raw=base64.b64decode(x['content'])
want='f5dee1069ab96838355cf6269dd6cdff2a08107e880594c5dad98d20424594ed'
assert hashlib.sha256(raw).hexdigest()==want
assert raw==(W/'deliverables/phase1-ha-followup-20261013-2343/supply/rg.py').read_bytes()
(R/'rg.py').write_bytes(raw)
(R/'SOURCE_REVIEW_BINDING.json').write_text(json.dumps({'read_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pr':pr['html_url'],'head':SHA,'merge':pr['merge_commit_sha'],'tool_git_blob':x['sha'],'sha256':want,'reviews':[{k:r[k] for k in ('id','state','commit_id','submitted_at','body','html_url')}|{'user':r['user']['login']} for r in reviews],'tool_change':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source='import os,socket,pathlib,hashlib,json\nassert socket.gethostname()=="edge01" and os.geteuid()==1003\nos.umask(0o077)\np=pathlib.Path("/home/svc_ansible/p1-app-20261014-1025")\np.mkdir(mode=0o700,exist_ok=False)\ns=p/"supply"\ns.mkdir(mode=0o700)\nf=s/"rg.py"\nraw='+repr(raw)+'\nwith f.open("xb") as h:h.write(raw);h.flush();os.fsync(h.fileno())\nassert hashlib.sha256(f.read_bytes()).hexdigest()=="'+want+'"\nprint(json.dumps({"host":socket.gethostname(),"uid":os.geteuid(),"path":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"mode":oct(f.stat().st_mode&0o777),"directory_mode":oct(p.stat().st_mode&0o777),"requests_sent":0}))\n'
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
r=t.run('stage-reviewed-rg','10.1.93.50',source,90,False);assert r['rc']==0
