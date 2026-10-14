import os,subprocess,sys
os.umask(0o077)
p=subprocess.run(['/usr/bin/python3', '-B', '-I', '/home/svc_ansible/p1-app-20261014-1025/supply/rg.py', 'run', '/home/svc_ansible/p1-app-20261014-1025/results'])
sys.exit(p.returncode)
