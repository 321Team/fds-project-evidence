import concurrent.futures, datetime, json, pathlib, subprocess, sys
OUT=pathlib.Path(__file__).resolve().parent
prefix=sys.argv[1]
targets={
 'pr81':'repos/321Team/infra-cicd/pulls/81',
 'reviews81':'repos/321Team/infra-cicd/pulls/81/reviews?per_page=100',
 'main':'repos/321Team/infra-cicd/commits/main',
 'merge-ci':'repos/321Team/infra-cicd/actions/runs/38529245862',
 'cicd-runners':'repos/321Team/infra-cicd/actions/runners',
 'cicd-active':'repos/321Team/infra-cicd/actions/runs?status=in_progress&per_page=100',
 'cicd-queued':'repos/321Team/infra-cicd/actions/runs?status=queued&per_page=100',
 'ansible-active':'repos/321Team/infra-ansible/actions/runs?status=in_progress&per_page=100',
 'ansible-queued':'repos/321Team/infra-ansible/actions/runs?status=queued&per_page=100',
 'cicd11':'repos/321Team/infra-cicd/issues/11',
 'cicd11-comments':'repos/321Team/infra-cicd/issues/11/comments?per_page=100&page=2',
 'baseline16':'repos/321Team/fds-project-baseline/issues/16',
 'baseline16-comments':'repos/321Team/fds-project-baseline/issues/16/comments?per_page=100&page=2',
 'baseline19-comments':'repos/321Team/fds-project-baseline/issues/19/comments?per_page=100&page=4',
}
def get(item):
    label,endpoint=item
    p=subprocess.run(['gh','api',endpoint],capture_output=True,timeout=30)
    assert p.returncode==0,(label,p.returncode)
    path=OUT/(prefix+'-'+label+'.json')
    with path.open('xb') as f:f.write(p.stdout)
    v=json.loads(p.stdout)
    if label.endswith(('active','queued')):return label,{'total_count':v['total_count'],'runs':[{k:r[k] for k in ('id','name','status','head_sha')} for r in v['workflow_runs']]}
    if label=='cicd-runners':return label,[{k:r[k] for k in ('id','name','status','busy')} for r in v['runners']]
    if label=='main':return label,v['sha']
    if label=='pr81':return label,{k:v[k] for k in ('state','merged','merge_commit_sha','merged_at')}
    if label=='merge-ci':return label,{k:v[k] for k in ('id','status','conclusion','head_sha')}
    return label,'saved'
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    for label,v in pool.map(get,targets.items()): print(label,json.dumps(v,ensure_ascii=False),flush=True)
