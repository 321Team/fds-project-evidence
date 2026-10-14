#!/usr/bin/env python3
"""Offline, read-only verification; never executes collected scripts or runtime."""
import collections
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def child(root, name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and bool(path.parts)
            and all(p not in ('.', '..') for p in path.parts)
            and '\\' not in name and ':' not in name, 'Unsafe relative path')
    target = root.joinpath(*path.parts)
    require(not target.is_symlink(), 'Symlink payload')
    return target


def verify(root):
    summary = load(root / 'AUDIT_RESULT.json')
    total = manifests = 0
    for run, case in summary['cases'].items():
        folder = root / 'runs' / run
        metadata = load(folder / 'COLLECTION_METADATA.json')
        receipt = load(folder / 'collection/receipt.json')
        require(receipt['rc'] == 0 and metadata['read_only']
                and metadata['new_runtime'] is False, 'Collection scope/rc')
        require(receipt['source_sha256'] == digest((folder / 'collection/collector.py').read_bytes()), 'Collector hash')
        require(receipt['stderr_sha256'] == digest((folder / 'collection/stderr.txt').read_bytes()), 'Collector stderr hash')
        require(receipt['stdout_sha256'] == metadata['transport_stdout_sha256'], 'Transport reference')
        raw, hashes = {}, {}
        for name, item in metadata['files'].items():
            data = child(folder / 'originals', name).read_bytes()
            require(len(data) == item['bytes'] and digest(data) == item['sha256'], 'Original mismatch: ' + name)
            raw[name], hashes[name] = data, digest(data)
            total += 1
        require(len(raw) == case['original_files_copied'], 'File count')
        for name, item in metadata['hash_only'].items():
            if item.get('present'):
                hashes[name] = item['sha256']
                if item.get('expected_sha256') is not None:
                    require(item['sha256'] == item['expected_sha256'] and item['expected_match'], 'Hash-only record')
        if run == '35683010080':
            supplement = load(root / 'collection-history/scan-archive-supplement/stdout.json')
            require(supplement['expected_match'], 'Supplement hash')
            hashes[supplement['relative']] = supplement['sha256']
        checks = []
        for name, data in raw.items():
            if name != 'SHA256SUMS' and not name.endswith('/SHA256SUMS'):
                continue
            for row in data.decode().splitlines():
                value, relative = row.split('  ', 1)
                full = str(PurePosixPath(name).parent / relative)
                require(hashes.get(full) == value, 'Original manifest: ' + full)
                checks.append({'manifest': name, 'path': full, 'sha256': value,
                               'match': True, 'raw_copied': full in raw})
        require(checks == load(folder / 'MANIFEST_VERIFICATION.json'), 'Manifest receipt')
        require(len(checks) == case['manifest_entries_matched'], 'Manifest count')
        manifests += len(checks)
        api = load(folder / 'github/run.json')
        require(api['run_attempt'] == 1 and str(api['id']) == run
                and api['head_sha'] == case['workflow_sha'] == metadata['expected_workflow_sha'], 'GitHub identity')
        require(api['conclusion'] == case['github_conclusion'], 'GitHub conclusion')
        require(int((folder / 'github/read-rc.txt').read_text()) != 0
                and '410' in (folder / 'github/read-stderr.txt').read_text(), 'Expired GitHub log classification')
        result = json.loads(raw['result.json'])
        reports = load(folder / 'REPORT_ALLOWLIST_SUMMARY.json')
        for name, report in reports.items():
            counts = dict(collections.Counter(v['Severity'] for v in report['findings']))
            require(counts == report['counts'], 'Derived report counts')
            require(name in metadata['hash_only'], 'Derived report original reference')
            require(report['source_sha256'] == metadata['hash_only'][name]['sha256'], 'Derived report source hash')
        if 'APP_WORKFLOW' not in result:
            require(result['TRIVY_CI_TOOLCHECK'] == result['DB_MISSING_ERROR_TEST'] == 'PASS', 'Toolcheck classification')
            require(int(raw['findings.exit-code.txt']) == 10 and int(raw['missing-db.exit-code.txt']) == 1, 'Toolcheck rc')
            require(b'--skip-db-update cannot be specified on the first run' in raw['missing-db.log'], 'Actual missing DB error')
            require(reports['findings.json']['counts'] == result['finding_counts'] == {'HIGH': 15, 'CRITICAL': 6}, 'Toolcheck findings')
        else:
            build = json.loads(raw['build-scan/result.json'])
            scan = json.loads(raw['build-scan/scan/result.json'])
            db = json.loads(raw['build-scan/scan/db/result.json'])
            require(result['context']['run_id'] == run and result['context']['workflow_sha'] == api['head_sha'], 'Runtime identity')
            require(result['build_result_sha256'] == hashes['build-scan/result.json']
                    and result['handoff_sha256'] == hashes['handoff.json']
                    and build['scan_result_sha256'] == hashes['build-scan/scan/result.json']
                    and scan['db_result_sha256'] == hashes['build-scan/scan/db/result.json'], 'Receipt chain')
            for prefix, item in [('', result), ('build-scan/', build)]:
                for step in item['steps']:
                    require(hashes[prefix + step['name'] + '.log'] == step['log_sha256'], 'Step log hash')
            require(db['DB_PREFLIGHT'] == 'PASS' and result['PUSH'] == result['DEPLOY'] == 'NOT_EXECUTED', 'Runtime boundary')
            require(int(raw['build-scan/scan/transaction-api/exit-code.txt']) == case['scanner_exit'], 'Scanner rc')
            require(result['APP_WORKFLOW'] == case['workflow_result']
                    and scan['IMAGE_SCAN'] == case['scanner_result']
                    and scan['error_code'] == case['scanner_reason'], 'Negative classification')
            if run == '35588577241':
                require(scan['images'] == {} and case['scanner_exit'] == 1, 'Error case')
            else:
                require(set(scan['images']) == {'transaction-api'}, 'Unscanned image boundary')
                require(scan['images']['transaction-api']['counts'] == reports['build-scan/scan/transaction-api/report.json']['counts'] == {'HIGH': 57, 'CRITICAL': 3}, 'Vulnerability case')
                prior = root.parent / 'run-35683010080-attempt-1/received-20260924/submitted'
                old = load(prior / 'manifest.json')['payloads']
                require(len(old) == 56, 'Old payload count')
                for name, entry in old.items():
                    require(hashes.get(name) == entry['sha256'], 'Old payload receipt comparison: ' + name)
                old_jsons = [p for p in prior.rglob('*.json') if p.name != 'manifest.json']
                require(len(old_jsons) == 6, 'Prior submitted JSON count')
                for path in old_jsons:
                    require(raw[path.relative_to(prior).as_posix()] == path.read_bytes(), 'Prior JSON bytes')
        require(case['deployment_images_at_case'] == 'NOT_COLLECTED' and case['new_runtime'] is False, 'Historical scope')
    require(total == summary['total_original_files_copied'] == 148 and manifests == 35, 'Totals')
    require(summary['ac05'] == 'PARTIAL_IMAGE_PRESERVATION_MISSING', 'AC05 remains incomplete')
    print(json.dumps({'original_files_rehashed': total, 'original_manifest_entries': manifests,
                      'old_payload_collection_records_matched': 56,
                      'server_hash_only_bytes_reread_by_this_verifier': False,
                      'new_runtime': False, 'ac05': summary['ac05']}, ensure_ascii=False))


if __name__ == '__main__':
    directory = Path(__file__).resolve().parent
    if os.name == 'nt' and not str(directory).startswith('\\\\?\\'):
        directory = Path('\\\\?\\' + str(directory))
    verify(directory)
