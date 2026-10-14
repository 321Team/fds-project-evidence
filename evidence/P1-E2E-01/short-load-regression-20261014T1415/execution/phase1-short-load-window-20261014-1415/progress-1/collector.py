import collections,datetime,json,os,pathlib,socket
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-short-load-202610141415/results')
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'read_only':True}
for name in ['process.json','completion.json','regression-attempt.json']:
    if (p/name).exists():out[name]=json.loads((p/name).read_bytes())
if (p/'stages.log').exists():out['stages_tail']=(p/'stages.log').read_text()[-6000:]
if (p/'requests.log').exists():
    data=(p/'requests.log').read_text();lines=data.splitlines()
    rows=[line.split() for line in lines if len(line.split())==6]
    out['flushed_request_rows']=len(rows)
    out['codes']=dict(collections.Counter(x[4] for x in rows));out['stages']=dict(collections.Counter(x[1] for x in rows))
if 'process.json' in out:
    proc=pathlib.Path('/proc')/str(out['process.json']['pid'])
    if proc.exists():
        stat=proc.joinpath('stat').read_text();out['same_process_live']=stat[stat.rfind(')')+2:].split()[19]==out['process.json']['start_ticks']
    else:out['same_process_live']=False
print(json.dumps(out))
