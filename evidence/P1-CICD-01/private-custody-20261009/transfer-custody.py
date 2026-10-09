import datetime,hashlib,json,os,pathlib,shutil
R=pathlib.Path(__file__).resolve().parent
audit=json.loads((R/'custody-audit.json').read_text(encoding='utf8'))
root=pathlib.Path(r'\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\01차 프로젝트\02 프로젝트 결과물')
assert root.is_dir()
dest=root/('P1-GWONUK-originals-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'))
dest.mkdir(exist_ok=False)
names=['k8s-tool-backup-20261009T091654.tar.gz','app-supply-37859961937.zip','app-tbs-37890963668-metadata.tar.gz','ansible-ci76-11602757338.zip','ansible-ci76-host-evidence.tar.gz']
receipt={'started_at_kst':datetime.datetime.now().astimezone().isoformat(),'destination':str(dest),'permission_basis':'User confirmed SMB share access is restricted to approved people; inherited filesystem ACL has Everyone/Users FullControl. SMB permission not independently inspected.','retention':'NOT_CONFIRMED_NO_DELETION_SCHEDULED','human_custodian_acceptance':'NOT_CONFIRMED','source_preserved':True,'files':[],'scope':'Five existing local originals; APP metadata archive excludes server raw/OCI/DB/report.'}
for item,name in zip(audit['items'],names,strict=True):
    src=pathlib.Path(item['absolute_path']);out=dest/name
    before=src.stat()
    with src.open('rb') as fin,out.open('xb') as fout:
        shutil.copyfileobj(fin,fout,1024*1024);fout.flush();os.fsync(fout.fileno())
    after=src.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'SOURCE_CHANGED'
    with out.open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
    assert actual==item['actual_sha256'] and out.stat().st_size==item['actual_bytes'],'RECEIVED_BYTES_MISMATCH'
    receipt['files'].append({'name':name,'bytes':out.stat().st_size,'sha256':actual,'received_hash_matches':True})
    (R/'share-transfer-progress.json').write_bytes(json.dumps(receipt,ensure_ascii=False,indent=2).encode())
manifest=''.join(x['sha256']+'  '+x['name']+'\n' for x in receipt['files'])
with (dest/'SHA256SUMS.txt').open('xb') as f:f.write(manifest.encode())
receipt['completed_at_kst']=datetime.datetime.now().astimezone().isoformat();receipt['status']='COPIED_5_OF_5_DESTINATION_HASH_VERIFIED'
raw=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
with (dest/'RECEIPT.json').open('xb') as f:f.write(raw)
readme='''# Phase 1 원본 보관 사본

5개 원본을 재압축 없이 복사하고 수신 파일 크기/SHA256을 대조했습니다. SHA256SUMS.txt와 RECEIPT.json 참조.

- K8S archive: PC에 회수한 이전17파일·메타데이터. 서버 fresh backup/restore 성공 증적이 아닙니다.
- APP supply: Source affbc69의125파일 공급물 원 ZIP. 실행 및 승인 상태는 evidence183/189/190 참조.
- APP TBS archive: Run37890963668의 JSON metadata 중심 수신 archive입니다. 서버 raw/OCI/image store/DB/report 전체를 포함하지 않습니다.
- CI76 ZIP·host archive: Run37895578228 / Job113706062449, evidence192에 연결됩니다. 운영 DNS 실행/엔진 전환 성공은 아닙니다.
- PC/서버 원본은 유지했습니다. 복사/해시 확인과 담당자의 최종 인수는 다릅니다. 인수자·보존 종료 기준은 미확정이며 자동 삭제를 설정하지 않았습니다.
- 공유 권한에 의한 승인 인원 제한은 사용자 확인 근거이며 SMB ACL 독립 감사 완료로 표시하지 않습니다. 외부 재공유하지 않습니다.
'''
with (dest/'README.md').open('xb') as f:f.write(readme.encode())
assert (dest/'RECEIPT.json').read_bytes()==raw
(R/'share-transfer-receipt.json').write_bytes(raw)
print(json.dumps({'status':receipt['status'],'destination':str(dest),'files':len(receipt['files']),'retention':receipt['retention']},ensure_ascii=False))
