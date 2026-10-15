"""Preserve only four authorized Run API/log originals. No dispatch or retry."""
import concurrent.futures,json,subprocess
import runtime as r
runs=[('R1-false',38693789875),('R2-false',38693851363),('R1-true',38693979785),('R2-true',38694721511)]
dest=r.O/'github-final';dest.mkdir(exist_ok=False)
def read(pair):
 label,n=pair;d=dest/label;d.mkdir()
 outputs={}
 for name,ep in [('run.json',f'repos/321Team/infra-cicd/actions/runs/{n}'),('jobs.json',f'repos/321Team/infra-cicd/actions/runs/{n}/jobs'),('logs.zip',f'repos/321Team/infra-cicd/actions/runs/{n}/logs')]:
  p=subprocess.run(['gh','api',ep],capture_output=True,timeout=30)
  (d/name).write_bytes(p.stdout);(d/(name+'.stderr')).write_bytes(p.stderr)
  outputs[name]={'rc':p.returncode,'bytes':len(p.stdout),'sha256':r.sha(p.stdout)}
  assert p.returncode==0,(label,name,p.returncode)
 run=r.load(d/'run.json');jobs=r.load(d/'jobs.json')['jobs']
 assert run['id']==n and run['head_sha']==r.SOURCE and run['run_attempt']==1 and run['status']=='completed' and run['conclusion']=='success'
 assert len(jobs)==1 and all(j['status']=='completed' and j['conclusion']=='success' for j in jobs)
 value={'label':label,'run':n,'url':run['html_url'],'head':run['head_sha'],'attempt':run['run_attempt'],'conclusion':run['conclusion'],'jobs':[{'id':j['id'],'name':j['name'],'started_at':j['started_at'],'completed_at':j['completed_at'],'runner_id':j['runner_id'],'steps':[{'name':s['name'],'conclusion':s['conclusion']} for s in j['steps']]} for j in jobs],'originals':outputs}
 r.save(d/'receipt.json',value);return value
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:result=list(p.map(read,runs))
r.save(dest/'RUN_SUMMARY.json',result)
print(json.dumps([{'run':x['run'],'conclusion':x['conclusion'],'jobs':len(x['jobs'])} for x in result]))
