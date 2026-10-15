BEGIN READ ONLY;
SET LOCAL statement_timeout = '3s';
SET LOCAL lock_timeout = '1s';
SELECT json_build_object('kind','identity','database',current_database(),
 'user',current_user,'at',current_timestamp,'timezone',current_setting('TimeZone'),
 'transaction_read_only',current_setting('transaction_read_only'));
WITH expected(phase, account_id, transaction_id) AS (
 VALUES ('R1','SIM_ac09_cd01e613d57641eb83548e9283d0f60d_P01','22b7c46c-cd07-4539-a7fc-8890b67b12ee'),
        ('R2','SIM_ac09_3451e56c57bc490e8d156cede958229f_P01','1827bd8a-a921-49f9-83f7-22529e903451')
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
