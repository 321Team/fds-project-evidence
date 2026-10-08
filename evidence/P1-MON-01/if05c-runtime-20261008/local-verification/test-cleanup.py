import json,pathlib
from cleanup import stop_recovery
unit='if05c-recover-fixture'
def case(initial,want,broken=False):
 state=list(initial);stops=[]
 def call(args):
  if args[1]=='show':return ('\n'.join('ActiveState='+x for x in state)+'\n').encode()
  stops.append(args[2:])
  if not broken:
   for i,n in enumerate((unit+'.timer',unit+'.service')):
    if n in args:state[i]='inactive'
  return b''
 try:stop_recovery(unit,call);return stops==want
 except AssertionError:return want=='REJECT'
checks={
'inactive_unloaded_no_stop':case(['inactive','inactive'],[]),
'active_timer_only':case(['active','inactive'],[[unit+'.timer']]),
'active_service_only':case(['inactive','active'],[[unit+'.service']]),
'both_active':case(['active','active'],[[unit+'.timer',unit+'.service']]),
'unknown_rejected':case(['unknown','inactive'],'REJECT'),
'incomplete_rejected':case(['inactive'],'REJECT'),
'active_persistent_rejected':case(['active','inactive'],'REJECT',True),
'deactivating_checked':case(['deactivating','inactive'],[[unit+'.timer']])}
pathlib.Path(__file__).with_name('cleanup-tests.json').write_text(json.dumps(checks,indent=2)+'\n');print(sum(checks.values()),'/',len(checks));assert all(checks.values())
