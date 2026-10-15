"""Prepare an exact, unexecuted read of the two AC09 accounts from received evidence."""
import datetime as dt, hashlib, json, re, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/'deliverables/p1-cicd-ac09-preparation-20261015'
analysis=json.loads((HERE/'APP_RUNTIME_COMPARISON.json').read_bytes())
r1=analysis['phases']['r1']['post']; r2=analysis['phases']['r2']['post']
planned=json.loads((SRC/'r2-return-current.payload.TEMPLATE.json').read_bytes())
account2=r2['payload']['account_id'] if r2 else planned['payload']['account_id']
txn2=r2['response']['transaction_id'] if r2 else None
account1=r1['payload']['account_id']; txn1=r1['response']['transaction_id']
for value in [account1,account2,txn1,txn2]:
    assert value is None or re.fullmatch(r'[A-Za-z0-9_-]+',value)

sql=f'''BEGIN READ ONLY;
SET LOCAL statement_timeout = '3s';
SET LOCAL lock_timeout = '1s';
SELECT json_build_object('kind','identity','database',current_database(),
 'user',current_user,'at',current_timestamp,'timezone',current_setting('TimeZone'),
 'transaction_read_only',current_setting('transaction_read_only'));
WITH expected(phase, account_id, transaction_id) AS (
 VALUES ('R1','{account1}','{txn1}'),
        ('R2','{account2}',{repr(txn2) if txn2 else 'NULL::text'})
)
SELECT json_build_object('kind','business_rows','phase',e.phase,
 'expected_account_id',e.account_id,'expected_transaction_id',e.transaction_id,
 'matched_rows',count(t.transaction_id),'rows',
 coalesce(json_agg(json_build_object(
   'transaction_id',t.transaction_id,'account_id',t.account_id,
   'amount',t.amount,'currency',t.currency,'transaction_type',t.transaction_type,
   'source_ip',t.source_ip,'occurred_at',t.occurred_at,'received_at',t.received_at,
   'fds_detected',t.fds_detected,'fds_rules',t.fds_rules,
   'fds_evaluation_skipped',t.fds_evaluation_skipped
 ) ORDER BY t.received_at) FILTER (WHERE t.transaction_id IS NOT NULL),'[]'::json))
FROM expected e LEFT JOIN public.transactions t
 ON t.account_id=e.account_id OR t.transaction_id=e.transaction_id
GROUP BY e.phase,e.account_id,e.transaction_id ORDER BY e.phase;
ROLLBACK;
'''
(HERE/'DB_POST_READONLY_PREPARED.sql').write_text(sql,encoding='utf-8',newline='\n')
script='''(
  test "$(hostname -s)" = db01 || exit 10
  test "$(id -un)" = server08 || exit 11
  umask 077
  mkdir -m 700 /home/server08/ac09-app-db-after-20261015-1535 || exit 12
  cd /home/server08/ac09-app-db-after-20261015-1535 || exit 13
  cat > DB_POST_READONLY.sql <<'AC09_DB_SQL'
'''+sql+'''AC09_DB_SQL
  test "$?" -eq 0 || exit 14
  printf '__SQL_HASH__  DB_POST_READONLY.sql\\n' | sha256sum -c - || exit 14
  sudo -v || exit 15
  hostname > host.txt || exit 16
  id -un >> host.txt || exit 16
  date -Is > start.txt || exit 16
  if sudo -n -u postgres timeout 45s psql -X -q -A -t -v ON_ERROR_STOP=1 -d fdsdb \\
      < DB_POST_READONLY.sql > db-after.jsonl 2> db-after.stderr; then
    ac09_db_rc=0
  else
    ac09_db_rc=$?
  fi
  printf '%s\\n' "$ac09_db_rc" > db-after.rc || exit 16
  date -Is > end.txt || exit 16
  sha256sum DB_POST_READONLY.sql host.txt start.txt db-after.jsonl db-after.stderr db-after.rc end.txt > SHA256SUMS.txt || exit 17
  printf 'AC09_DB_AFTER_RC=%s\\n' "$ac09_db_rc"
  cat host.txt start.txt db-after.jsonl db-after.stderr db-after.rc end.txt SHA256SUMS.txt
  exit "$ac09_db_rc"
)
'''
script=script.replace('__SQL_HASH__',hashlib.sha256(sql.encode()).hexdigest())
header='''# AC09 두 단계 DB 거래 대조 — 준비안, 실행하지 않음

중앙이 R2 실제 업무 결과와 기존 정상 db01 콘솔 경로를 결속한 뒤 사용할 **1회 READ ONLY 후보**다. APP는 DB 접속·실행·사용자 질문을 하지 않았다. 기존 catalog의13:54:33 rc0를 재조회하지 않는다.

대상은 기존 `server08@db01` → postgres/fdsdb. 정확 AC09 계정2개와 확보한 Transaction ID만 읽는다. schema11열은 실제 수신 catalog에 있다. 계정 OR 거래ID로 조회하므로 같은 계정의 중복 행 또는 잘못 저장된 계정도 숨기지 않는다. 업무행 쓰기·삭제·전체 데이터 조회·다른 시험은 없다.

'''
if r2 is None:
    header+='**현재 결속:** R1 actual ID/계정은 확정. R2는 기존 payload TEMPLATE의 예정 계정이며 actual ID/시각은 아직 미수신이다. R2 실제 POST 결과의 계정이 같음을 중앙이 확인한 뒤 사용해야 한다. R2가 미실행이면 0행을 현행 업무 실패로 판정하지 않는다. 실제 R2 원문이 오면 이 준비안의 입력을 실제값으로 갱신한다.\n\n'
else:
    header+='**현재 결속:** R1/R2 actual POST 원문에서 두 계정·Transaction ID를 확정했다. DB 읽기 자체의 실행 여부는 여전히 미실행이다.\n\n'
header+='''기존 보호 경로가 있으면 덮어쓰거나 재실행하지 않는다. 암호는 sudo 콘솔에만 입력한다. 모든 실패 출력은 원본으로 보존한다.

```bash
'''
footer='''```

정상 수집: db01/server08, fdsdb/postgres, READ ONLY on, rc0, stderr 원본·시각·SHA 보존. 각 phase의 matched_rows=1, 정확 account/transaction ID, amount10000/currencyKRW/deposit/source_ip, occurred_at의 같은 순간, 정상 received_at, detected=false/skipped=false 및 네 Rule false/detail null을 API와 대조한다. received_at은 API가 만든 시각이며 외부 호스트 시각 차이로 임의의 새 초단위 합격 기준을 만들지 않는다.

최소 비교 필드는 기존 기준의11열이다. 행 개수·phase·expected ID는 이11열의 대조를 돕는 출력이며 새 인수조건이 아니다. 이 사후 조회는 과거 사전0행 증적을 소급 생성하지 않는다. R1 원 실행 기록의 db_before=NOT_COLLECTED를 보존한다. 데이터가 없거나 다르면 추가 POST/DELETE 없이 실제 결과를 판정한다.

이 준비 블록은 새 회차 실행 허가가 아니다. 중앙이 기존 허용 범위와 시점에 따라 사용하며, 앱 운영복원·회수 우선순위에 개입하지 않는다.
'''
(HERE/'DB_POST_READONLY_PREPARED.md').write_text(header+script+footer,encoding='utf-8',newline='\n')
bash=Path('C:/Program Files/Git/bin/bash.exe')
check=subprocess.run([str(bash),'--noprofile','--norc','-n'],input=script,capture_output=True,text=True,encoding='utf-8',timeout=15)
assert check.returncode==0,check.stderr
bind=dict(at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds'),
          executed=False,bash_syntax_rc=0,sql_parser_runtime='NOT_RUN',
          r1=dict(account=account1,transaction_id=txn1,source='ACTUAL_POST'),
          r2=dict(account=account2,transaction_id=txn2,source='ACTUAL_POST' if r2 else 'PLANNED_TEMPLATE_NOT_ACTUAL'),
          sql_sha256=hashlib.sha256(sql.encode()).hexdigest())
(HERE/'DB_READ_PREPARATION.json').write_text(json.dumps(bind,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(bind,ensure_ascii=False))
