from pathlib import Path
import datetime as dt,importlib.util,json
BASE=Path(__file__).resolve().parent;R=BASE/'phase1-short-load-window-20261014-1415'
def j(p):return json.loads(p.read_bytes())
b=j(R/'CONFIRMED_WINDOW.json');v=j(R/'before-validated.json');db=j(R/'DB_BEFORE_ACCEPTED.json')
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
assert dt.datetime.fromisoformat(b['start_at'])<=now<=dt.datetime.fromisoformat(b['latest_start'])
assert b['db_before_after_available'] and b['harbor_app_db_mon_nodes_other_writer_nonoverlap']
assert v['passed'] and (now-dt.datetime.fromisoformat(v['at_kst'])).total_seconds()<120
assert db['run']==b['run'] and db['count']==0 and db['rc']==0
assert 0<=(now-dt.datetime.fromisoformat(db['db_timestamp'])).total_seconds()<=300
assert not (R/'actual-load-once').exists(),'LOCAL_ATTEMPT_EXISTS_NO_RERUN'
source=(R/'edge_launch_once.py').read_bytes();compile(source,'unchanged-generator-launch','exec')
spec=importlib.util.spec_from_file_location('transport',BASE/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=R
receipt=t.run('actual-load-once','10.1.93.50',source,500,False)
print(json.dumps({'run':b['run'],'rc':receipt['rc'],'automatic_retry':False}))
