
import datetime as dt,hashlib,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
repo='quay.io/sclorg/postgresql-16-c9s'
index='sha256:d33717fd33c1a4b11afef94568d0c20812a19d62fb8c633fadee1e491e2edd4a'
platform='sha256:862cf9364c60a1c47f1721b4700302a959969a09091a8434b3c64949730ed1f1'
argv=['/usr/bin/skopeo','inspect','--no-creds','--tls-verify=true','--raw','docker://'+repo+'@'+platform]
p=subprocess.run(argv,capture_output=True,timeout=18);assert p.returncode==0
assert 'sha256:'+hashlib.sha256(p.stdout).hexdigest()==platform
manifest=json.loads(p.stdout);config_digest=manifest['config']['digest']
obj=json.loads(subprocess.check_output(['podman','image','inspect',repo+'@'+index],timeout=10))[0]
canonical='sha256:'+obj['Id'].removeprefix('sha256:')
assert canonical==config_digest and repo+'@'+index in obj['RepoDigests'] and repo+'@'+platform in obj['RepoDigests']
assert obj['Architecture']=='amd64' and obj['Os']=='linux' and obj['Config']['User']=='26'
home=pathlib.Path('/home/server01_cicd-runner')
plan=json.loads((home/'FDS_D03_Decisions_202610142110/plan.json').read_bytes())
apps=[]
for role in ('api','engine'):
    image=json.loads(subprocess.check_output(['podman','image','inspect',plan['images'][role]],timeout=10))[0]
    assert 'sha256:'+image['Id'].removeprefix('sha256:')==plan['images'][role]
    apps.append({'role':role,'config_id':'sha256:'+image['Id'].removeprefix('sha256:')})
result={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'SUPPLY_VERIFIED_BY_OCI_DESCRIPTOR','read_only_image_operations':True,'supply_commands_retried':0,'runtime_started':False,'original_supply_result_preserved':True,'correction':'The SHA256 of skopeo inspect --config output is not the OCI config descriptor digest; use the platform manifest config.digest. No runtime code, approved plan, or source digest changed.','index_digest':index,'platform_manifest':manifest,'platform_manifest_sha256':hashlib.sha256(p.stdout).hexdigest(),'config_descriptor_digest':config_digest,'actual_image_id':canonical,'repo_digests':obj['RepoDigests'],'apps':apps,'metadata_argv':argv,'metadata_rc':p.returncode,'metadata_stderr':p.stderr.decode()}
dest=home/'FDS_D03_SupplyValidation_202610142110';dest.mkdir(mode=0o700)
(dest/'platform-manifest.json').write_bytes(p.stdout)
(dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
(dest/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(dest.iterdir()) if f.is_file()))
print(json.dumps(result))
