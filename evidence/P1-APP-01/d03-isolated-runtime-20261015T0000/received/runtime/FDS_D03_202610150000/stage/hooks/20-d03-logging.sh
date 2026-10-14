psql -X -v ON_ERROR_STOP=1 -d fds_lab <<'SQL' || exit 1
ALTER SYSTEM SET log_statement='all';
ALTER SYSTEM SET log_line_prefix='D03 [%p] ';
ALTER SYSTEM SET lc_messages='C';
ALTER SYSTEM SET logging_collector='off';
ALTER SYSTEM SET log_destination='stderr';
SQL
