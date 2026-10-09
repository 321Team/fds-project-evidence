
import base64,datetime,hashlib,json,os,pathlib,socket,stat,sys
config={'apply/fds-engine-dryrun.json': '8cbcd654092cc83ed5b70e796639b79e2927205df46ec45c19bb4d28f22a4cfb', 'apply/fds-engine-unspread-dryrun.json': 'd6db1732195e91cf85dff911c744438516e35e071e4b02fef30ebf009ca7e978', 'apply/transaction-api-dryrun.json': '5d8cded0a86fd32538b1370c73ca34d6b97c2cfd47292bbfdca747dd8391f88e', 'apply/transaction-api-unspread-dryrun.json': '52929729281ea7ce217e1c4135071cddce9672c4289bc0d9467f60beb7d49776', 'pre/mon-after-fds-engine-1-pods.json': 'bc37462083c21707f3b00bf83f3dce86b40d0999df3735535a3c5111b459ca6f', 'pre/mon-after-fds-engine-2-pods.json': '4a05f0524b4ab2f0252a6eb2688c86069ccdc789f0c6c12fd150fd8740066cde', 'pre/mon-after-fds-engine-3-pods.json': '4a05f0524b4ab2f0252a6eb2688c86069ccdc789f0c6c12fd150fd8740066cde', 'pre/mon-after-fds-engine-4-pods.json': '4a05f0524b4ab2f0252a6eb2688c86069ccdc789f0c6c12fd150fd8740066cde', 'pre/mon-after-fds-engine-5-pods.json': '4a05f0524b4ab2f0252a6eb2688c86069ccdc789f0c6c12fd150fd8740066cde', 'pre/mon-after-transaction-api-1-pods.json': '215cd93e0b4ff27479a14c0c7f333669a46b462ae1d403b29ef0fff05c6624ad', 'pre/mon-after-transaction-api-2-pods.json': '87ff6b508f4a861338ac730c9eb77b034d732acd3cb14cad38ab16c7d40c2e06', 'pre/mon-after-transaction-api-3-pods.json': '87ff6b508f4a861338ac730c9eb77b034d732acd3cb14cad38ab16c7d40c2e06', 'pre/mon-after-transaction-api-4-pods.json': '87ff6b508f4a861338ac730c9eb77b034d732acd3cb14cad38ab16c7d40c2e06', 'pre/mon-pre-pods.json': '844eb17a3ac20951638c10b3f432b145dea5417ab1572d41b4a858fd23ee8945'}
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
