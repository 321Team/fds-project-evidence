BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '3s';
SELECT current_user, current_database(), current_setting('transaction_read_only');
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'transactions'
  AND column_name IN ('account_id', 'fds_detected', 'fds_evaluation_skipped')
ORDER BY column_name;
SELECT account_id, fds_detected, fds_evaluation_skipped FROM public.transactions WHERE false;
ROLLBACK;
