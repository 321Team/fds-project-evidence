import json, os, sys
d = sys.argv[1]
def L(f):
    return json.load(open(os.path.join(d, f)))
print('== namespace PSA 라벨')
for it in L('ns.json')['items']:
    lb = it['metadata'].get('labels', {})
    print(it['metadata']['name'], {k.split('/')[-1]: v for k, v in lb.items() if 'pod-security' in k})
print('== monitoring-api Pod 생성 시각')
for it in L('pods-api.json')['items']:
    print(it['metadata']['name'], it['metadata']['creationTimestamp'])
print('== monitoring-api NetworkPolicy egress')
for it in L('np-api.json')['items']:
    s = it['spec']
    outs = []
    for r in s.get('egress') or []:
        ports = ','.join(str(p.get('port')) for p in r.get('ports') or [])
        tos = []
        for t in r.get('to') or []:
            if 'ipBlock' in t:
                tos.append(t['ipBlock']['cidr'])
            else:
                tos.append(json.dumps(t.get('podSelector', {}).get('matchLabels', {}), sort_keys=True))
        outs.append('%s:%s' % ('+'.join(tos), ports))
    print('np', it['metadata']['name'], s['podSelector'].get('matchLabels'), outs)
print('== RBAC: monitoring-node에서 Workload를 만들거나 수정할 수 있는 주체')
CR = {}; RO = {}; CRB = []; RB = []
for it in L('rbac.json')['items']:
    k = it['kind']; m = it['metadata']
    if k == 'ClusterRole':
        CR[m['name']] = it.get('rules') or []
    elif k == 'Role':
        RO[(m['namespace'], m['name'])] = it.get('rules') or []
    elif k == 'ClusterRoleBinding':
        CRB.append(it)
    elif k == 'RoleBinding':
        RB.append(it)
NS = 'monitoring-node'
G = {'pods': '', 'replicationcontrollers': '', 'deployments': 'apps', 'daemonsets': 'apps', 'statefulsets': 'apps', 'replicasets': 'apps', 'jobs': 'batch', 'cronjobs': 'batch'}
def hits(rules):
    out = []
    for r in rules:
        res = set(r.get('resources') or [])
        verbs = set(r.get('verbs') or [])
        grp = set(r.get('apiGroups') or [])
        vs = ['*'] if '*' in verbs else sorted(verbs & {'create', 'update', 'patch'})
        if not vs:
            continue
        rs = [x for x, g in G.items() if (x in res or '*' in res) and (g in grp or '*' in grp)]
        if rs:
            out.append(','.join(rs) + ':' + ','.join(vs))
    return out
def subj(s):
    return s['kind'] + '/' + ((s.get('namespace') + '/') if s.get('namespace') else '') + s['name']
rows = []
for b in CRB:
    h = hits(CR.get(b['roleRef']['name'], []))
    for s in (b.get('subjects') or []) if h else []:
        rows.append(('CRB', b['metadata']['name'], b['roleRef']['name'], subj(s), ' | '.join(h)))
for b in RB:
    if b['metadata']['namespace'] == NS:
        rr = b['roleRef']
        rules = CR.get(rr['name'], []) if rr['kind'] == 'ClusterRole' else RO.get((NS, rr['name']), [])
        h = hits(rules)
        for s in (b.get('subjects') or []) if h else []:
            rows.append(('RB', b['metadata']['name'], rr['name'], subj(s), ' | '.join(h)))
def base(r):
    n = r[3].split('/')[-1]
    return n.startswith('system:') or n.startswith('kubeadm:')
print('-- 기본(system:/kubeadm:) 외 주체')
for r in sorted(set(x for x in rows if not base(x))):
    print('*', *r)
print('-- 기본 주체:', sorted(set(r[3] for r in rows if base(r))))
print('-- monitoring-node RoleBinding 전체')
for b in RB:
    if b['metadata']['namespace'] == NS:
        print(b['metadata']['name'], b['roleRef']['name'], [subj(s) for s in b.get('subjects') or []])
