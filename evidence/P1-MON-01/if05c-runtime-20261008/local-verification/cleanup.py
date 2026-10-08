import re
def stop_recovery(unit,call):
    assert re.fullmatch(r'if05c-recover-[a-z0-9-]+',unit),'BAD_UNIT'
    names=[unit+'.timer',unit+'.service']
    for attempt in range(3):
        raw=call(['systemctl','show',*names,'-p','ActiveState']).decode()
        states=[l.split('=',1)[1] for l in raw.splitlines() if l.startswith('ActiveState=')]
        assert len(states)==2 and all(x in ('inactive','active','activating','deactivating') for x in states),'UNKNOWN_UNIT_STATE'
        if states==['inactive','inactive']:return
        assert attempt<2,'CLEANUP_NOT_CONFIRMED'
        call(['systemctl','stop',*[name for name,state in zip(names,states) if state!='inactive']])
