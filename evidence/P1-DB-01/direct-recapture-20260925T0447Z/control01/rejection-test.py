import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('10.1.93.55', 5432))
    print('CONNECTED - unexpected')
except Exception as e:
    print('REJECTED as expected:', repr(e))
