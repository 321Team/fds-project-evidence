#!/usr/bin/env python3
import os
from pathlib import Path
import runpy
import sys
import unittest

def audit(event, args):
    if event in ('socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo'):
        raise RuntimeError('LOCAL_TEST_NETWORK_FORBIDDEN')
    if event == 'subprocess.Popen':
        executable = os.path.basename(os.fsdecode(args[0]))
        if executable in ('gh','podman','docker','ssh','scp','sudo','ansible','ansible-playbook','curl','wget'):
            raise RuntimeError('LOCAL_TEST_EXTERNAL_COMMAND_FORBIDDEN:'+executable)

sys.addaudithook(audit)
repo = Path(sys.argv[1]).resolve()
target = sys.argv[2]
if target == 'DISCOVER':
    sys.path.insert(0,str(repo/'tests'))
    suite = unittest.defaultTestLoader.discover(str(repo/'tests'),pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
sys.argv = [str(repo/target),'-v']
runpy.run_path(str(repo/target),run_name='__main__')

