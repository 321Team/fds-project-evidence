"""Disconnected-clone SSH planning inventory. No configuration/service mutations."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time

SHARE = Path('/mnt/hbr-ssh-check')
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
def require(ok, code):
    if not ok:
        raise ValueError(code)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    require(os.geteuid()==0 and socket.gethostname().split('.')[0]=='harbor01', 'HOST_OR_USER')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a','389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_ALREADY_PRESENT')
    local=Path(__file__).resolve().parent
    require(local.parent==Path('/root') and local.name.startswith('hbr-ssh-check-local-'), 'LOCAL_PATH')
    require(time.time()<int((local/'expires-epoch.txt').read_text()), 'EXPIRED')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE')
    os.umask(0o077)
    private=Path(tempfile.mkdtemp(prefix='hbr-ssh-precheck-',dir='/root'))
    result={'started_epoch':time.time(),'private':str(private),'collector_sha256':sha(Path(__file__).read_bytes()),
            'scope':'READ_ONLY_SSH_PLANNING','mutations':'NONE','commands':[]}
    files={}
    def query(name,argv,publish=True):
        outpath,errpath=private/(name+'.stdout'),private/(name+'.stderr')
        start=time.time()
        with outpath.open('xb') as out,errpath.open('xb') as err:
            try:
                rc=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=ENV,timeout=20).returncode
            except subprocess.TimeoutExpired: rc=124
            except OSError: rc=127
        require(outpath.stat().st_size<16*1024*1024,'OUTPUT_LIMIT')
        raw,errors=outpath.read_bytes(),errpath.read_bytes()
        result['commands'].append({'name':name,'argv':argv,'started_epoch':start,'finished_epoch':time.time(),
            'rc':rc,'stdout_sha256':sha(raw),'stdout_bytes':len(raw),'stderr_sha256':sha(errors),'stderr_bytes':len(errors)})
        if publish: files[outpath.name]=raw
        return rc,raw
    result['tools']={name:shutil.which(name,path=ENV['PATH']) for name in ('sshd','ssh-keygen','nmcli','firewall-cmd','nft','ip','visudo','systemctl')}
    files['os-release.txt']=Path('/etc/os-release').read_bytes()
    query('addresses',['ip','-j','address','show'])
    query('routes4',['ip','-j','-4','route','show','table','all'])
    query('routes6',['ip','-j','-6','route','show','table','all'])
    query('forwarding',['sysctl','net.ipv4.ip_forward','net.ipv6.conf.all.forwarding'])
    query('selinux',['getenforce'])
    query('units',['systemctl','show','sshd.service','NetworkManager.service','firewalld.service','docker.service',
                   '--no-pager','--property=Id,LoadState,ActiveState,SubState,FragmentPath'])
    query('listeners',['ss','-H','-ltn'])
    sshd=result['tools']['sshd'] or '/usr/sbin/sshd'
    query('sshd-syntax',[sshd,'-t'])
    rc,raw=query('sshd-effective',[sshd,'-T','-C','user=server08,host=harbor01,addr=192.168.253.1'],False)
    allowed={'port','listenaddress','addressfamily','permitrootlogin','pubkeyauthentication','passwordauthentication',
             'kbdinteractiveauthentication','authenticationmethods','allowusers','allowgroups','denyusers','denygroups',
             'authorizedkeysfile','usepam','allowtcpforwarding','allowagentforwarding','x11forwarding','disableforwarding'}
    files['sshd-selected.txt']=('\n'.join(line for line in raw.decode(errors='replace').splitlines()
         if line.split(' ',1)[0] in allowed)+'\n').encode()
    query('account-server08',['id','server08'])
    query('account-hbrctl',['getent','passwd','hbrctl'])
    for key in sorted(Path('/etc/ssh').glob('ssh_host_*_key.pub')):
        require(not key.is_symlink(),'HOST_KEY_SYMLINK')
        query('fingerprint-'+key.stem,['ssh-keygen','-lf',str(key)])
    rc,raw=query('nm-uuids',['nmcli','-g','UUID','connection','show'])
    if rc==0:
        ids=raw.decode().splitlines()
        require(len(ids)<=32 and all(re.fullmatch('[0-9a-fA-F-]{36}',v) for v in ids),'NM_INVENTORY')
        fields='connection.id,connection.uuid,connection.type,connection.interface-name,connection.autoconnect,ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns,ipv4.routes,ipv4.never-default,ipv6.method'
        for i,uid in enumerate(ids): query('nm-profile-'+str(i),['nmcli','-f',fields,'connection','show',uid])
    query('firewall-zones',['firewall-cmd','--list-all-zones'])
    query('firewall-policies',['firewall-cmd','--get-policies'])
    query('nft-rules',['nft','-j','list','ruleset'])
    rc,raw=query('docker-network-ids',['docker','--host=unix:///var/run/docker.sock','network','ls','-q','--no-trunc'])
    if rc==0:
        ids=raw.decode().splitlines()
        require(len(ids)<=32 and all(re.fullmatch('[0-9a-f]{64}',v) for v in ids),'DOCKER_NETWORK_IDS')
        for i,nid in enumerate(ids):
            query('docker-network-'+str(i),['docker','--host=unix:///var/run/docker.sock','network','inspect',
                 '--format','{"id":{{json .Id}},"name":{{json .Name}},"driver":{{json .Driver}},"internal":{{json .Internal}},"ipam":{{json .IPAM.Config}}}',nid])
    result['finished_epoch']=time.time()
    result['nonzero_queries']=[{'name':c['name'],'rc':c['rc']} for c in result['commands'] if c['rc']!=0]
    # Missing accounts/components may legitimately produce nonzero. Never label the inventory READY.
    files['RECEIPT.json']=(json.dumps(result,indent=2)+'\n').encode()
    dest=SHARE/'SSH_PRECHECK'
    dest.mkdir(exist_ok=False)
    for name,raw in files.items(): (dest/name).write_bytes(raw)
    manifest=''.join(sha(raw)+'  '+name+'\n' for name,raw in sorted(files.items())).encode()
    (dest/'SHA256SUMS').write_bytes(manifest)
    with (SHARE/'EXPORT_DONE').open('x') as out: out.write(sha(manifest)+'\n')
    print('SSH_PRECHECK_EXPORTED REVIEW_REQUIRED NONZERO='+str(len(result['nonzero_queries'])))
    print('No NIC, SSH account/key, firewall, service or Docker changes performed.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        code=str(exc)
        print('SSH_PRECHECK_STOP '+(code if re.fullmatch('[A-Z_]+',code) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
