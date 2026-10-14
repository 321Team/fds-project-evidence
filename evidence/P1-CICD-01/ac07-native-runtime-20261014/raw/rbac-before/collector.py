"""Bounded read-only SA effective binding inputs; no Secret or token request."""
import datetime as dt
import hashlib
import json
import os
import socket
import subprocess
from urllib.parse import quote

assert socket.gethostname() == 'k8s-control01' and os.geteuid() == 0
USER = 'system:serviceaccount:ci-cd:cicd-runner-sa'
GROUPS = ['system:serviceaccounts', 'system:serviceaccounts:ci-cd', 'system:authenticated']
out = {'host': socket.gethostname(), 'at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
       'classification': 'PURE_READ_PRECHECK', 'token_issued': False, 'mutation': False,
       'subject': USER, 'groups': GROUPS, 'queries': [], 'bindings': [], 'roles': []}

def get(path):
    argv = ['/usr/bin/kubectl', '--kubeconfig=/etc/kubernetes/admin.conf',
            '--request-timeout=5s', 'get', '--raw='+path]
    p = subprocess.run(argv, capture_output=True, timeout=7)
    out['queries'].append({'argv': argv, 'rc': p.returncode,
                          'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(),
                          'stderr_sha256': hashlib.sha256(p.stderr).hexdigest(),
                          'at_utc': dt.datetime.now(dt.timezone.utc).isoformat()})
    assert p.returncode == 0 and len(p.stdout) < 2*1024*1024
    return json.loads(p.stdout)

def matches(s):
    return ((s.get('kind') == 'ServiceAccount' and s.get('namespace') == 'ci-cd'
             and s.get('name') == 'cicd-runner-sa') or
            (s.get('kind') == 'User' and s.get('name') == USER) or
            (s.get('kind') == 'Group' and s.get('name') in GROUPS))

refs = set()
for kind in ['rolebindings', 'clusterrolebindings']:
    obj = get('/apis/rbac.authorization.k8s.io/v1/'+kind+'?limit=500')
    assert not obj.get('metadata', {}).get('continue') and len(obj['items']) <= 500
    out[kind+'_examined'] = len(obj['items'])
    for row in obj['items']:
        selected = [s for s in row.get('subjects', []) if matches(s)]
        if not selected:
            continue
        meta, ref = row['metadata'], row['roleRef']
        assert ref['apiGroup'] == 'rbac.authorization.k8s.io'
        assert ref['kind'] in ['Role', 'ClusterRole']
        out['bindings'].append({'kind': row['kind'],
          'metadata': {k: meta.get(k) for k in ['name','namespace','uid','resourceVersion']},
          'matching_subjects': selected, 'roleRef': ref})
        refs.add((ref['kind'], meta.get('namespace','') if ref['kind']=='Role' else '', ref['name']))
assert len(refs) <= 12
for kind, namespace, name in sorted(refs):
    path = ('/apis/rbac.authorization.k8s.io/v1/namespaces/'+quote(namespace,safe='')+
            '/roles/'+quote(name,safe='') if kind == 'Role' else
            '/apis/rbac.authorization.k8s.io/v1/clusterroles/'+quote(name,safe=''))
    row = get(path)
    out['roles'].append({'kind': row['kind'],
      'metadata': {k: row['metadata'].get(k) for k in ['name','namespace','uid','resourceVersion']},
      'rules': row.get('rules',[]), 'aggregationRule': row.get('aggregationRule')})
out['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
print(json.dumps(out, ensure_ascii=False, sort_keys=True))
