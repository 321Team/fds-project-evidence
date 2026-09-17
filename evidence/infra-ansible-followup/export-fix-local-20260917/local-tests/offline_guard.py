import os
import sys

def install():
    def audit(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo'):
            raise RuntimeError('LOCAL_TEST_NETWORK_FORBIDDEN')
        if event=='subprocess.Popen' and os.path.basename(os.fsdecode(args[0])) in (
                'gh','podman','docker','ssh','scp','sudo','ansible','ansible-playbook','curl','wget'):
            raise RuntimeError('LOCAL_TEST_EXTERNAL_COMMAND_FORBIDDEN')
    sys.addaudithook(audit)

