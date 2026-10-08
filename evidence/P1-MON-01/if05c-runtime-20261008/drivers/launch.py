import datetime,hashlib,json,os,pathlib,subprocess,sys
os.umask(0o077)
ROOT='/root/if05c-20261008-oo0o4gd4'
HASHES={'runtime.py': '554baa1776c061972555367dfa5a5a8461156de651b3646f974738f0454f69bc', 'guard.py': '5b88b92ad1592f2a513bb51b1714dbff77e15248cdef87bdbfa3e14f071a8589', 'input.json': 'e02ddd6be671ad47ffbcfe65264fc2b7a45c47b670f9fd148bc53fcfc76c8b1c'}
p=pathlib.Path(ROOT)
assert os.geteuid()==0
assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in HASHES.items())
with (p/'launch-once').open('x') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat())
(p/'preflight-status.json').write_bytes((p/'status.json').read_bytes())
(p/'status.json').unlink()
with (p/'runtime.stdout').open('xb') as out,(p/'runtime.stderr').open('xb') as err:
 proc=subprocess.Popen([sys.executable,'-B',str(p/'runtime.py'),'run',str(p)],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
 start=pathlib.Path('/proc/%d/stat'%proc.pid).read_text().rsplit(')',1)[1].split()[19]
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':proc.pid,'starttime':start,'path':str(p),'source_sha256':HASHES['runtime.py']}
(p/'launch.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
