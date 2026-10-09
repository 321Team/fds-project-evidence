import datetime,hashlib,json,pathlib,shlex,shutil,subprocess,tarfile
R=pathlib.Path(__file__).resolve().parent
meta=json.loads((R/'app-raw-export.stdout').read_text())
outdir=R.parents[1]/'phase1-work-20261009/private/app-raw-handoff-20261009'
outdir.mkdir(exist_ok=False)
archive=outdir/'app-raw-37890963668.tar.gz'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','server01_cicd-runner@10.250.10.20','cat -- '+shlex.quote(meta['archive'])]
with archive.open('xb') as f:
 r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(inner)],stdout=f,stderr=subprocess.PIPE,timeout=180)
(R/'app-raw-receive.stderr').write_bytes(r.stderr);assert r.returncode==0
with archive.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert h==meta['archive_sha256'] and archive.stat().st_size==meta['archive_bytes']
expected=json.loads((R/'raw-expected.json').read_text());seen=set();export_receipt=None
with tarfile.open(archive,'r:gz') as t:
 for m in t:
  assert m.isfile() and m.name not in seen
  if m.name=='EXPORT_RECEIPT.json':export_receipt=json.load(t.extractfile(m));seen.add(m.name);continue
  assert m.name in expected and m.size==expected[m.name]['size']
  with t.extractfile(m) as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
  assert actual==expected[m.name]['sha256'];seen.add(m.name)
assert seen==set(expected)|{'EXPORT_RECEIPT.json'}
assert export_receipt and len(export_receipt['files'])==69
share=json.loads((R/'share-transfer-receipt.json').read_text(encoding='utf8'))
dest=pathlib.Path(share['destination'])/archive.name
with archive.open('rb') as f,dest.open('xb') as g:shutil.copyfileobj(f,g,1024*1024)
with dest.open('rb') as f:shared_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert shared_hash==h
receipt={'at_kst':datetime.datetime.now().astimezone().isoformat(),'status':'SERVER_PC_SHARE_HASH_MATCH_69_PAYLOADS_VERIFIED','source_run':37890963668,'server_archive':meta['archive'],'local_archive':str(archive),'share_archive':str(dest),'archive_sha256':h,'archive_bytes':archive.stat().st_size,'payload_count':69,'payload_bytes':sum(x['size'] for x in expected.values()),'manifest_metadata_archive_sha256':meta['expected_metadata_archive_sha256'],'retention':'NOT_CONFIRMED_NO_DELETION_SCHEDULED','human_custodian_acceptance':'NOT_CONFIRMED','server_raw_and_image_store':'PRESERVED_NOT_DELETED','scope':'Original manifest-listed logs/source/OCI/Trivy DB/reports received and rehashed. Internal Podman store and unlisted files not copied. No new app execution/Push/Deploy.'}
raw=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
(R/'app-raw-transfer-receipt.json').write_bytes(raw)
for p in [outdir/'RECEIPT.json',dest.parent/'APP_RAW_RECEIPT.json']:
 with p.open('xb') as f:f.write(raw)
with pathlib.Path(str(dest)+'.sha256').open('xb') as f:f.write((h+'  '+dest.name+'\n').encode())
print(json.dumps({'status':receipt['status'],'archive_bytes':receipt['archive_bytes'],'payload_count':69,'share_folder':str(dest.parent)},ensure_ascii=False))
