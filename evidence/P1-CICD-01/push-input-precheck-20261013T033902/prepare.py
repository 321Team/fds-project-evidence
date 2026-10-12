from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import base64, datetime, hashlib, json, subprocess

P = Path(__file__).resolve().parent
SHA = '2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
def digest(raw): return hashlib.sha256(raw).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def query(item):
    name, endpoint = item
    result = subprocess.run(['gh', 'api', endpoint], capture_output=True, timeout=45)
    assert result.returncode == 0, name
    data = json.loads(result.stdout)
    (P / 'github' / (name + '.json')).write_bytes(result.stdout)
    return {'name': name, 'endpoint': endpoint, 'at_utc': now(), 'sha256': digest(result.stdout)}, data

if __name__ == '__main__':
    (P / 'github').mkdir(exist_ok=False)
    (P / 'source').mkdir(exist_ok=False)
    jobs = [('main', 'repos/321Team/infra-cicd/commits/main'),
            ('secrets', 'repos/321Team/infra-cicd/actions/secrets'),
            ('runners', 'repos/321Team/infra-cicd/actions/runners'),
            ('queued', 'repos/321Team/infra-cicd/actions/runs?status=queued&per_page=100'),
            ('running', 'repos/321Team/infra-cicd/actions/runs?status=in_progress&per_page=100'),
            ('app-approval', 'repos/321Team/infra-cicd/issues/comments/6074515472'),
            ('harbor-ac02-history', 'repos/321Team/fds-project-baseline/issues/comments/5947371286'),
            ('harbor-tls', 'repos/321Team/fds-project-baseline/issues/comments/6128729026')]
    paths = ['tools/trivy/' + n + '.py' for n in ('verify_runner', 'prepare_db', 'oci_archive', 'scan_images')]
    paths += ['tools/delivery/delivery_gate.py', '.github/workflows/app-push.yml']
    jobs += [('source-' + Path(path).name, 'repos/321Team/infra-cicd/contents/' + path + '?ref=' + SHA) for path in paths]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(query, jobs))
    receipts = []
    binding = []
    for receipt, data in results:
        receipts.append(receipt)
        if receipt['name'] == 'main': assert data['sha'] == SHA
        if receipt['name'].startswith('source-'):
            raw = base64.b64decode(data['content'])
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            assert blob == data['sha']
            (P / 'source' / Path(data['path']).name).write_bytes(raw)
            binding.append({'commit': SHA, 'path': data['path'], 'git_blob': blob, 'sha256': digest(raw)})
    (P / 'GITHUB_RECEIPTS.json').write_text(json.dumps(receipts, indent=2) + '\n')
    (P / 'SOURCE_BINDING.json').write_text(json.dumps(binding, indent=2) + '\n')
    print(json.dumps({'github_reads': len(receipts), 'fixed_source_files': len(binding), 'main': SHA}))
