"""Offline verification of preserved receipts. Does not execute any collected script."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads((root / 'analysis/receipt-verification.json').read_text())
checked = 0
stdout_checked = 0
for group, info in report['receipts'].items():
    folder = root / group
    assert sha(folder / 'SHA256SUMS') == info['manifest_sha256']
    lines = (folder / 'SHA256SUMS').read_text().splitlines()
    assert len(lines) == info['items']
    for line in lines:
        digest, name = line.split('  ', 1)
        path = folder / name
        assert path.resolve().is_relative_to(folder.resolve()) and sha(path) == digest
        checked += 1
    receipt = json.loads((folder / ('RECEIPT.json' if group == 'inventory' else 'SUMMARY.json')).read_text())
    collector = {'inventory': 'export.py', 'target-syntax': 'check.py',
                 'syntax-supplement': 'supplement.py'}[group]
    assert sha(root / 'source' / group / collector) == receipt['collector_sha256']
    for command in receipt['commands']:
        path = folder / (command['name'] + '.stdout')
        if path.exists():
            assert sha(path) == command['stdout_sha256']
            assert path.stat().st_size == command['stdout_bytes']
            stdout_checked += 1
first = json.loads((root / 'inventory/RECEIPT.json').read_text())
assert first['nonzero_queries'] == [{'name': 'account-hbrctl', 'rc': 2}]
assert (root / 'inventory/account-hbrctl.stdout').read_bytes() == b''
syntax = json.loads((root / 'target-syntax/SUMMARY.json').read_text())
supplement = json.loads((root / 'syntax-supplement/SUMMARY.json').read_text())
assert syntax['issues'] == ['NM_SHADOW_OPTIONS_UNCONFIRMED']
assert not supplement['issues'] and not supplement['warnings'] and not supplement['nonzero']
assert syntax['renderer_sha256'] == sha(root / 'source/target-syntax/render-clone-ssh-plan.py')
assert supplement['nm_candidate_sha256'] == sha(root / 'source/syntax-supplement/90-hbr-no-auto-default.conf.candidate')
firewall = next(c for c in syntax['commands'] if c['name'] == 'firewalld-candidate-check')
assert firewall['stderr_sha256'] == supplement['original_firewalld_stderr_sha256']
for group, info in report['source_bindings'].items():
    folder = root / 'source' / group
    assert sha(folder / 'SHA256SUMS') == info['handoff_manifest_sha256']
    assert sha(folder / 'stage-local.sh') == info['stage_sha256']
    for line in (folder / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = folder / name
        assert path.resolve().is_relative_to(folder.resolve()) and sha(path) == digest
print(json.dumps({'receipt_manifest_items_verified': checked,
                  'exported_command_stdout_verified': stdout_checked,
                  'collector_and_handoff_binding': 'PASS',
                  'original_warning_and_supplement_binding': 'PASS',
                  'scope': 'OFFLINE_ONLY_NOT_RUNTIME_OR_ACCEPTANCE'}))
