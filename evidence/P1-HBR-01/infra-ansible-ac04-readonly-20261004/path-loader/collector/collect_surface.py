"""Targeted read-only observation. Never evaluates nft files or changes sysctls."""
import datetime, hashlib, json, os, pathlib, re, socket, subprocess, sys

PROXY_KEYS = {'-proto', '-host-ip', '-host-port', '-container-ip', '-container-port', '-use-listen-fd'}

def emit(v):
    print(json.dumps(v, ensure_ascii=False), flush=True)

def command(name, argv):
    v = {'name':name, 'argv':argv, 'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=45)
        v.update(rc=r.returncode, stdout=r.stdout.decode(errors='replace'), stderr=r.stderr.decode(errors='replace'))
    except (OSError, subprocess.TimeoutExpired) as exc:
        v.update(rc=124 if isinstance(exc, subprocess.TimeoutExpired) else 127, error=type(exc).__name__)
    emit(v)
    return v

def selected_proxy_args(args):
    out = {}; unknown = []
    i = 1
    while i < len(args):
        key = args[i]
        if key in PROXY_KEYS and i+1 < len(args):
            out[key] = args[i+1]; i += 2
        else:
            unknown.append(key if key in PROXY_KEYS else 'UNRECOGNIZED_REDACTED'); i += 1
    return {'selected_args':out, 'unknown_options':unknown}

def listener_pids(stdout):
    return sorted({int(x) for x in re.findall(r'pid=(\d+)', stdout)})

def process_record(pid, root=pathlib.Path('/proc')):
    p = root / str(pid)
    try:
        exe = os.readlink(p/'exe')
        v = {'name':'listener-process','pid':pid,'exe':exe,'comm':(p/'comm').read_text().strip()}
        # Only known docker-proxy networking argv is exposed. No arbitrary process argv/environment.
        if pathlib.Path(exe).name == 'docker-proxy':
            data = (p/'cmdline').read_bytes()
            if len(data) > 65536: raise ValueError('CMDLINE_TOO_LARGE')
            v.update(selected_proxy_args(data.decode(errors='replace').rstrip('\0').split('\0')))
        else:
            v['argv']='NOT_COLLECTED_NON_DOCKER_PROXY'
        return v
    except (OSError, ValueError) as exc:
        return {'name':'listener-process','pid':pid,'status':'UNAVAILABLE_REVIEW_REQUIRED','error':type(exc).__name__}

def nft_lines(text):
    selected=[]
    for i,line in enumerate(text.splitlines()):
        s=line.strip();commented=s.startswith('#');candidate=s.lstrip('#').strip() if commented else s
        if candidate.startswith(('include ', 'flush ', 'table ', 'define ')):
            selected.append({'line':i+1,'commented':commented,'text':line})
    return selected

def bounded_read(path, limit=1048576):
    p=pathlib.Path(path)
    if p.is_symlink(): raise ValueError('SYMLINK_REVIEW_REQUIRED')
    with p.open('rb') as f: data=f.read(limit+1)
    if len(data)>limit: raise ValueError('FILE_TOO_LARGE')
    return data

def main():
    if socket.gethostname().split('.')[0] != 'harbor01' or os.geteuid()!=0:
        emit({'status':'STOP_TARGET_OR_PRIVILEGE_MISMATCH'}); return 1
    identity=command('identity-addresses',['ip','-j','address','show'])
    try:
        addrs=json.loads(identity.get('stdout',''))
        valid=identity['rc']==0 and any(x.get('ifname')=='ens160' and any(a.get('local')=='10.1.93.54' for a in x.get('addr_info',[])) for x in addrs)
    except (ValueError,TypeError): valid=False
    if not valid:
        emit({'status':'STOP_TARGET_ADDRESS_MISMATCH'}); return 1
    records=[identity]
    owners=command('443-listener-owners',['ss','-H','-ltnp','( sport = :443 )']);records.append(owners)
    pids=listener_pids(owners.get('stdout',''))
    emit({'name':'listener-owner-coverage','pid_count':len(pids),'status':'CAPTURED_REVIEW_REQUIRED' if pids else 'NO_PID_REVIEW_REQUIRED'})
    for pid in pids: emit(process_record(pid))
    # Discover all currently running docker-proxy processes using comm only, no broad process argv capture.
    proxy_pids=[]
    for p in pathlib.Path('/proc').iterdir():
        if not p.name.isdecimal(): continue
        try:
            if (p/'comm').read_text().strip()=='docker-proxy': proxy_pids.append(int(p.name))
        except OSError: pass
    for pid in sorted(set(proxy_pids)-set(pids)): emit(process_record(pid))
    reads_failed=[]
    for iface in ['all','default','ens160']:
        for key in ['disable_ipv6','forwarding']:
            path='/proc/sys/net/ipv6/conf/'+iface+'/'+key
            try: emit({'name':'ipv6-policy','path':path,'value':bounded_read(path,128).decode().strip()})
            except (OSError,ValueError) as exc:
                reads_failed.append(path);emit({'name':'ipv6-policy','path':path,'status':'UNAVAILABLE','error':type(exc).__name__})
    for name,argv in [
        ('nftables-unit',['systemctl','show','nftables.service','--property=LoadState,UnitFileState,ActiveState,SubState,FragmentPath,DropInPaths,ExecStart,ExecReload,ExecStop,Requires,Wants,WantedBy,Triggers,TriggeredBy']),
        ('ipv6-routes',['ip','-j','-6','route','show','table','all']),
        ('ipv6-nat',['ip6tables','-t','nat','-S'])]:
        records.append(command(name,argv))
    for path in ['/etc/sysconfig/nftables.conf','/etc/nftables.conf','/etc/nftables/main.nft']:
        try:
            data=bounded_read(path)
            emit({'name':'nft-config','path':path,'sha256':hashlib.sha256(data).hexdigest(),'selected_directives':nft_lines(data.decode(errors='replace'))})
        except FileNotFoundError: emit({'name':'nft-config','path':path,'status':'ABSENT'})
        except (OSError,ValueError) as exc:
            reads_failed.append(path);emit({'name':'nft-config','path':path,'status':'UNAVAILABLE_REVIEW_REQUIRED','error':str(exc) if isinstance(exc,ValueError) else type(exc).__name__})
    path='/etc/docker/daemon.json'
    try:
        data=bounded_read(path);v=json.loads(data)
        if not isinstance(v,dict): raise ValueError('DOCKER_CONFIG_OBJECT_REQUIRED')
        keys=['ipv6','ip6tables','userland-proxy','bip','fixed-cidr-v6']
        emit({'name':'docker-daemon-selected','path':path,'sha256':hashlib.sha256(data).hexdigest(),'configured':{k:v[k] for k in keys if k in v},'unset_keys':[k for k in keys if k not in v], 'unset_meaning':'DEFAULT_NOT_INFERRED'})
    except FileNotFoundError: emit({'name':'docker-daemon-selected','path':path,'status':'ABSENT_DEFAULT_NOT_INFERRED'})
    except (OSError,ValueError) as exc:
        reads_failed.append(path);emit({'name':'docker-daemon-selected','path':path,'status':'UNAVAILABLE_REVIEW_REQUIRED','error':type(exc).__name__})
    failed=[r['name'] for r in records if r['rc']!=0]
    emit({'verdict':'COLLECTION_FAILED' if failed or reads_failed else 'PATH_LOADER_CAPTURED_REVIEW_REQUIRED',
          'failed_commands':failed,'unavailable_reads':reads_failed,'listener_reachability':'NOT_TESTED',
          'global_custom_loader_audit':'NOT_PERFORMED','loader_include_closure':'REVIEW_REQUIRED',
          'apply_approval':'NOT_GRANTED','runtime_apply':False})
    return 1 if failed or reads_failed else 0

if __name__=='__main__': sys.exit(main())
