import hashlib,io,json,pathlib,re,shlex,subprocess,tarfile
r=pathlib.Path(__file__).resolve().parent
name='sec19-edge-p4.jhwyv1bh'
jobs=[(name,['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01','tar -C /home/server01_ansible -czf - '+name])]
c0='sec19-edge-c0.Ky13JT1l'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','svc_ansible@10.1.93.102','sudo -n tar -C /root -czf - '+c0]
jobs.append((c0,['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(inner)]))
reports=[]
for folder,cmd in jobs:
    p=subprocess.run(cmd,capture_output=True,timeout=40)
    (r/(folder+'.tar.gz')).write_bytes(p.stdout)
    (r/(folder+'.stderr')).write_bytes(p.stderr)
    assert p.returncode==0,p.stderr
    with tarfile.open(fileobj=io.BytesIO(p.stdout)) as t:
        assert all(m.isfile() or m.isdir() for m in t)
        files={m.name:t.extractfile(m).read() for m in t if m.isfile()}
    assert all(not x.startswith('/') and '..' not in pathlib.PurePosixPath(x).parts for x in files)
    manifests=[]
    for f,b in files.items():
        if f.endswith('/SHA256SUMS'):
            prefix=f.rsplit('/',1)[0]+'/'
            for line in b.decode().splitlines():
                sha,rel=line.split('  ',1); assert hashlib.sha256(files[prefix+rel]).hexdigest()==sha,rel
            manifests.append({'name':f,'files_verified':len(b.decode().splitlines())})
    if folder==name:
        verdict=json.loads(files[folder+'/result.json'])
        assert verdict['runtime_rc']==0 and verdict['baseline_equal'] and verdict['captures_absent']
        state=json.loads(files[folder+'/state-before.stdout'])
        outcomes=[]
        for e in state['endpoints']:
            worker=e['node'];pod=e['addresses'][0]
            capture=next(b.decode() for f,b in files.items() if f.endswith('/tcpdump_'+worker+'.txt'))
            curl=next(b.decode() for f,b in files.items() if f.endswith('/curl_'+worker+'.txt'))
            hits=re.findall(r'IP 10\.1\.93\.50\.\d+ > '+re.escape(pod)+r'\.8000:',capture)
            assert hits and 'CURL_RC=0' in curl and 'HTTP_CODE=200' in curl
            outcomes.append({'worker':worker,'pod':pod,'source':'10.1.93.50','matching_packet_lines':len(hits),'curl_rc':0,'http':200})
        print(json.dumps(outcomes,indent=2))
        for suffix in ('runtime-started-utc.txt','runtime-finished-utc.txt','runtime.stderr'):
            print(suffix,files[folder+'/'+suffix].decode())
        (r/'worker-verification.json').write_text(json.dumps(outcomes,indent=2)+'\n')
    reports.append({'archive':folder+'.tar.gz','sha256':hashlib.sha256(p.stdout).hexdigest(),'bytes':len(p.stdout),'files':len(files),'manifests':manifests,'outer_hash_scope':'local SSH stream received bytes'})
(r/'receipt.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
