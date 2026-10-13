"""Read existing OCI archive metadata only; no extraction, container or token use."""
import datetime,hashlib,json,os,pathlib,socket,stat,tarfile
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000
root=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.57rithja/build-scan')
expected={'transaction-api':('70da457069443c8b7af55d93d4e942ab4788bcfb9fe11506ee0482cd17bfaec3','ef0afe42feb0f9e50f54b5aaab99a34bbeb01f10bc9fb8a0580519101645dc39'),'fds-engine':('bb5951c6bb2cf113f0d7815fddc41c2b1e2c9cd69ccbd8794f13f2bc277d405f','de34afb7a557d6ccc844fb74613ebc971eb493260236acc35ef3051935122813')}
def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
out={'host':socket.gethostname(),'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mutation':False,'archive_extraction':False,'container_execution':False,'images':{}}
for service,(expected_archive,manifest) in expected.items():
    path=root/(service+'.oci.tar')
    for q in (path,*path.parents):assert not q.is_symlink()
    before=path.stat();assert stat.S_ISREG(before.st_mode) and before.st_uid==1000 and before.st_size<1024**3
    digest=sha_file(path);assert digest==expected_archive
    with tarfile.open(path,'r:') as outer:
        def blob(digest):
            p='blobs/sha256/'+digest.split(':')[-1];m=outer.getmember(p);assert m.isfile() and m.size<1024*1024
            raw=outer.extractfile(m).read();assert hashlib.sha256(raw).hexdigest()==digest.split(':')[-1];return json.loads(raw)
        m=blob(manifest);conf=blob(m['config']['digest']);c=conf['config']
        row={'path':str(path),'archive_sha256':digest,'manifest_digest':'sha256:'+manifest,'config_digest':m['config']['digest'],'config_user':c.get('User'),'entrypoint':c.get('Entrypoint'),'cmd':c.get('Cmd'),'working_dir':c.get('WorkingDir'),'selected_layer_entries':[]}
        for i,layer in enumerate(m['layers']):
            member=outer.getmember('blobs/sha256/'+layer['digest'].split(':')[-1]);assert member.isfile() and member.size<1024**3
            with outer.extractfile(member) as stream,tarfile.open(fileobj=stream,mode='r|*') as tar:
                for j,item in enumerate(tar):
                    assert j<200000
                    name=item.name.removeprefix('./').rstrip('/')
                    if name in ('app','app/run.py','app/app') or (name.startswith('app/') and '/.wh.' in name):
                        row['selected_layer_entries'].append({'layer_index':i,'layer_digest':layer['digest'],'path':name,'type':'directory' if item.isdir() else 'regular' if item.isfile() else 'other','mode':oct(item.mode),'uid':item.uid,'gid':item.gid,'size':item.size})
        out['images'][service]=row
    after=path.stat();assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(out,sort_keys=True))
