"""Normal server02 credential metadata and bounded GETs only; no SSAR/POST."""
import base64, copy, datetime, hashlib, json, os, pwd, socket, stat, subprocess
from pathlib import Path

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

assert socket.gethostname() == 'k8s-control01'
assert pwd.getpwuid(os.getuid()).pw_name == 'server02' and os.getuid() == 1000
cfg = Path('/home/server02/.kube/config')
ca = Path('/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem')
out = dict(started_at_utc=now(), host=socket.gethostname(), user='server02',
           mutation=False, token_issued=False, private_credential_exported=False, queries=[])
out['paths'] = []
for p in (cfg, ca):
    s = p.lstat()
    assert not p.is_symlink() and s.st_uid in (0, os.getuid())
    assert not stat.S_IMODE(s.st_mode) & (0o077 if p == cfg else 0o022)
    out['paths'].append(dict(path=str(p), uid=s.st_uid, mode=oct(stat.S_IMODE(s.st_mode))))
out['ca_sha256'] = sha(ca.read_bytes())
assert out['ca_sha256'] == '5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c'
k = ['/usr/bin/kubectl', '--kubeconfig='+str(cfg),
     '--server=https://10.1.93.109:6443', '--certificate-authority='+str(ca), '--request-timeout=6s']
r = subprocess.run(['/usr/bin/kubectl', '--kubeconfig='+str(cfg), 'config', 'view', '--raw', '-o', 'json'], capture_output=True, timeout=8)
assert r.returncode == 0
d = json.loads(r.stdout)
ctx = next(x['context'] for x in d['contexts'] if x['name'] == d['current-context'])
cluster = next(x['cluster'] for x in d['clusters'] if x['name'] == ctx['cluster'])
user = next(x['user'] for x in d['users'] if x['name'] == ctx['user'])
assert cluster['server'] == 'https://10.1.93.109:6443'
assert not cluster.get('insecure-skip-tls-verify')
assert set(user) == {'client-certificate-data', 'client-key-data'}
assert sha(base64.b64decode(cluster['certificate-authority-data'])) == out['ca_sha256']
cert = base64.b64decode(user['client-certificate-data'])
cr = subprocess.run(['/usr/bin/openssl', 'x509', '-noout', '-subject', '-enddate', '-nameopt', 'RFC2253'], input=cert, capture_output=True, timeout=5)
assert cr.returncode == 0
out['credential'] = dict(context=d['current-context'], configured_user=ctx['user'],
    api=cluster['server'], mechanism='EXISTING_CLIENT_CERTIFICATE',
    public_certificate_sha256=sha(cert), public_metadata=cr.stdout.decode().strip())
fields = cr.stdout.decode().splitlines()[0].removeprefix('subject=').strip().split(',')
principal = next(x.removeprefix('CN=') for x in fields if x.startswith('CN='))
groups = [x.removeprefix('O=') for x in fields if x.startswith('O=')]
out['credential'].update(principal=principal, groups=groups)
del user, d, cert, r

def get(path):
    r = subprocess.run(k+['get', '--raw='+path], capture_output=True, timeout=8)
    out['queries'].append(dict(path=path, at_utc=now(), rc=r.returncode,
                              stdout_sha256=sha(r.stdout), stderr_sha256=sha(r.stderr)))
    assert r.returncode == 0 and len(r.stdout) < 4*1024*1024, path
    return json.loads(r.stdout)

out['deployments'] = []
for name in ('transaction-api', 'fds-engine'):
    d = get('/apis/apps/v1/namespaces/fds-app/deployments/'+name)
    normalized = copy.deepcopy(d['spec'])
    c = next(x for x in normalized['template']['spec']['containers'] if x['name'] == name)
    image = c['image']; c['image'] = '__AC09_IMAGE_ONLY__'
    out['deployments'].append(dict(name=name, uid=d['metadata']['uid'],
        resourceVersion=d['metadata']['resourceVersion'], generation=d['metadata']['generation'],
        image=image, replicas=d['spec']['replicas'], spec_sha256=sha(canon(d['spec'])),
        normalized_spec_sha256=sha(canon(normalized)),
        status={q:d['status'].get(q) for q in ('observedGeneration','replicas','updatedReplicas','readyReplicas','availableReplicas','unavailableReplicas')}))
out['pods'] = []
for p in get('/api/v1/namespaces/fds-app/pods')['items']:
    out['pods'].append(dict(name=p['metadata']['name'], uid=p['metadata']['uid'],
        owners=p['metadata'].get('ownerReferences'), deletionTimestamp=p['metadata'].get('deletionTimestamp'),
        node=p['spec'].get('nodeName'), ip=p['status'].get('podIP'),
        containers=[{q:c.get(q) for q in ('name','image','imageID','ready','restartCount')} for c in p['status'].get('containerStatuses',[])]))
out['finished_at_utc']=now()
print(json.dumps(out,sort_keys=True))
