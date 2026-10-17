"""One local standalone fixture; exact provenance, shared lock and bounded recovery."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import stat
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lifecycle',HERE/'lifecycle.py')
life=importlib.util.module_from_spec(spec);spec.loader.exec_module(life)
c=life.c
secure=life.secure

def preflight(root,args,commands):
    secure(HERE)
    raw=(HERE/'manifest.json').read_bytes()
    c.require(hashlib.sha256(raw).hexdigest()==args.manifest_sha256,'MANIFEST_HASH')
    manifest=json.loads(raw)
    for rel,row in manifest['files'].items():
        p=HERE/rel
        c.require(p.is_file() and not p.is_symlink() and p.stat().st_uid==c.HOST_UID and p.stat().st_gid==c.HOST_GID,'SUPPLY_OWNERSHIP')
        c.require(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'SUPPLY_HASH:'+rel)
        c.require(stat.S_IMODE(p.stat().st_mode)==row['mode'],'SUPPLY_MODE:'+rel)
    image=json.loads(commands.run(['image','inspect',c.IMAGE])['stdout'])[0]
    c.require(image['Id'].removeprefix('sha256:')==c.IMAGE.removeprefix('sha256:'),'BASE_IMAGE_CHANGED')
    c.require(not image.get('Config',{}).get('Volumes'),'IMAGE_IMPLICIT_VOLUME')
    c.require(not json.loads(commands.run(['ps','-a','--format','json'])['stdout']),'OTHER_CONTAINER_PRESENT')
    info=json.loads(commands.run(['info','--format','json'])['stdout'])
    c.require(info['host']['security']['rootless'] is True,'NOT_ROOTLESS')
    c.require(info['host']['security']['selinuxEnabled'] is True,'SELINUX_DISABLED')
    c.require(info['host']['cgroupVersion']=='v2','CGROUP_VERSION')
    c.require(info['store']['graphRoot']=='/home/ansible-verify/.local/share/containers/storage'
              and info['store']['runRoot']=='/run/user/1001/containers','STORE_IDENTITY')
    rootless_maps=c.rootless_id_maps(info['host']['idMappings'])
    c.require(os.statvfs(root).f_bavail*os.statvfs(root).f_frsize>=2*1024**3,'DISK_HEADROOM')
    control={'session':root.name,'manifest_sha256':args.manifest_sha256,'host':socket.gethostname(),
             'host_uid':os.getuid(),'host_gid':os.getgid(),'rootless_id_maps':rootless_maps,
             'boot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
             'not_before':args.not_before,'end_by':args.end_by,'podman_binary':c.PODMAN,
             'store':{k:info['store'][k] for k in ('graphRoot','runRoot')},
             'namespaces':{key:os.readlink('/proc/self/ns/'+key) for key in ('pid','net','ipc','mnt','uts','user','cgroup')}}
    return control

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--not-before',required=True)
    parser.add_argument('--end-by',required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args();os.umask(0o077)
    root=HERE.parent;name=root.name
    try:life.host_identity(root);c.require(HERE.name=='kit','WRONG_KIT')
    except (Exception,KeyboardInterrupt) as exc:
        print(json.dumps({'execution':'REJECTED','initial_error':life.error(exc),'mutation_requests':0}));return 1
    evidence=life.Evidence(root,'host');commands=life.Commands(evidence)
    execution='FAILED';initial=None;cleanup={'status':'NOT_CREATED'};cid=None;control=None
    with life.Signals() as signals:
        try:
            with life.SessionLock(root,create=True):
                try:
                    life.assert_no_active(root)
                    control=preflight(root,args,commands)
                    start=life.dt.datetime.fromisoformat(args.not_before);end=life.dt.datetime.fromisoformat(args.end_by)
                    c.require(start.utcoffset() is not None and end.utcoffset() is not None and start<end,'WINDOW_FORMAT')
                    argv=c.create_argv(str(HERE),str(root),name,args.manifest_sha256)
                    if not args.execute:
                        evidence.save('PLAN.json',{'status':'PLAN_ONLY','argv':argv,'control':control})
                        print(json.dumps({'status':'PLAN_ONLY','evidence_errors':evidence.errors}));return int(bool(evidence.errors))
                    c.require(start<=life.now() and (end-life.now()).total_seconds()>=c.BUDGET+600,'OUTSIDE_SUFFICIENT_WINDOW')
                    commands.end=end
                    for folder in ('control','results'):(root/folder).mkdir(mode=0o700)
                    control['bind_witnesses']={}
                    for dest,path in (('/supply',HERE),('/control',root/'control'),('/results',root/'results')):
                        s=path.lstat()
                        c.require(stat.S_ISDIR(s.st_mode) and not path.is_symlink() and s.st_uid==c.HOST_UID and s.st_gid==c.HOST_GID and stat.S_IMODE(s.st_mode)==0o700,'BIND_SOURCE_IDENTITY')
                        control['bind_witnesses'][dest]={'source':str(path),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode)}
                    evidence.fixed('control/host.json',control)
                    evidence.fixed('CREATE_REQUEST.json',{'argv':argv,'time':life.now().isoformat(),'control':control})
                    c.require(not evidence.errors,'PREFLIGHT_EVIDENCE_INCOMPLETE')
                    create_error=None
                    try:create=commands.run(argv[3:],60,mutation=True)
                    except life.CommandFailure as exc:create=exc.row;create_error=exc
                    resolved=c.resolve_cid(root,name,args.manifest_sha256,create.get('stdout'))
                    evidence.save('CID_SOURCES.json',resolved);cid=resolved['cid']
                    cleanup={'status':'CREATE_IDENTITY_UNCONFIRMED_HANDOFF','sources':resolved}
                    if create_error:raise create_error
                    c.require(cid is not None,'CID_SOURCE_UNCONFIRMED')
                    value=life.inspected(commands,cid,root,args.manifest_sha256)
                    c.assert_created_isolation(value,str(root))
                    c.persist_identity(root,value,cid,name,args.manifest_sha256)
                    evidence.fixed('CREATED.json',value)
                    c.require(not evidence.errors,'CREATE_EVIDENCE_INCOMPLETE')
                    life.binding(control,root)
                    c.require((end-life.now()).total_seconds()>=c.BUDGET+60+180,'INSUFFICIENT_START_WINDOW')
                    commands.run(['start',cid],30,mutation=True)
                    deadline=time.monotonic()+c.BUDGET+60
                    while True:
                        value=life.inspected(commands,cid,root,args.manifest_sha256)
                        if value['State']['Status'] in ('exited','stopped'):
                            evidence.fixed('TERMINAL.json',value);break
                        c.require(time.monotonic()<deadline,'SESSION_DEADLINE')
                        time.sleep(5)
                    result=root/'results/SESSION_RESULT.json'
                    c.require(value['State']['ExitCode']==0 and not value['State'].get('OOMKilled',False) and result.is_file(),'FIXTURE_FAILED')
                    data=json.loads(result.read_bytes())
                    c.require(data['status']=='PASS_LOCAL_ROLE_FIXTURES' and data['source_head']==c.HEAD
                              and data.get('session')==name and data.get('manifest_sha256')==args.manifest_sha256
                              and data.get('stages')==7,'RESULT_BINDING_OR_STATUS')
                    c.require(not evidence.errors,'EXECUTION_EVIDENCE_INCOMPLETE')
                    execution='PASS_LOCAL_ROLE_FIXTURES'
                except (Exception,KeyboardInterrupt) as exc:
                    initial=life.error(exc)
                    if isinstance(exc,OSError):evidence.errors.append({'operation':'mandatory_provenance_or_io',**initial})
                finally:
                    signals.recovering=True
                    if cid and control:cleanup=life.recover(commands,root,control,cid,signals)
                    elif commands.mutations.get('create'):cleanup={'status':'CREATE_IDENTITY_UNCONFIRMED_HANDOFF','sources':cleanup.get('sources')}
                return life.finish(evidence,commands,execution,cleanup,initial,signals)
        except (Exception,KeyboardInterrupt) as exc:
            if initial is None:initial=life.error(exc)
            else:cleanup['outer_error']=life.error(exc)
            signals.recovering=True
            return life.finish(evidence,commands,execution,cleanup,initial,signals)

if __name__=='__main__':raise SystemExit(main())
