import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]);raw=p.read_bytes();d=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='f5c970f3c770997aa4acb0643eb0d29ecd3c4df267f7887cb04a1e6d23eff003'
assert d['collector_sha256']=='cd2205c11461f4c12258ecae62d64051c6f458e41cdd50e1bac1920131f8b750'
assert not d['errors'] and len(d['files'])==d['discovered_paths']==9
assert all(f['status']=='SCANNED' and f['stable_during_read'] and f['stream_complete'] and f['unparsed_chunks']==0 and f['read_bytes']==f['size_before']==f['size_after'] for f in d['files'])
out={'schema':'fds.edge-w4-analysis.v1','input_sha256':hashlib.sha256(raw).hexdigest(),
     'collection_started_kst':d['started_at_kst'],'collection_finished_kst':d['finished_at_kst'],
     'files_scanned':len(d['files']),'parsed_records':sum(f['parsed_records'] for f in d['files']),
     'read_bytes':sum(f['read_bytes'] for f in d['files']),'decoded_bytes':sum(f['decoded_bytes'] for f in d['files']),
     'records_in_w4':sum(c['count'] for f in d['files'] for c in f['w4_counts']),
     'unparsed_chunks':sum(f['unparsed_chunks'] for f in d['files']),
     'file_intervals':[{'path':f['path'],'records':f['parsed_records'],'first_kst':f['first_record_kst'],'last_kst':f['last_record_kst']} for f in d['files']],
     'http_5xx_overall_verdict':'NOT_MEASURED',
     'limitations':['No matching request in collected access files is not zero HTTP 5xx proof.',
                    'Effective/historical log_format, logging exclusions, actual route coverage and other log destinations NOT_VERIFIED.',
                    'Original access-log payloads remain on Edge; received bytes are host-generated projection, not the raw access logs.']}
print(json.dumps(out,ensure_ascii=False,indent=2))
