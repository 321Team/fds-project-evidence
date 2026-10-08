import datetime,json,os,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent;mode=sys.argv[1]
assert mode in ('precheck','run');os.umask(0o077)
marker=root/(mode+'.once');marker.open('x').close()
code=root/'source';check=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=code,capture_output=True,timeout=10)
assert check.returncode==0,'SOURCE_DRIFT'
env=os.environ.copy();env['KC']='kubectl --kubeconfig=/etc/kubernetes/admin.conf --request-timeout=10s';env['CONFIRM']='YES'
argv=['bash',str(code/'probe.sh'),mode];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root/(mode+'.stdout')).open('xb') as out,(root/(mode+'.stderr')).open('xb') as err:
 q=subprocess.run(argv,cwd=root,env=env,stdout=out,stderr=err)
result={'mode':mode,'argv':argv,'source_commit':'d6866187ae32af286cd5d9c651cdcb4d706f5f59','started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rc':q.returncode}
(root/(mode+'.result.json')).write_text(json.dumps(result,indent=2)+'\n')
