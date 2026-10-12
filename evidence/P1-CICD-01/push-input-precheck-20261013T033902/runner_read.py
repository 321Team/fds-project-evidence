# Executed with the four fixed source modules loaded by collect.py, in memory.
import datetime, hashlib, json, os, pwd, socket, stat, sys
from pathlib import Path
from prepare_db import require, verify_binary
from verify_runner import sha256
from oci_archive import inspect_archive, json_object
from scan_images import check_report

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def audit(event, args):
    if event == 'open':
        mode, flags = args[1], args[2]
        if isinstance(mode, str) and any(c in mode for c in 'wax+'):
            raise RuntimeError('WRITE_REFUSED')
        if isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise RuntimeError('WRITE_REFUSED')
    if event in ('subprocess.Popen', 'os.system', 'os.remove', 'os.rename', 'os.mkdir', 'os.chmod',
                 'os.chown', 'socket.connect', 'os.exec', 'os.posix_spawn'):
        raise RuntimeError('MUTATION_OR_NETWORK_REFUSED')
sys.addaudithook(audit)

require(socket.gethostname() == 'cicd-runner01' and os.geteuid() == 1000, 'WRONG_HOST_OR_UID')
home = Path(pwd.getpwuid(os.getuid()).pw_dir)
require(str(home) == '/home/server01_cicd-runner', 'WRONG_HOME')
root = home / 'FDS_CICD_AppWorkflow.57rithja'
for path in (root, home):
    s = path.lstat()
    require(stat.S_ISDIR(s.st_mode) and s.st_uid == 1000 and stat.S_IMODE(s.st_mode) == 0o700, 'PRIVATE_ROOT_REQUIRED')

out = {'started_at_utc': now(), 'hostname': socket.gethostname(), 'uid': os.geteuid(),
       'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
       'source_directory': str(root), 'files': {}, 'images': {}, 'read_only': True,
       'credential_access': False, 'fresh_scan': False, 'registry_access': False,
       'code_commit': '2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7',
       'code_sha256': MODULE_HASHES}

def read(name):
    path = root / name
    for part in (path, *path.parents): require(not part.is_symlink(), 'INPUT_SYMLINK')
    s0 = path.stat()
    require(stat.S_ISREG(s0.st_mode) and s0.st_nlink == 1 and s0.st_size <= 64*1024**2, 'INPUT_TYPE_SIZE')
    raw = path.read_bytes()
    s1 = path.stat()
    require((s0.st_ino, s0.st_size, s0.st_mtime_ns) == (s1.st_ino, s1.st_size, s1.st_mtime_ns), 'INPUT_CHANGED')
    out['files'][name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'uid': s0.st_uid,
                          'mode': oct(stat.S_IMODE(s0.st_mode))}
    return json_object(raw)

app = read('result.json')
build = read('build-scan/result.json')
scan = read('build-scan/scan/result.json')
require(app.get('APP_WORKFLOW') == app.get('APP_TEST_BUILD_SCAN') == 'PASS', 'APP_NOT_PASS')
require(app['build_result_sha256'] == out['files']['build-scan/result.json']['sha256'], 'BUILD_RECEIPT_HASH')
require(build['BUILD_SCAN'] == scan['IMAGE_SCAN'] == 'PASS', 'BUILD_SCAN_NOT_PASS')
require(build['scan_result_sha256'] == out['files']['build-scan/scan/result.json']['sha256'], 'SCAN_RECEIPT_HASH')
expected_context = {'workflow_sha': 'c9eff5fb2e50a690818a3e67347ab4a1bfc88f51',
                    'run_id': '37890963668', 'attempt': 1,
                    'input_sha256': '72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3'}
for receipt in (app, build, scan):
    require(all(receipt['context'][key] == value for key, value in expected_context.items()), 'BUILD_CONTEXT')
require(build['context'] == scan['context'], 'SCAN_CONTEXT')
require(build['source']['repository'] == '321Team/fds-msa' and
        build['source']['commit'] == scan['source_sha'] == 'affbc69beef9967f7977d09a6fec14f7fb6c0e94', 'SOURCE_BINDING')
require(set(build['images']) == set(scan['images']) == {'transaction-api', 'fds-engine'}, 'IMAGE_SET')
for name in ('transaction-api', 'fds-engine'):
    path = root / 'build-scan' / (name + '.oci.tar')
    require(not path.is_symlink() and path.stat().st_nlink == 1, 'ARCHIVE_LINK')
    identity = inspect_archive(path)
    for key in ('archive_sha256', 'manifest_digest', 'config_digest'):
        require(identity[key] == build['images'][name][key] == scan['images'][name][key], 'ARCHIVE_BINDING')
    item = scan['images'][name]
    require(item['scan'] == 'PASS' and type(item['exit_code']) is int and item['exit_code'] == 0, 'SCAN_STATUS')
    report_name = 'build-scan/scan/' + name + '/report.json'
    report = read(report_name)
    require(out['files'][report_name]['sha256'] == item['report_sha256'], 'REPORT_HASH')
    require(check_report(report, 0, identity) == item['counts'] == {'HIGH': 0, 'CRITICAL': 0}, 'REPORT_BINDING')
    out['images'][name] = {'identity': identity, 'scan': {key: item[key] for key in (
        'scan', 'exit_code', 'counts', 'manifest_digest', 'report_sha256')}}
verify_binary()
out.update(context=expected_context, source=build['source'], historical_provenance='PASS',
           installed_scanner_identity='PASS', finished_at_utc=now())
print(json.dumps(out))
