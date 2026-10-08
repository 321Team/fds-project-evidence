import datetime as dt,json,sys
from pathlib import Path
KST=dt.timezone(dt.timedelta(hours=9))
start=dt.datetime.fromisoformat('2026-10-08T20:26:49+09:00').timestamp()
end=dt.datetime.fromisoformat('2026-10-08T20:27:52+09:00').timestamp()
def stamp(t):return dt.datetime.fromtimestamp(t,KST).isoformat()
d=json.loads(Path(sys.argv[1]).read_bytes())
assert d['rc']==0 and d['pid']==d['post_pid'] and d['netns']==d['post_netns']
assert len(d['queries'])==4 and all(q['rc']==0 and q['status']=='success' and q['http_status']==200 for q in d['queries'])
out={'schema':'fds.w4-history-analysis.v1','http_5xx_verdict':'NOT_MEASURED','counter_series':[],'http_metric_names':{},'app_up_series':[]}
for q in d['queries']:
    if q['label'].startswith('http_metric_names'):
        out['http_metric_names'][q['label']]=[x['metric']['__name__'] for x in q['results']]
        continue
    for x in q['results']:
        if x['metric'].get('job')!='transaction-api':continue
        values=x['values']; inside=[(t,v) for t,v in values if start<=t<=end]
        row={'metric':x['metric'],'samples_total':len(values),'samples_in_w4':len(inside),
             'first_kst':stamp(values[0][0]),'last_kst':stamp(values[-1][0]),
             'unique_values':sorted(set(v for t,v in values)),
             'within_series_decreases':sum(float(b[1])<float(a[1]) for a,b in zip(values,values[1:])),
             'max_observed_interval_seconds':round(max((b[0]-a[0] for a,b in zip(values,values[1:])),default=0),3)}
        if q['label']=='scrape_health_raw_5m':
            row['zero_samples_kst']=[stamp(t) for t,v in values if v=='0']
            out['app_up_series'].append(row)
        else:out['counter_series'].append(row)
out['limitations']=['Raw range samples, not repeated query_range interpolation.',
    'Per-series absence/deletion, final scrape gaps and process replacement remain; zero samples do not establish HTTP 5xx absence.',
    'Metric name discovery is two historical instants for names containing http/request, not an inventory of every central logging system.',
    'Pod identity for historical IPs is not independently mapped here. Counter resets across different series are not treated as same-process changes.']
print(json.dumps(out,ensure_ascii=False,indent=2))
