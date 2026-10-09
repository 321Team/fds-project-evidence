"""Read-only SSH receipt. No remote file creation or service/API mutations."""
import base64, datetime, hashlib, json, pathlib, shlex, subprocess, sys

ROOT=pathlib.Path(__file__).resolve().parent
PROJECT=ROOT.parent
EVIDENCE=PROJECT/'phase1-work-20261008/phase1-readonly-evidence'
OLD=EVIDENCE/'evidence/P1-APP-01/topology-spread-apply-20261007T0540Z/control01/p65-apply-20261007'
EXPECTED={}
for line in (OLD/'SHA256SUMS.all').read_text().splitlines():
    digest,name=line.split(None,1); name=name.strip().removeprefix('./')
    if name.endswith('-dryrun.json') or (name.endswith('-pods.json') and name!='pre/mon-post-final-pods.json'):
        EXPECTED[name]=digest
assert len(EXPECTED)==14

REMOTE=r'''
import base64,datetime,hashlib,json,os,pathlib,socket,stat,sys
config=CONFIG
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
if not ('2026-10-09T00:00:00+09:00'<=now.isoformat()<'2026-10-09T09:00:00+09:00'):
    raise SystemExit('STOP: outside collection window')
if socket.gethostname() not in ('k8s-control01','control01') or os.geteuid()!=0:
    raise SystemExit('STOP: unexpected host/euid')
root=pathlib.Path('/home/server02/p65-apply-20261007')
if root.resolve()!=root: raise SystemExit('STOP: source root symlink')
result={'schema':'fds.readonly-original-receipt.v1','host':socket.gethostname(),'euid':os.geteuid(),'source_root':str(root),'started_at_kst':now.isoformat(),'files':[],'remote_write':False}
for name,expected in config.items():
    p=root/name
    try:
        if p.resolve()!=p: raise ValueError('symlink')
        with p.open('rb') as f:
            before=os.fstat(f.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size>2000000: raise ValueError('type/size')
            raw=f.read(2000001)
            after=os.fstat(f.fileno())
        if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino): raise ValueError('changed during read')
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=expected: raise ValueError('original manifest mismatch')
        json.loads(raw)
        result['files'].append({'path':name,'sha256':digest,'expected_sha256':expected,'size':len(raw),'mode':oct(stat.S_IMODE(before.st_mode)),'uid':before.st_uid,'gid':before.st_gid,'mtime_ns':before.st_mtime_ns,'content_base64':base64.b64encode(raw).decode()})
    except Exception as e:
        result['files'].append({'path':name,'error':type(e).__name__+': '+str(e)})
        result['status']='STOP_INCOMPLETE'
        break
result['status']=result.get('status','RECEIVED_MANIFEST_MATCH')
result['finished_at_kst']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
print(json.dumps(result))
sys.exit(0 if result['status']=='RECEIVED_MANIFEST_MATCH' else 2)
'''.replace('CONFIG',repr(EXPECTED))

def main():
    stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    if not ('2026-10-09T00:00:00+09:00'<=stamp.isoformat()<'2026-10-09T09:00:00+09:00'):
        raise SystemExit('STOP: outside collection window')
    out=ROOT/'private'/('app-receipt-'+stamp.strftime('%Y%m%dT%H%M%S'))
    out.mkdir(parents=True,exist_ok=False)
    raw=REMOTE.encode(); (out/'collector.py').write_bytes(raw)
    inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.102','sudo -n python3 -']
    command=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
    p=subprocess.run(command,input=raw,capture_output=True,timeout=80)
    (out/'receipt.stdout.json').write_bytes(p.stdout); (out/'receipt.stderr').write_bytes(p.stderr)
    receipt={'started_at_kst':stamp.isoformat(),'finished_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'command':command,'collector_sha256':hashlib.sha256(raw).hexdigest(),'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'source_manifest_sha256':hashlib.sha256((OLD/'SHA256SUMS.all').read_bytes()).hexdigest()}
    (out/'invocation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('receipt_dir='+str(out)+' rc='+str(p.returncode))
    if p.returncode: print(p.stderr.decode(errors='replace')); raise SystemExit(2)
    data=json.loads(p.stdout); assert len(data['files'])==14
    for row in data['files']:
        raw=base64.b64decode(row.pop('content_base64'),validate=True)
        assert hashlib.sha256(raw).hexdigest()==EXPECTED[row['path']]==row['sha256']
        dest=out/'original'/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    (out/'metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('original_files=14 original_manifest_match=14')

if __name__=='__main__': main()
