"""Fail-closed environment gate and fixed existing role suites. No host plays."""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
import tempfile
import traceback

spec=importlib.util.spec_from_file_location('contract','/supply/contract.py')
contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
require=contract.require
OUT=Path('/results');SUPPLY=Path('/supply');SCRATCH=Path('/scratch')
SOURCE=SUPPLY/'source'
RECEIPTS=[]
EVIDENCE_ERRORS=[]

def write(name,value):
    contract.atomic_record(OUT/name,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())

def command(label,argv,timeout,env=None):
    start=time.monotonic();at=dt.datetime.now(dt.timezone.utc).isoformat()
    row={'label':label,'argv':[str(x) for x in argv],'started_at_utc':at,'status':'INTENT_ONLY','rc':None,
         'waits':[],'signals':[],'child_exit_observed':None,'initial_error':None}
    problem=None
    def wait_child(process,seconds,phase):
        entry={'phase':phase,'timeout_seconds':seconds};row['waits'].append(entry)
        try:
            result=process.wait(timeout=seconds);entry['rc']=result;row['child_exit_observed']=result;return result
        except (Exception,KeyboardInterrupt) as exc:
            entry['error_type']=type(exc).__name__;raise
    def send_signal(process,number):
        entry={'signal':number};row['signals'].append(entry)
        try:os.killpg(process.pid,number);entry['status']='SENT'
        except ProcessLookupError:entry['status']='PROCESS_NOT_FOUND'
    try:
        write(label+'.intent.json',row)
        with (OUT/(label+'.stdout')).open('xb') as stdout,(OUT/(label+'.stderr')).open('xb') as stderr:
            try:
                p=subprocess.Popen([str(x) for x in argv],stdout=stdout,stderr=stderr,env=env,cwd=SOURCE,start_new_session=True)
                try:row['rc']=wait_child(p,timeout,'initial');row['status']='RETURNED'
                except subprocess.TimeoutExpired:
                    row['status']='TIMEOUT'
                    row['initial_error']={'type':'TimeoutExpired','timeout_seconds':timeout}
                    send_signal(p,signal.SIGTERM)
                    try:wait_child(p,5,'after_TERM')
                    except subprocess.TimeoutExpired:
                        send_signal(p,signal.SIGKILL)
                        wait_child(p,5,'after_KILL')
                    row['rc']=124
            finally:
                for stream in (stdout,stderr):
                    try:stream.flush();os.fsync(stream.fileno())
                    except OSError as exc:EVIDENCE_ERRORS.append({'label':label,'operation':'raw_fsync','error':repr(exc)})
    except (Exception,KeyboardInterrupt) as exc:
        problem=exc;row.update(status='COMMAND_OR_RECORD_UNCONFIRMED',error=repr(exc))
        if row['initial_error'] is None:row['initial_error']={'type':type(exc).__name__,'message':str(exc)}
    finally:
        row['elapsed_seconds']=time.monotonic()-start;RECEIPTS.append(row)
        try:write(label+'.receipt.json',row)
        except OSError as exc:EVIDENCE_ERRORS.append({'label':label,'operation':'receipt','error':repr(exc)})
    if problem:raise problem
    require(row['rc']==0,'COMMAND_FAILED:'+label+':'+str(row['rc']))
    require(not EVIDENCE_ERRORS,'COMMAND_EVIDENCE_INCOMPLETE')

def gate():
    control=json.loads(Path('/control/host.json').read_bytes())
    require(control['host_uid']==contract.HOST_UID and control['host_gid']==contract.HOST_GID,'CONTROL_HOST_IDENTITY')
    require(os.getuid()==os.getgid()==0,'NOT_ISOLATED_UID0')
    require(sys.version_info[:2]==(3,12),'PYTHON_VERSION')
    require(not any(OUT.iterdir()),'RESULTS_NOT_FRESH')
    require(all(p.stat().st_uid==p.stat().st_gid==0 for p in (SUPPLY,OUT,SCRATCH)),'PATH_OWNERSHIP')
    bind_observed={}
    for dest in ('/supply','/control','/results'):
        s=Path(dest).stat()
        bind_observed[dest]={'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode)}
    contract.assert_bind_witnesses(control['bind_witnesses'],bind_observed,'/home/ansible-verify/'+control['session'])
    for path in (OUT,SCRATCH):require(stat.S_IMODE(path.stat().st_mode)==0o700,'PATH_MODE')
    for path in ('/','/supply','/control'):
        require(bool(os.statvfs(path).f_flag & os.ST_RDONLY),'NOT_READONLY:'+path)
    for path in ('/results','/scratch'):require(not os.statvfs(path).f_flag & os.ST_RDONLY,'NOT_WRITABLE:'+path)
    require(not os.statvfs('/dev/shm').f_flag & os.ST_RDONLY,'PRIVATE_SHM_READONLY')
    require(os.statvfs('/dev/shm').f_blocks*os.statvfs('/dev/shm').f_frsize==64*1024**2,'PRIVATE_SHM_SIZE')
    status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    for key in ('CapEff','CapPrm','CapBnd','CapAmb'):require(int(status[key].strip(),16)==0,'CAPABILITIES_PRESENT')
    require(status['NoNewPrivs'].strip()=='1' and status['Seccomp'].strip()=='2','SECURITY_FILTER')
    label=Path('/proc/self/attr/current').read_text().strip()
    require(':container_t:' in label,'SELINUX_CONTAINER_DOMAIN')
    namespaces={key:os.readlink('/proc/self/ns/'+key) for key in ('pid','net','ipc','mnt','uts','user','cgroup')}
    for key,value in namespaces.items():require(value!=control['namespaces'][key],'HOST_NAMESPACE:'+key)
    require(sorted(p.name for p in Path('/sys/class/net').iterdir())==['lo'],'EXTERNAL_NETWORK_INTERFACE')
    mapping=[list(map(int,line.split())) for line in Path('/proc/self/uid_map').read_text().splitlines()]
    gid_mapping=[list(map(int,line.split())) for line in Path('/proc/self/gid_map').read_text().splitlines()]
    uid_binding=contract.inner_to_host_map(mapping,control['rootless_id_maps']['uidmap'],contract.HOST_UID)
    gid_binding=contract.inner_to_host_map(gid_mapping,control['rootless_id_maps']['gidmap'],contract.HOST_GID)
    limits={name:Path('/sys/fs/cgroup/'+name).read_text().strip() for name in ('cpu.max','memory.max','memory.swap.max','pids.max')}
    quota,period=map(int,limits['cpu.max'].split());require(quota/period<=2,'CPU_LIMIT')
    require(int(limits['memory.max'])<=4*1024**3 and int(limits['memory.swap.max'])==0 and int(limits['pids.max'])<=512,'RESOURCE_LIMIT')
    manifest_raw=(SUPPLY/'manifest.json').read_bytes()
    require(hashlib.sha256(manifest_raw).hexdigest()==control['manifest_sha256'],'MANIFEST_IDENTITY')
    manifest=json.loads(manifest_raw)
    for rel,row in manifest['files'].items():
        p=SUPPLY/rel
        require(not p.is_symlink() and p.is_file(),'SUPPLY_TYPE:'+rel)
        require(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'SUPPLY_HASH:'+rel)
        require(stat.S_IMODE(p.stat().st_mode)==row['mode'],'SUPPLY_MODE:'+rel)
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip()==contract.HEAD,'SOURCE_HEAD')
    require(subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=SOURCE,text=True).strip()==contract.TREE,'SOURCE_TREE')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE),'SOURCE_DIRTY')
    write('ISOLATION.json',{'passed':True,'uid':0,'gid':0,'uid_map':mapping,'gid_map':gid_mapping,
                           'rootless_id_maps':control['rootless_id_maps'],'uid_binding':uid_binding,'gid_binding':gid_binding,
                           'host_bind_witnesses':control['bind_witnesses'],'container_bind_witnesses':bind_observed,'limits':limits,'selinux':label,
                           'namespaces':namespaces,'source_head':contract.HEAD,'manifest_sha256':control['manifest_sha256']})

def main():
    os.umask(0o077)
    try:
        gate()
        for name in ('home','tmp','engines'):(SCRATCH/name).mkdir(mode=0o700)
        for version in ('2.16.19','2.21.3'):
            venv=SCRATCH/'engines'/version
            command('venv-'+version,[sys.executable,'-I','-B','-m','venv',venv],120)
            python=venv/'bin/python'
            command('pip-'+version,[python,'-I','-B','-m','pip','install','--no-index','--no-cache-dir','--require-hashes',
                                   '--find-links=/supply/wheels','-r','/supply/requirements-pip.txt'],60)
            command('engine-'+version,[python,'-I','-B','-m','pip','install','--no-index','--no-cache-dir','--require-hashes',
                                      '--find-links=/supply/wheels','-r','/supply/requirements-'+version+'.txt'],120)
            command('engine-version-'+version,[venv/'bin/ansible-playbook','--version'],15)
            first=(OUT/('engine-version-'+version+'.stdout')).read_text().splitlines()[0]
            require(first=='ansible-playbook [core '+version+']','ENGINE_VERSION')
        command('parser-version',['/supply/chronyd-parser','-v'],15)
        require('version 4.8 ' in (OUT/'parser-version.stdout').read_text(),'PARSER_VERSION')
        # The real copied loader+parser must work inside this image before role tests.
        probe=OUT/'parser-smoke.conf';probe.write_text('server 192.0.2.123 iburst\n')
        command('parser-smoke',['/supply/chronyd-parser','-p','-f',probe],15)
        with tempfile.TemporaryDirectory(prefix='fds-ntp-stage-',dir=SCRATCH/'tmp') as directory:
            stage_probe=Path(directory)/'chrony.conf'
            stage_probe.write_text('server 192.0.2.123 iburst\n')
            command('parser-stage-smoke',['/supply/chronyd-parser','-p','-f',stage_probe],15)
        stages=json.loads((SUPPLY/'suite-plan.json').read_bytes())
        for row in stages:
            env=dict(os.environ,PATH='/scratch/engines/'+row['engine']+'/bin:/usr/local/bin:/usr/bin:/bin')
            env.pop('FDS_ANSIBLE_ENGINE_DIR',None);env.pop('FDS_ANSIBLE_ENGINE_VERSION',None)
            command(row['name'],row['argv'],row['timeout_seconds'],env)
            result=json.loads((OUT/row['result']).read_bytes())
            contract.check_result(row['kind'],result)
            if row.get('expected_names'):
                require(sorted(x['name'] for x in result['results'])==row['expected_names'],'CHANGED_CASE_SET:'+row['name'])
        control=json.loads(Path('/control/host.json').read_bytes())
        require(not EVIDENCE_ERRORS,'EVIDENCE_INCOMPLETE')
        write('SESSION_RESULT.json',{'status':'PASS_LOCAL_ROLE_FIXTURES','source_head':contract.HEAD,'stages':len(stages),
                                     'session':control['session'],'manifest_sha256':control['manifest_sha256'],
                                     'receipts':RECEIPTS,'production_runtime':False,'phase1_acceptance':False})
        return 0
    except (Exception,KeyboardInterrupt):
        failure={'status':'STOP_REVIEW_REQUIRED','traceback':traceback.format_exc(),'receipts':RECEIPTS,'evidence_errors':EVIDENCE_ERRORS}
        try:write('SESSION_FAILURE.json',failure)
        except OSError as exc:EVIDENCE_ERRORS.append({'operation':'SESSION_FAILURE','error':repr(exc)})
        print(json.dumps(failure,ensure_ascii=False),file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
