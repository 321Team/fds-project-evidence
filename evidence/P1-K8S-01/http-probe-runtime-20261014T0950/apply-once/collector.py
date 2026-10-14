import subprocess,sys
p=subprocess.run(['/usr/bin/python3', '-B', '-I', '/var/tmp/p1-http-probe-source-20261014-0945/engine_stop.py', 'apply', '/var/tmp/p1-http-probe-source-20261014-0945/observed-binding.json', '--source-sha256', '8b9fe37dd0bcdbd09e0c7d5e7fb41eaa9e25d47fb56223bbab6273081251cc32', '--start', '2026-10-14T09:45:00+09:00', '--latest-start', '2026-10-14T09:55:00+09:00', '--end', '2026-10-14T10:20:00+09:00', '--output', '/var/tmp/p1-http-probe-20261014-0945'])
sys.exit(p.returncode)
