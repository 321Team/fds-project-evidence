from pathlib import Path
import sys
p=Path(__file__).resolve().parent
app=sys.argv[1];assert app in ('fds-engine','transaction-api')
source=(p/'recovery_template.remote.py').read_text(encoding='utf-8')
source=source.replace('__APP__',repr(app)).replace('__MON_SOURCE__',repr((p.parent/'current-mon/collector.py').read_bytes()))
compile(source,app,'exec');(p/(app+'-recovery.remote.py')).write_text(source,encoding='utf-8')
