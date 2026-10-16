"""Recover only this exact session while its original binding is still valid."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lifecycle',HERE/'lifecycle.py')
life=importlib.util.module_from_spec(spec);spec.loader.exec_module(life)
c=life.c

def main():
    os.umask(0o077);root=HERE.parent
    try:life.host_identity(root);life.secure(HERE)
    except (Exception,KeyboardInterrupt) as exc:
        print(json.dumps({'execution':'REJECTED','initial_error':life.error(exc),'mutation_requests':0}));return 1
    evidence=life.Evidence(root,'recovery');commands=life.Commands(evidence)
    initial=None;cleanup={'status':'HANDOFF'}
    with life.Signals() as signals:
        try:
            with life.SessionLock(root,create=False):
                try:
                    life.assert_no_active(root)
                    raw=c.read_protected_record(root/'control/host.json')
                    c.require(raw is not None,'CONTROL_MISSING')
                    control=json.loads(raw);life.binding(control,root)
                    c.require(hashlib.sha256((HERE/'manifest.json').read_bytes()).hexdigest()==control['manifest_sha256'],'MANIFEST_HASH')
                    manifest=json.loads((HERE/'manifest.json').read_bytes())
                    for rel in ('contract.py','lifecycle.py','cleanup_session.py'):
                        c.require(hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==manifest['files'][rel]['sha256'],'RECOVERY_SUPPLY_CHANGED')
                    resolved=c.resolve_cid(root,root.name,control['manifest_sha256'])
                    evidence.save('CID_SOURCES.json',resolved)
                    c.require(resolved['cid'] is not None,'CID_SOURCE_UNCONFIRMED')
                    cleanup=life.recover(commands,root,control,resolved['cid'],signals)
                except (Exception,KeyboardInterrupt) as exc:initial=life.error(exc)
                signals.recovering=True
                return life.finish(evidence,commands,'RECOVERY_ONLY',cleanup,initial,signals)
        except (Exception,KeyboardInterrupt) as exc:
            initial=life.error(exc);signals.recovering=True
            return life.finish(evidence,commands,'RECOVERY_ONLY',cleanup,initial,signals)

if __name__=='__main__':raise SystemExit(main())
