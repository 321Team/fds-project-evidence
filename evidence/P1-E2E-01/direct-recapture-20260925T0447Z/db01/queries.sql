\pset pager off
\o psql-info.txt
select version(), current_user, now();
\o rules-recent20.txt
select now();
select occurred_at, fds_rules from transactions where fds_rules is not null order by occurred_at desc limit 20;
\o rules-r04-r07.txt
select now();
select occurred_at, fds_rules from transactions where fds_rules::jsonb @> '[{"rule_id":"R04","triggered":true}]' or fds_rules::jsonb @> '[{"rule_id":"R07","triggered":true}]' order by occurred_at desc limit 5;
\o rules-full-rows.txt
\x on
select 'R01' as rule, t.* from transactions t where t.fds_rules::jsonb @> '[{"rule_id":"R01","triggered":true}]' order by occurred_at desc limit 1;
select 'R02' as rule, t.* from transactions t where t.fds_rules::jsonb @> '[{"rule_id":"R02","triggered":true}]' order by occurred_at desc limit 1;
select 'R04' as rule, t.* from transactions t where t.fds_rules::jsonb @> '[{"rule_id":"R04","triggered":true}]' order by occurred_at desc limit 1;
select 'R07' as rule, t.* from transactions t where t.fds_rules::jsonb @> '[{"rule_id":"R07","triggered":true}]' order by occurred_at desc limit 1;
\x off
\o schema-transactions.txt
\d transactions
\o
