import datetime,hashlib,json,os,pathlib,pwd,stat,subprocess,sys,tempfile
BASE='da4e273e7e26a9a0b51211e5146066960df072b5'
home=pathlib.Path.home()
assert os.uname().nodename=='ansible01' and pwd.getpwuid(os.getuid()).pw_name=='server01_ansible' and os.getuid()!=0
os.umask(0o077)
raw=sys.stdin.buffer.read(16*1024*1024+1)
assert len(raw)<16*1024*1024 and raw.startswith(b'# v2 git bundle')
root=pathlib.Path(tempfile.mkdtemp(prefix='issue9-native-engine-',dir=home))
(root/'source.bundle').write_bytes(raw)
subprocess.run(['git','clone','-q',str(root/'source.bundle'),str(root/'source')],check=True)
src=root/'source'
assert subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()==BASE
assert subprocess.check_output(['git','-C',str(src),'status','--porcelain'],text=True)==''
candidate=home/'ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin'
assert candidate.is_dir()
key=home/'.ssh/p1_ansible_ed25519'
assert key.is_file()
logs=root/'evidence';logs.mkdir(mode=0o700)
env={'PATH':'/usr/bin:/bin','HOME':str(home),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','ANSIBLE_CONFIG':str(src/'ansible.cfg'),'ANSIBLE_LOCAL_TEMP':str(root/'ansible-tmp'),'ANSIBLE_PRIVATE_KEY_FILE':str(key),'FDS_ANSIBLE_ENGINE_DIR':str(candidate),'FDS_ANSIBLE_ENGINE_VERSION':'2.21.3','GATE0_EVIDENCE_DIR':str(root/'gate0-syntax')}
records=[]
def run(name,argv,expected=0):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r=subprocess.run(argv,cwd=src,env=env,capture_output=True,timeout=90)
    (logs/(name+'.stdout')).write_bytes(r.stdout);(logs/(name+'.stderr')).write_bytes(r.stderr)
    records.append(dict(name=name,argv=argv,rc=r.returncode,expected_rc=expected,started_at=start,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    assert r.returncode==expected,(name,r.returncode)
    return r
try:
    baseline=run('system-version',['/usr/bin/ansible','--version'])
    for cli in ('ansible-playbook','ansible-inventory','ansible','ansible-config'):
        run(cli+'-selected-version',['/bin/bash','-c','set -eu; source scripts/lib/ansible-engine.sh; fds_engine_init; fds_engine_exec "$1" --version','engine-native',cli])
    run('gate0-selected-syntax',['/bin/bash','scripts/p1-k8s-01-gate0-run.sh','syntax'])
    run('mismatch-stop',['/bin/bash','-c','set -eu; source scripts/lib/ansible-engine.sh; FDS_ANSIBLE_ENGINE_VERSION=2.16.19; fds_engine_init'],64)
    after=run('system-version-after',['/usr/bin/ansible','--version'])
    assert baseline.stdout==after.stdout
    state='PASS_CONTROLLER_NATIVE_SYNTAX_ONLY'
except Exception as exc:
    state='STOP_CONTROLLER_NATIVE_CHECK'
    (logs/'failure.txt').write_text(str(exc)+'\n')
finally:
    report=dict(status=state,host=os.uname().nodename,user=pwd.getpwuid(os.getuid()).pw_name,uid=os.getuid(),source_sha=BASE,source_bundle_sha256=hashlib.sha256(raw).hexdigest(),candidate_bin=str(candidate),commands=records,managed_host_execution='NOT_RUN',key_restore='NOT_RUN',global_engine_transition='NOT_RUN',dns_mon_ntp_wrapper_runtime='NOT_RUN',evidence_root=str(logs))
    (logs/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    (logs/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(logs.iterdir()) if f.is_file()))
    print(json.dumps(report))
sys.exit(0 if state=='PASS_CONTROLLER_NATIVE_SYNTAX_ONLY' else 2)
