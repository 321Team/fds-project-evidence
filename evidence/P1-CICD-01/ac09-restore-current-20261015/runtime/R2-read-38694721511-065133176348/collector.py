"""Read sanitized receipt files for one actual Run; never connect to a socket."""
import base64,datetime,hashlib,json,os,pathlib,pwd,re,socket,stat,sys
HOME=pathlib.Path('/home/server01_cicd-runner')
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000 and pwd.getpwuid(1000).pw_name=='server01_cicd-runner'
assert len(sys.argv)==3 and re.fullmatch('[1-9][0-9]{0,19}',sys.argv[1]) and sys.argv[2] in ('false','true')
RUN=int(sys.argv[1]);MODE=sys.argv[2]
PLAN='3b928b2c74600d81066f4577a0b3095df027351434137249a67ef5e328720183'
RECORD='2c30b446277704f42bb6a0698d2457b4d712091b1f1dc8603a103184f795e80f'
SOURCE='fddc76e1c261cd938f06211b7ed035fdcb32e606'
EXPECTED={'execution':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':SOURCE,'run_id':RUN,'attempt':1},'record_sha256':RECORD,'plan_sha256':PLAN,'sa_uid':'8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'}
def safe(path,regular=False):
    for p in (path,*path.parents):
        s=p.lstat();assert (stat.S_ISREG(s.st_mode) if regular and p==path else stat.S_ISDIR(s.st_mode)) and s.st_uid in (0,1000) and not s.st_mode&0o022
    if regular:assert s is not None
def no_sensitive(value):
    if isinstance(value,dict):
        for k,v in value.items():
            assert k.lower() not in ('token','password','authorization','private_key','client-key-data','client-certificate-data','bearer')
            no_sensitive(v)
    elif isinstance(value,list):
        for v in value:no_sensitive(v)
    elif isinstance(value,str):
        assert '-----BEGIN' not in value and not re.search(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',value)
def read(path):
    safe(path,True);before=path.lstat();assert before.st_uid==1000 and before.st_nlink==1 and stat.S_IMODE(before.st_mode)==0o600 and 0<before.st_size<=1048576
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        opened=os.fstat(f.fileno());assert (opened.st_dev,opened.st_ino)==(before.st_dev,before.st_ino);raw=f.read(1048577);after=os.fstat(f.fileno())
    sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert sig(before)==sig(after)==sig(path.lstat())
    obj=json.loads(raw);no_sensitive(obj)
    return {'sha256':hashlib.sha256(raw).hexdigest(),'raw_b64':base64.b64encode(raw).decode(),'data':obj,'bytes':len(raw)}
safe(HOME);assert stat.S_IMODE(HOME.lstat().st_mode)==0o700
out={'host':socket.gethostname(),'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_run':RUN,'mode':MODE,'mutation':False,'socket_connected':False,'matches':[],'skipped_unstable':0}
dirs=sorted(HOME.glob('FDS_CICD_Deploy.*'));assert len(dirs)<=200
for d in dirs:
    try:
        safe(d);assert d.lstat().st_uid==1000 and stat.S_IMODE(d.lstat().st_mode)==0o700
        dispatch=read(d/'dispatch.json')
        if dispatch['data'].get('binding')!=EXPECTED or dispatch['data'].get('mode')!=MODE:continue
        item={'directory':str(d),'files':{'dispatch.json':dispatch}}
        if (d/'result.json').exists():item['files']['result.json']=read(d/'result.json')
        out['matches'].append(item)
    except (OSError,ValueError,AssertionError):out['skipped_unstable']+=1
assert len(out['matches'])<=1
path=HOME/'FDS_DeploySockets'/('r'+str(RUN)+'.sock')
out['socket']={'path':str(path),'exists':os.path.lexists(path)}
if os.path.lexists(path):
    safe(path.parent);s=path.lstat();out['socket'].update(is_socket=stat.S_ISSOCK(s.st_mode),uid=s.st_uid,mode=oct(stat.S_IMODE(s.st_mode)))
if MODE=='true' and out['matches'] and 'result.json' in out['matches'][0]['files']:
    root=HOME/'FDS_CICD_DeployClaims';out['claim_files']={}
    claim=root/(PLAN+'.claim.json')
    if claim.exists():out['claim_files'][claim.name]=read(claim)
    journal=root/(PLAN+'.checkpoints')
    if journal.exists():
        safe(journal);files=sorted(journal.glob('*.json'));assert len(files)<=500
        for f in files:
            assert re.fullmatch(r'[0-9]{4}\.json',f.name);out['claim_files'][journal.name+'/'+f.name]=read(f)
print(json.dumps(out,sort_keys=True))
