from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
meta=json.loads((R/'remote-originals/results/meta.json').read_bytes());run=meta['run']
assert re.fullmatch(r'2026101410[23][0-9]',run) and '202610141025'<=run<='202610141035'
sql="BEGIN READ ONLY; SET LOCAL statement_timeout='5s'; SELECT current_database(), current_user, current_timestamp; SELECT account_id, transaction_id, transaction_type, amount, fds_detected, fds_evaluation_skipped, coalesce((SELECT string_agg(r->>'rule_id', ',') FROM jsonb_array_elements(fds_rules) r WHERE (r->>'triggered')::bool), '-'), occurred_at FROM public.transactions WHERE left(account_id,length('SIM_rg_"+run+"_'))='SIM_rg_"+run+"_' ORDER BY received_at; COMMIT;"
text="# db01/server08. READ ONLY for actual APP RUN "+run+"; preserve all 8 pipe-separated columns.\nhostname\ndate --iso-8601=seconds\nsudo -u postgres psql -X -P pager=off -A -t -F '|' -v ON_ERROR_STOP=1 -d fdsdb -c \""+sql+"\"\nprintf 'DB_AFTER_RC=%s\\n' \"$?\"\ndate --iso-8601=seconds\n"
(R/'db-after-actual-run-console.txt').write_text(text,encoding='utf-8',newline='\n')
print(text)
