"""One authorized read-only collection per target. Failures are not retried."""
import ast,json
import collect_readonly as c
plan=[('edge','edge01','edge-read-02'),('control','k8s-control01','d04-control-01'),('grafana','k8s-control01','grafana-read-01')]+[('boot',h,'boot-'+h+'-01') for h in c.HOSTS if h!='edge01']
for mode,host,label in plan: ast.parse(c.source(mode,host))
results=[]
for mode,host,label in plan:
 rc=c.collect(mode,host,label); results.append({'mode':mode,'host':host,'label':label,'rc':rc})
 print(json.dumps(results[-1]),flush=True)
(c.ROOT/'COLLECTION_RESULT.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
