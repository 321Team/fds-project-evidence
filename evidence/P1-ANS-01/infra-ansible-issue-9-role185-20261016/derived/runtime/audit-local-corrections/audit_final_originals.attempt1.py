"""Audit already collected bytes only. No network, source import, or test rerun."""
from pathlib import Path, PurePosixPath
import collections
import configparser
import datetime as dt
import hashlib
import json
import re
import tarfile

H = Path(__file__).resolve().parent
if not str(H).startswith('\\\\?\\'):
    H = Path('\\\\?\\' + str(H))
R = H / 'originals-20261016T081814170331'
COLLECTION = 'EVIDENCE_COLLECTED-20261016T081814170331.json'
OBSERVATION = 'observe-20261016T081754586553-SUMMARY.json'

def read(p):
    return json.loads(p.read_bytes())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    with (H / name).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def when(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))

def checked_sums(p, root):
    rows = []
    for line in p.read_text(encoding='utf-8').splitlines():
        digest, rel = line.split('  ', 1)
        pp = PurePosixPath(rel)
        assert not pp.is_absolute() and '..' not in pp.parts and ':' not in rel
        assert sha(root.joinpath(*pp.parts)) == digest, ('SHA256SUMS', p.name, rel)
        rows.append(rel)
    assert len(rows) == len(set(rows))
    return rows

def main():
    b = read(H / 'SESSION_BINDING.json')
    c = read(H / COLLECTION)
    receipt = read(R / '__COLLECTION_READ_RECEIPT__.json')
    inventory = {x['path']: x for x in receipt['files']}
    dirs = {x['path']: x for x in receipt['directories']}
    assert receipt['classification'] == 'READ_DERIVATIVE_NOT_SERVER_ORIGINAL'
    assert receipt['source_unchanged_during_read'] and receipt['root'] == b['root']
    assert len(inventory) == len(receipt['files']) == c['server_original_files'] == 3446
    assert c['collector_derived_files'] == 1
    assert sha(H / c['archive']) == c['archive_sha256']
    local_files = {p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file()}
    assert local_files == set(inventory) | {'__COLLECTION_READ_RECEIPT__.json'}
    assert {x['path']: x for x in c['files'] if x['path'] in inventory} == inventory
    for rel, row in inventory.items():
        p = R / rel
        assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], rel
        assert row['uid'] == 1001 and row['gid'] == 1002, rel
    with tarfile.open(H / c['archive'], 'r:') as tf:
        members = tf.getmembers()
        assert len(members) == len(local_files) == len({x.name for x in members})
        for member in members:
            assert member.isfile() and member.name in local_files
            raw = tf.extractfile(member).read()
            assert raw == (R / member.name).read_bytes()
            if member.name in inventory:
                row = inventory[member.name]
                assert (member.mode, member.uid, member.gid) == (row['mode'], row['uid'], row['gid'])

    assert sha(R / 'kit/manifest.json') == b['manifest_sha256']
    manifest = read(R / 'kit/manifest.json')
    assert manifest['source_head'] == b['source_head'] == 'affaad6b1a31d680164d9e3d5ef5d2a9d3fce95a'
    assert manifest['source_tree'] == '2563bcea5ceee3543451e96ac76011ef05e486bf'
    assert len(manifest['files']) == 487
    for rel, row in manifest['files'].items():
        captured = inventory['kit/' + rel]
        assert captured['sha256'] == row['sha256'] and captured['mode'] == row['mode'], rel
    assert {x for x in inventory if x.startswith('kit/')} == {'kit/manifest.json'} | {'kit/' + x for x in manifest['files']}
    frozen = checked_sums(H / 'PRE_EXECUTION_SHA256SUMS', H)
    assert len(frozen) == 181

    operator_meta = read(H / 'OPERATOR_ORIGINALS_COLLECTED.json')
    O = H / operator_meta['originals_directory']
    assert operator_meta['session'] == b['session'] and operator_meta['boot'] == b['boot']
    assert operator_meta['source_unchanged_during_read'] and len(operator_meta['files']) == 12
    assert set(operator_meta['missing']) == {'recovery.stdout', 'recovery.stderr', 'recovery.rc'}
    for row in operator_meta['files']:
        assert sha(O / row['name']) == row['sha256'] and (O / row['name']).stat().st_size == row['bytes']
    for phase in ('stage', 'plan', 'plan-binding', 'execute'):
        assert (O / (phase + '.rc')).read_bytes() == b'0\n'
        assert (O / (phase + '.stderr')).read_bytes() == b''

    control = read(R / 'control/host.json')
    identity = read(R / 'OWNED_IDENTITY.json')
    terminal = read(R / 'TERMINAL.json')
    created = read(R / 'CREATED.json')
    isolation = read(R / 'results/ISOLATION.json')
    session = read(R / 'results/SESSION_RESULT.json')
    request = read(R / 'CREATE_REQUEST.json')
    final_path, = list(R.glob('host-*-FINAL.json'))
    final = read(final_path)
    plan_path, = list(R.glob('host-*-PLAN.json'))
    plan = read(plan_path)
    obs = read(H / OBSERVATION)
    host_read = read(H / (obs['source_prefix'] + '-svc.stdout'))
    assert control['session'] == identity['session'] == session['session'] == b['session']
    assert control['manifest_sha256'] == identity['manifest_sha256'] == session['manifest_sha256'] == b['manifest_sha256']
    assert control['boot'] == receipt['boot'] == host_read['boot'] == b['boot']
    assert (control['not_before'], control['end_by']) == (b['start'], b['end'])
    assert (control['host'], control['host_uid'], control['host_gid']) == ('cicd-runner01', 1001, 1002)
    assert request['control'] == control and plan['status'] == 'PLAN_ONLY'
    assert all(control[k] == v for k, v in plan['control'].items())
    assert plan['argv'] == request['argv']
    assert sha(plan_path) == '2248892536cfc1858f3092ecd85f90ebdf0d76279a77d6af3005e8ff3f837eb7'
    assert terminal['Id'] == created['Id'] == identity['cid'] == 'b0d9da1071bd48759f1866549d37f682888b01f9c8dca6017823725cd65aec79'
    assert terminal['Name'] == b['session']
    assert terminal['Config']['Image'] == identity['image'] == b['image']
    assert terminal['Config']['Labels']['fds.fixture.manifest'] == b['manifest_sha256']
    assert terminal['Config']['Labels']['fds.fixture.session'] == b['session']
    assert terminal['State']['ExitCode'] == 0 and not terminal['State']['Running'] and not terminal['State']['OOMKilled']
    assert not terminal['State']['Error'] and not terminal['State']['Dead']
    started = when(terminal['State']['StartedAt']); finished = when(terminal['State']['FinishedAt'])
    assert when(b['start']) <= when(request['time']) <= started < when(b['new_start_cutoff'])
    assert started < finished < when(b['end'])
    assert terminal['HostConfig']['ReadonlyRootfs'] and terminal['HostConfig']['NetworkMode'] == 'none'
    assert not terminal['HostConfig']['Privileged'] and 'no-new-privileges' in terminal['HostConfig']['SecurityOpt']
    assert not terminal['EffectiveCaps'] and not terminal['BoundingCaps']
    assert 'HOME=/scratch/home' in terminal['Config']['Env']
    mounts = {x['Destination']: x for x in terminal['Mounts']}
    assert set(mounts) == {'/supply', '/control', '/results'}
    for destination, name in (('/supply', 'kit'), ('/control', 'control'), ('/results', 'results')):
        m = mounts[destination]
        assert m['Type'] == 'bind' and m['Source'] == b['root'] + '/' + name
        assert m['RW'] is (destination == '/results') and {'nodev', 'nosuid'} <= set(m['Options'])
        witness = control['bind_witnesses'][destination]
        assert all(dirs[name][k] == witness[k] for k in ('device', 'inode', 'mode', 'uid', 'gid'))
        container_witness = isolation['container_bind_witnesses'][destination]
        assert all(container_witness[k] == witness[k] for k in ('device', 'inode', 'mode'))
        assert container_witness['uid'] == container_witness['gid'] == 0
    assert isolation['passed'] and isolation['manifest_sha256'] == b['manifest_sha256']
    assert isolation['host_bind_witnesses'] == control['bind_witnesses']
    assert isolation['rootless_id_maps'] == control['rootless_id_maps']
    assert isolation['source_head'] == session['source_head'] == b['source_head']
    assert all(isolation['namespaces'][k] != v for k, v in control['namespaces'].items())
    assert isolation['limits'] == {'cpu.max': '200000 100000', 'memory.max': '4294967296', 'memory.swap.max': '0', 'pids.max': '512'}
    assert ':container_t:' in isolation['selinux']
    assert final == read(O / 'execute.stdout')
    assert final['execution'] == session['status'] == 'PASS_LOCAL_ROLE_FIXTURES'
    assert final['initial_error'] is None and final['evidence'] == 'COMPLETE' and final['evidence_errors'] == [] and final['signals'] == []
    assert not final['production_runtime'] and not final['phase1_acceptance']
    assert final['cleanup']['status'] == 'OWN_CONTAINER_REMOVED' and final['cleanup']['cid'] == identity['cid']
    assert final['cleanup']['absence_query_rc'] == 1 and final['cleanup']['error'] is None
    assert obs['exists_rc'] == host_read['exists']['rc'] == 1
    assert host_read['exists']['argv'][-1] == identity['cid'] and host_read['exists']['stderr'] == ''
    info = json.loads(host_read['info']['stdout'])
    assert host_read['info']['rc'] == 0 and info['host']['security']['rootless']
    assert {k: info['store'][k] for k in control['store']} == control['store']
    assert obs['controllers'] == obs['proc_read_errors'] == obs['observation_errors'] == []
    assert host_read['controllers'] == host_read['proc_read_errors'] == host_read['errors'] == []
    assert not (R / 'results/SESSION_FAILURE.json').exists()

    commands = []
    for p in sorted(R.glob('host-*.completion.json')):
        row = read(p); intent = read(p.with_name(p.name.replace('.completion.json', '.intent.json')))
        assert intent['status'] == 'INTENT_ONLY'
        for k in ('argv', 'started_at_utc', 'timeout_seconds'):
            assert intent[k] == row[k]
        assert when(row['started_at_utc']) <= when(row['ended_at_utc']) < when(b['end'])
        for channel in row['raw_channels'].values():
            assert channel['stored'] and channel['capture'] == 'COMPLETE_RETURNED'
            assert sha(R / channel['file']) == channel['sha256']
            assert (R / channel['file']).stat().st_size == channel['bytes']
        assert row['status'] == 'RETURNED'
        assert row['argv'][:3] == ['/usr/bin/podman', '--remote=false', '--cgroup-manager=systemd']
        if row['rc'] != 0:
            assert row['rc'] == 1 and row['argv'][3:5] == ['container', 'exists'] and row['argv'][-1] == identity['cid']
        commands.append(dict(record=p.name, **row))
    command_list, = list(R.glob('host-*-COMMANDS.json'))
    recorded_commands = read(command_list)
    execution_prefix = command_list.name.removesuffix('-COMMANDS.json')
    assert recorded_commands == [{k:v for k,v in row.items() if k != 'record'} for row in commands if row['record'].startswith(execution_prefix)]
    mutations = [x for x in commands if x['argv'][3] in ('create', 'start', 'stop', 'rm')]
    assert collections.Counter(x['argv'][3] for x in mutations) == {'create': 1, 'start': 1, 'rm': 1}
    assert all(x['rc'] == 0 for x in mutations)
    assert next(x['argv'] for x in mutations if x['argv'][3] == 'create') == request['argv']
    assert all(identity['cid'] in x['argv'] for x in mutations if x['argv'][3] != 'create')
    assert all('--force' not in x['argv'] and '-f' not in x['argv'] for x in mutations)

    suite_plan = read(R / 'kit/suite-plan.json')
    assert sha(R / 'kit/suite-plan.json') == '21995f962d1365341b8583b34c7e831d76dcd85d8c30d6aece11e657134adf0d'
    assert session['stages'] == len(suite_plan) == 7 and len(session['receipts']) == 18
    assert [x['label'] for x in session['receipts'][11:]] == [x['name'] for x in suite_plan]
    for row in session['receipts']:
        intent = read(R / 'results' / (row['label'] + '.intent.json'))
        assert row == read(R / 'results' / (row['label'] + '.receipt.json'))
        assert row['status'] == 'RETURNED' and row['rc'] == row['child_exit_observed'] == 0
        assert row['signals'] == [] and row['initial_error'] is None
        assert intent['status'] == 'INTENT_ONLY' and intent['rc'] is None
        assert all(intent[k] == row[k] for k in ('label', 'argv', 'started_at_utc'))
        assert started <= when(row['started_at_utc']) < finished
        assert row['elapsed_seconds'] > 0
        for channel in ('stdout', 'stderr'):
            assert ('results/' + row['label'] + '.' + channel) in inventory
    assert [x['label'] for x in session['receipts'][:11]] == [f'{p}-{v}' for v in ('2.16.19','2.21.3') for p in ('venv','pip','engine','engine-version')] + ['parser-version','parser-smoke','parser-stage-smoke']

    expected_counts = [45, 45, 48, 25, 1, 2, 19]
    suites = []; mon_receipts = []; checksum_files = []; fixture_configs = []
    mon_names = None
    for plan_row, count, outer in zip(suite_plan, expected_counts, session['receipts'][11:], strict=True):
        name = plan_row['name']; result_path = R / 'results' / plan_row['result']
        result = read(result_path); root = result_path.parent
        assert outer['argv'] == plan_row['argv']
        if plan_row['kind'] == 'mon':
            cases = result['cases']
            assert result['status'] == 'PASS' and result['source_commit'] == b['source_head'] and not result['source_dirty']
            assert result['expected_cases'] == len(cases) == count
            assert result['initial_error'] is None and result['evidence_errors'] == []
            names = [x['case'] for x in cases]
            assert len(set(names)) == count
            if mon_names is not None: assert names == mon_names
            mon_names = names
            partial = read(root / 'CASES.partial.json')
            assert partial['status'] == 'INCOMPLETE' and partial['cases'] == cases
            for case in cases:
                assert case['passed'] is True
                if 'expected_rc' not in case: continue
                command = read(root / (case['case'] + '.receipt.json'))
                intent = read(root / (case['case'] + '.intent.json'))
                log = root / (case['case'] + '.log')
                assert case['actual_rc'] == case['expected_rc'] == command['actual_rc'] == command['expected_rc']
                assert case['command_status'] == command['status'] == 'RETURNED'
                assert case['evidence_errors'] == command['evidence_errors'] == [] and command['primary_error'] is None
                assert command['output_state'] == 'COMPLETE' and log.stat().st_size == command['bytes'] and sha(log) == command['sha256']
                assert intent['status'] == 'INTENT_ONLY' and intent['actual_rc'] is None
                assert all(intent[k] == command[k] for k in ('case','argv','expected_rc','started_at_utc','timeout_seconds','stream'))
                assert started <= when(command['started_at_utc']) <= when(command['ended_at_utc']) <= finished
                mon_receipts.append({'suite':name, 'case':case['case'], 'rc':command['actual_rc'], 'receipt':(root/(case['case']+'.receipt.json')).relative_to(R).as_posix(), 'log_sha256':command['sha256']})
            assert len(list(root.glob('*.receipt.json'))) == sum('expected_rc' in x for x in cases) == 40
            assert (root / 'module-ready.txt').read_bytes() == b'fixture-module-ready\n'
            log = (root / 'localhost-cli-preflight.log').read_text()
            assert all(x in log for x in ('Exercise actual module transfer and copy', 'Read the transferred module result', 'Require exact module result'))
            assert re.search(r'localhost\s+: ok=3\s+changed=1\s+unreachable=0\s+failed=0', log)
            sums = checked_sums(root / 'SHA256SUMS', root)
            assert set(sums) == {p.name for p in root.iterdir() if p.is_file() and p.name != 'SHA256SUMS'}
            checksum_files.append({'suite':name,'files':len(sums)})
        elif plan_row['kind'] == 'generic':
            cases = result['results']
            assert result['passed'] == result['total'] == len(cases) == count
            assert sorted(x['name'] for x in cases) == plan_row['expected_names']
            assert all(x['passed'] is True and x.get('errors', []) == [] for x in cases)
            if name == 'ntp-flow':
                assert result['observed_sha256'] == sha(R / 'kit/chronyd-parser')
                for case in cases: assert read(root / case['name'] / 'RESULT.json') == case
            if name in ('ntp-flow', 'ntp-legacy'):
                for case in cases:
                    for channel in ('stdout.log','stderr.log'):
                        assert (root / case['name'] / channel).is_file()
        elif plan_row['kind'] == 'serial':
            assert result['passed'] is True and result['rc'] == 2 and len(result['hosts']) == 5
            assert result['name'] == 'five_clients_third_failure_restores_and_stops'
            hosts = result['hosts']
            assert hosts['k8s-worker01']['pair_matches_before'] and hosts['k8s-worker01']['restarts'] == 2
            for host in ('k8s-worker02','k8s-worker03'):
                assert hosts[host]['pair_matches_before'] and hosts[host]['observed_commands'] == hosts[host]['restarts'] == 0
            cases = [result]
        else:
            assert plan_row['kind'] == 'transport'
            assert result['passed'] is True and result['total'] == result['passed_cases'] == count == 2
            assert result['returncode'] == 0 and result['modules'] == ['fds_ntp_probe','fds_ntp_migration']
            cases = [{'module':m,'passed':True} for m in result['modules']]
        suites.append({'suite':name,'engine':plan_row['engine'],'result_file':result_path.relative_to(R).as_posix(),
                       'result_sha256':sha(result_path),'expected_cases':count,'passed_cases':count,'suite_rc':outer['rc'],
                       'scope':result.get('scope'),'cases':cases})

    for p in sorted((R / 'results').rglob('ansible.cfg')):
        config = configparser.ConfigParser(interpolation=None); config.read_string(p.read_text())
        row = {'file':p.relative_to(R).as_posix(),'directories':[]}
        for option, leaf in (('local_tmp','.ansible-local'),('remote_tmp','.ansible-remote')):
            value = config['defaults'][option]
            relative = p.parent.relative_to(R).as_posix() + '/' + leaf
            assert value == '/' + relative
            info = dirs[relative]
            assert (info['mode'],info['uid'],info['gid']) == (0o700,1001,1002)
            row['directories'].append({'option':option,'value':value,'linux_metadata':info})
        fixture_configs.append(row)
    assert len(fixture_configs) == 77
    assert sum(x['passed_cases'] for x in suites) == 185 and len(mon_receipts) == 80
    summary = {
        'classification':'POST_EXECUTION_ORIGINAL_EVIDENCE_AUDIT_NOT_TEST_RERUN',
        'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),
        'status':'PASS_LOCAL_ROLE_FIXTURES_185_OWN_CLEANUP_CONFIRMED',
        'session':b['session'],'source_head':b['source_head'],'source_tree':manifest['source_tree'],
        'candidate_archive_sha256':b['archive_sha256'],'manifest_sha256':b['manifest_sha256'],'cid':identity['cid'],
        'started_at_kst':terminal['State']['StartedAt'],'finished_at_kst':terminal['State']['FinishedAt'],
        'container_duration_seconds':(finished-started).total_seconds(),
        'source_original_files_checked':len(inventory),'manifest_entries_checked':len(manifest['files']),
        'operator_originals_checked':len(operator_meta['files']),'pre_execution_frozen_files_unchanged':len(frozen),
        'collection':COLLECTION,'archive':c['archive'],'archive_sha256':c['archive_sha256'],
        'host_command_receipts_checked':len(commands),'host_mutations':[{k:x[k] for k in ('record','argv','rc','started_at_utc','ended_at_utc')} for x in mutations],
        'setup_receipts_rc0':11,'suite_receipts_rc0':7,'role_cases_verified':185,'role_cases_failed':0,'role_cases_skipped':0,
        'mon_command_receipts_checked':len(mon_receipts),'mon_noncommand_assertion_cases':10,
        'fixture_configs_checked':len(fixture_configs),'linux_tmp_directories_mode0700_checked':2*len(fixture_configs),
        'mon_sha256sums':checksum_files,
        'suites':[{k:v for k,v in x.items() if k!='cases'} for x in suites],
        'cleanup':final['cleanup'],'post_observation':OBSERVATION,'post_observation_at_kst':obs['at_kst'],
        'controller_count':0,'exact_exists_rc':1,'host_execute_rc':0,
        'production_runtime':False,'phase1_acceptance':False,'ci_run_created':False,
        'new_remote_mutations_during_audit':0,
        'limits':['Isolated container localhost/files/parser fixtures; mocked service/chronyc/host observations remain mocked.',
                  'No production MON/NTP deployment, network/time daemon validation, GitHub CI, merge, or final AC acceptance.',
                  'NTP legacy/wrapper retain their existing summary/log evidence formats; no per-command receipt completeness is inferred for them.',
                  'MON CASES.partial.json remains INCOMPLETE by design; final RESULTS.json supplies the completed verdict.',
                  'Collection receipt and audits are derived records; 3446 captured files and 12 operator outputs are the original bytes.'],
        'retained_server_paths':[b['root'],b['input_directory']],
        'retained_paths_reason':'Original evidence and fixed supply retained; not an active container or pending recovery.'
    }
    save('HOST_COMMAND_AUDIT.json', commands)
    save('SUITE_CASE_AUDIT.json', suites)
    save('MON_COMMAND_AUDIT.json', mon_receipts)
    save('FIXTURE_TMP_DIRECTORY_AUDIT.json', fixture_configs)
    save('EVIDENCE_AUDIT.json', summary)
    print(json.dumps({k:summary[k] for k in ('status','role_cases_verified','source_original_files_checked','host_command_receipts_checked','fixture_configs_checked','exact_exists_rc')},ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
        save('AUDIT_ERROR-'+stamp+'.json',{'error_type':type(exc).__name__,'error':str(exc),'scope':'LOCAL_AUDIT_ONLY_ORIGINALS_UNCHANGED'})
        raise
