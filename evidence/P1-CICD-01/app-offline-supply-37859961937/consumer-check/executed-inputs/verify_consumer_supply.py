"""One-shot Linux byte compatibility check in a private temporary workspace."""
import copy,datetime,hashlib,json,os,pathlib,pwd,re,socket,stat,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parent
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    assert socket.gethostname()=='ansible01' and pwd.getpwuid(os.geteuid()).pw_name=='server01_ansible','STOP host/account'
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00','STOP window'
    assert ROOT.parent==pathlib.Path('/home/server01_ansible') and re.fullmatch('app-supply-check[.][A-Za-z0-9]+',ROOT.name),'STOP path'
    assert ROOT.resolve()==ROOT and stat.S_IMODE(ROOT.stat().st_mode)==0o700,'STOP private directory'
gate();started=now();sys.dont_write_bytecode=True;os.umask(0o077)
manifest=json.loads((ROOT/'INPUT_HASHES.json').read_bytes())
for name,digest in manifest.items():
    p=ROOT/name;assert p.is_file() and not p.is_symlink() and sha(p)==digest,name
sys.path.insert(0,str(ROOT/'consumer/tools/delivery'))
import offline_supply_v3 as supply
ZIP=ROOT/'supply.zip'
assert sha(ZIP)=='2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd' and ZIP.stat().st_size==109786915
source=ROOT/'supplied';source.mkdir(mode=0o700)
with zipfile.ZipFile(ZIP) as z:
    infos=z.infolist();names=[i.filename for i in infos]
    assert len(names)==126 and len(set(names))==126 and sum(i.file_size for i in infos)<512*1024**2
    checks={}
    for line in z.read('SHA256SUMS').decode().splitlines():
        h,n=line.split('  ',1);assert re.fullmatch('[0-9a-f]{64}',h) and n not in checks;checks[n]=h
    assert set(checks)==set(names)-{'SHA256SUMS'}
    for i in infos:
        p=pathlib.PurePosixPath(i.filename)
        assert not p.is_absolute() and all(x not in ('','..','.') for x in p.parts) and '\\' not in i.filename and ':' not in i.filename
        assert not i.is_dir() and not stat.S_ISLNK((i.external_attr>>16)&0xffff)
        raw=z.read(i)
        if i.filename!='SHA256SUMS':assert hashlib.sha256(raw).hexdigest()==checks[i.filename]
        out=source/i.filename;out.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with out.open('xb') as f:f.write(raw)
m=json.loads((source/'SUPPLY_MANIFEST.json').read_bytes())
assert sha(source/'SUPPLY_MANIFEST.json')=='6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4'
assert m['source']['commit']=='affbc69beef9967f7977d09a6fec14f7fb6c0e94' and m['supply_tool']['commit']=='8eac4c982076e3c219840a13686b15c46879981f'
assert m['policy']['delivery_authorization'] is False
record={'directory':str(source),'images':m['images'],'profiles':m['profiles'],
        'requirements':{k:v for k,v in m['requirements'].items() if k.endswith('/requirements.txt') or k.endswith('/requirements-test.txt')},
        'source_inputs':{'ci/apko/'+k:v for k,v in m['apko_inputs'].items()}}
config={'offline_supply':record,'services':{name:{'context':name,'dockerfile':name+'/Dockerfile'} for name in supply.SERVICES}}
staged=ROOT/'staged'
gate();supply.validate_record(record);identities=supply.stage(record,staged)
gate();supply.verify_staged(staged,record);supply.validate_source(ROOT/'app-source',config,staged)
negative=[]
def rejects(label,func,prefix):
    try:func()
    except Exception as e:
        assert str(e).startswith(prefix),(label,type(e).__name__,str(e))
        negative.append({'case':label,'result':'REJECTED','code':str(e)})
    else:raise AssertionError('Expected rejection: '+label)
bad=copy.deepcopy(record);bad['images']['builder']['archive_sha256']='0'*64
rejects('wrong_builder_expected_hash',lambda:supply.verify_staged(staged,bad),'STAGED_IMAGE_CHANGED:builder')
bad=copy.deepcopy(record);bad['profiles']['transaction-api-test']['roots_sha256']='0'*64
rejects('wrong_test_profile_expected_hash',lambda:supply.verify_staged(staged,bad),'STAGED_PROFILE_CHANGED')
bad=copy.deepcopy(config);key='ci/apko/wolfi-python313-builder.apko.yaml';bad['offline_supply']['source_inputs'][key]='0'*64
rejects('wrong_source_apko_expected_hash',lambda:supply.validate_source(ROOT/'app-source',bad,staged),'SOURCE_APKO_INPUT_CHANGED:')
gate();supply.verify_staged(staged,record);supply.validate_source(ROOT/'app-source',config,staged)
result={'schema':'fds.consumer-supply-compatibility.v1','started_at_kst':started,'finished_at_kst':now(),
        'host':socket.gethostname(),'account':pwd.getpwuid(os.geteuid()).pw_name,'python':sys.version.split()[0],
        'consumer_commit':'04e49811e46ffcd3f35183c2cfb9493901f84dc5','source_commit':m['source']['commit'],'supply_tool_commit':m['supply_tool']['commit'],
        'archive_sha256':sha(ZIP),'input_hashes':manifest,'calls_passed':['validate_record','stage','verify_staged','validate_source'],
        'negative_cases':negative,'final_original_revalidation':'PASS','identities':identities,
        'source_approval':'PENDING','full_app_config_validation':'NOT_RUN','image_load':'NOT_RUN','app_execution':'NOT_RUN','runtime_apply':'NOT_RUN',
        'scope':'Actual committed consumer file validation on received bytes; private workspace only. No mock, approval fields, package install or image execution.'}
raw=(json.dumps(result,indent=2)+'\n').encode();(ROOT/'result.json').write_bytes(raw);sys.stdout.buffer.write(raw)
