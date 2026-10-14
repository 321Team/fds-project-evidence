from pathlib import Path
import json,hashlib,datetime as dt
r=Path(__file__).resolve().parent/'phase1-short-load-window-20261014-1415'
p=r/'db-after-user-transcript.txt';raw=p.read_bytes();s=raw.decode('utf-8')
assert "left(account_id,length('SIM_load_202610141415_'))='SIM_load_202610141415_'" in s
assert '\nfdsdb|postgres|2026-10-14 14:20:54.434941+09\n' in s
assert '\nDB_AFTER_RC=0\n' in s and '\nCOMMIT\n' in s
parts=next(x for x in s.splitlines() if x.startswith('8400|')).split('|')
assert len(parts)==7
types={x.split('|')[0]:int(x.split('|')[1]) for x in s.splitlines() if x.startswith(('deposit|','transfer|','withdrawal|'))}
data={'run':'202610141415','host':'db01','database':'fdsdb','user':'postgres','db_timestamp':'2026-10-14T14:20:54.434941+09:00','stored_rows':int(parts[0]),'distinct_accounts':int(parts[1]),'distinct_transactions':int(parts[2]),'first_received_at':parts[3],'last_received_at':parts[4],'skipped':int(parts[5]),'detected':int(parts[6]),'types':types,'rc':0,'source':'user-submitted console text','console_text_local_sha256':hashlib.sha256(raw).hexdigest(),'server_original_file_hash_verified':False,'received_at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()}
with (r/'DB_AFTER_ACCEPTED.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(data,ensure_ascii=False))
