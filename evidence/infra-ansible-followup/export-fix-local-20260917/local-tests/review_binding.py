"""Proposed OFFLINE review cross-check, not a deployed receipt collector.

The caller must separately authenticate input provenance and verify all bytes,
manifests, fixture matrices, and cleanup evidence. Passing this function alone
does not accept a real CI run. Current fixtures are synthetic.
"""
def exact(value,expected,label):
    if type(value) is not type(expected) or value!=expected:
        raise ValueError('BINDING_MISMATCH:'+label)

def check(receipt,expected):
    p,r,j,c,ci,h= [receipt[k] for k in ('pr','run','job','check','ci','host')]
    sha=expected['source']
    for name,value in [('pr',p['head']['sha']),('run',r['head_sha']),
                       ('job',j['head_sha']),('check',c['head_sha']),('ci',ci['source_commit'])]:
        exact(value,sha,'source:'+name)
    exact(p['number'],expected['pr'],'pr')
    for value in [r['id'],j['run_id']]:exact(value,expected['run'],'run')
    for value in [r['run_attempt'],j['run_attempt']]:exact(value,expected['attempt'],'attempt')
    for value in [j['id'],c['id']]:exact(value,expected['job'],'job/check')
    for x in [r,j,c]:
        exact(x['status'],'completed','status')
        exact(x['conclusion'],expected['conclusion'],'conclusion')
    exact(ci['status'],expected['ci_status'],'ci_status')
    for key,value in [('GITHUB_RUN_ID',str(expected['run'])),
                      ('GITHUB_RUN_ATTEMPT',str(expected['attempt'])),
                      ('RUNNER_NAME',expected['runner_name']),
                      ('GITHUB_REPOSITORY',expected['repository'])]:
        exact(ci['github'][key],value,key)
    exact(j['runner_id'],expected['runner_id'],'job_runner_id')
    exact(j['runner_name'],expected['runner_name'],'job_runner_name')
    exact(h['runner']['agentId'],expected['runner_id'],'host_runner_id')
    exact(h['runner']['agentName'],expected['runner_name'],'host_runner_name')
    exact(h['bundle_sha256'],expected['bundle_sha256'],'bundle')
    exact(h['image_id'],expected['image_id'],'image')
    for key in ['runner','proxy','workspace']:exact(h['cleanup'][key],'REMOVED','cleanup:'+key)
    exact(receipt['pagination_complete'],True,'pagination')
    runners=receipt['runners']
    if type(runners['total_count']) is not int or type(runners['runners']) is not list:
        raise ValueError('RUNNER_LIST_TYPE')
    exact(runners['total_count'],len(runners['runners']),'runner_count')
    for row in runners['runners']:
        if type(row.get('id')) is not int or type(row.get('name')) is not str:
            raise ValueError('RUNNER_ROW_TYPE')
        if row['id']==expected['runner_id'] or row['name']==expected['runner_name']:
            raise ValueError('TARGET_RUNNER_STILL_REGISTERED')
    return True

