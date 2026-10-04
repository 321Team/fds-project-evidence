import socket, ssl, struct, time
H, P = "10.1.93.55", 5432
def startup():
    kv = b"user\0fds_app\0database\0fdsdb\0\0"
    b = struct.pack(">I", 196608) + kv
    return struct.pack(">I", len(b) + 4) + b
def readmsg(s):
    data = b""
    s.settimeout(5)
    try:
        while True:
            c = s.recv(4096)
            if not c:
                break
            data += c
            if len(data) >= 5 and len(data) >= 1 + struct.unpack(">I", data[1:5])[0]:
                break
    except Exception as e:
        return "RECV_" + type(e).__name__, data
    return "OK", data
def parse(data):
    if not data:
        return "EMPTY"
    t = chr(data[0])
    if t == "E":
        d = {}
        for f in data[5:].split(b"\0"):
            if f:
                d[f[:1].decode()] = f[1:].decode("utf-8", "replace")
        return "ErrorResponse S=%s C=%s M=%s" % (d.get("S"), d.get("C"), d.get("M"))
    if t == "R":
        return "AuthRequest code=%d (pg_hba ALLOWED - closed without password)" % struct.unpack(">I", data[5:9])[0]
    return "type=" + t
print("time", time.strftime("%Y-%m-%d %H:%M:%S %Z"))
for mode in ("PLAIN", "SSL"):
    try:
        s = socket.create_connection((H, P), timeout=5)
        print(mode, "local", s.getsockname()[0], "-> %s:%d TCP_CONNECTED" % (H, P))
        if mode == "SSL":
            s.sendall(struct.pack(">II", 8, 80877103))
            r = s.recv(1)
            print(mode, "SSLRequest reply", r)
            if r == b"S":
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s)
                print(mode, "TLS", s.version())
        s.sendall(startup())
        st, d = readmsg(s)
        s.close()
        print(mode, st, parse(d))
    except Exception as e:
        print(mode, "ERROR", type(e).__name__, e)
