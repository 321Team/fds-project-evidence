"""Verify received bytes and compare observed recovery to the reviewed contract."""
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SHARE = Path('D:/FDS-Isolated-Lab/harbor-app-recovery-result-20261009-150720')
BASE = SHARE / 'RECOVERY_RESULT'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
manifest = (BASE / 'SHA256SUMS').read_bytes()
assert sha(manifest) == (SHARE / 'EXPORT_DONE').read_text().strip()
listed = set()
for line in manifest.decode().splitlines():
    expected, name = line.split('  ', 1)
    p = (BASE / name).resolve()
    assert p.is_relative_to(BASE.resolve()) and p.is_file() and not p.is_symlink()
    assert name not in listed and sha(p.read_bytes()) == expected, name
    listed.add(name)
assert listed == {p.name for p in BASE.iterdir() if p.name != 'SHA256SUMS'}
r = json.loads((BASE / 'result.json').read_bytes())
receipt = json.loads((BASE / 'RECEIPT.json').read_bytes())
original = json.loads((BASE / 'original-a3-result.json').read_bytes())
assert sha((BASE / 'result.json').read_bytes()) == receipt['result_sha256']
assert r['source_sha256'] == '2178a40b948ccc87ee00b3aad29f0b6c4b7054ac4485f0cd588d75d46b46cb0c'
assert receipt['collector_sha256'] == 'a80f1afa2e801c81bba00c0c38497e492b85930c7e198b562d5dcf2611673e59'
assert sha((BASE / 'original-a3-result.json').read_bytes()) == '5df896fd9f501cbac82e1091c6368160d79dbca34baf651681f766f331102fa7'
assert sha((BASE / 'original-a3.claim').read_bytes()) == 'fc00ce44c9aaa35b3cb15d150db208a560f0873532736fb4daafe870c3afa175'
assert r['status'] == 'MANUAL_RECOVERY_HEALTHY_REVIEW_REQUIRED'
assert r['AUTOSTART'] == r['SYSLOG_INGESTION'] == 'NOT_TESTED' and r['AC_CLOSE'] == 'NOT_EVALUATED'
assert r['before'] == original['after']
assert all(row['status'] == 'running' and row['health'] == 'healthy' for row in r['after'].values())
assert len(r['after']) == 10
assert all(c['rc'] == 0 for c in r['commands'])
order = ['postgresql', 'redis', 'registry', 'registryctl', 'core', 'portal', 'jobservice', 'trivy-adapter', 'proxy']
starts = [c for c in r['commands'] if c['name'].startswith('start-')]
assert [c['name'][6:] for c in starts] == r['started_services'] == order
for c, service in zip(starts, order):
    assert c['argv'] == ['docker', '--host=unix:///var/run/docker.sock', 'start', r['before'][service]['id']]
    assert c['finished_epoch'] - c['started_epoch'] < 60
    assert (BASE / c['stdout_file']).read_text().strip() == r['before'][service]['id']
assert r['profile_before'] == r['profile_after']


def metadata(rows):
    copied = copy.deepcopy(rows)
    for row in copied.values():
        row.pop('health'); row.pop('status')
        row['mounts'].sort(key=lambda m: (m['Destination'], m['Source']))
    return copied


def nft_clean(value):
    if isinstance(value, list):
        return [nft_clean(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            if key == 'handle':
                continue
            if key == 'counter' and isinstance(child, dict):
                child = {k: v for k, v in child.items() if k not in ('packets', 'bytes')}
            out[key] = nft_clean(child)
        return out
    return value


assert metadata(r['before']) == metadata(r['after'])
states, units, tables = 0, 0, 0
for c in r['commands']:
    if c['name'] == 'state':
        rows = [json.loads(line) for line in (BASE / c['stdout_file']).read_text().splitlines()]
        assert len(rows) == 10
        assert metadata({row['service']: row for row in rows}) == metadata(r['before'])
        states += 1
    elif c['name'] == 'docker-unit':
        unit = dict(line.split('=', 1) for line in (BASE / c['stdout_file']).read_text().splitlines())
        assert unit['InvocationID'] == original['unit_after']['InvocationID']
        assert unit['ActiveState'] == 'active' and unit['SubState'] == 'running'
        assert all('fds-harbor-ac04-guard.service' in unit[k].split() for k in ('Requires', 'After'))
        units += 1
    elif c['name'] == 'ac04':
        rows = json.loads((BASE / c['stdout_file']).read_bytes())['nftables']
        assert nft_clean([row for row in rows if 'metainfo' not in row]) == r['firewall_before']
        tables += 1
private = json.loads((BASE / 'PRIVATE_FILE_METADATA.json').read_bytes())
private_rows = {row['file']: row for row in private if 'sha256' in row}
for name in listed & private_rows.keys():
    assert sha((BASE / name).read_bytes()) == private_rows[name]['sha256']
assert len(private_rows) == receipt['private_file_count']
assert receipt['excluded_derived_directories'] == ['__pycache__']
claim = json.loads((BASE / 'app-recovery.claim').read_bytes())
assert claim['work'] == receipt['source_work'] == '/root/hbr-app-recovery-ik0dm4a1'
assert claim['source_sha256'] == r['source_sha256']
assert r['started_epoch'] <= claim['epoch'] <= starts[0]['started_epoch']
tz = timezone(timedelta(hours=9))
summary = {'verified_at_kst': datetime.now(tz).isoformat(),
           'started_kst': datetime.fromtimestamp(r['started_epoch'], tz).isoformat(),
           'finished_kst': datetime.fromtimestamp(r['finished_epoch'], tz).isoformat(),
           'duration_seconds': round(r['finished_epoch'] - r['started_epoch'], 3),
           'result_sha256': sha((BASE / 'result.json').read_bytes()),
           'received_manifest_sha256': sha(manifest), 'received_files_verified': len(listed),
           'private_files_reported': len(private_rows), 'raw_private_all_received': False,
           'command_count': len(r['commands']), 'command_nonzero_count': 0,
           'start_count': len(starts), 'start_order': order, 'healthy_after': 10,
           'metadata_state_samples_verified': states, 'same_docker_invocation_samples': units,
           'ac04_shape_samples_verified': tables, 'profile_before_after_equal': True,
           'original_a3_result_claim_unchanged': True,
           'verdict': 'MANUAL_RECOVERY_CONFIRMED_FROM_RECEIVED_EXECUTION_RECORDS',
           'independent_review': 'PENDING', 'AUTOSTART': 'NOT_TESTED',
           'SYSLOG_INGESTION': 'NOT_TESTED', 'AC_CLOSE': 'NOT_EVALUATED'}
destination = ROOT / 'app-recovery-received-20261009'
if destination.exists():
    assert (destination / 'SHA256SUMS').read_bytes() == manifest
    for name in listed:
        assert (destination / name).read_bytes() == (BASE / name).read_bytes()
else:
    shutil.copytree(BASE, destination)
(ROOT / 'app-recovery-result-verification-20261009.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
