"""Local-only prepared observer: two fixed GETs per explicitly selected phase."""
import argparse, base64, datetime, hashlib, json, os, re, signal, socket
from urllib.parse import urlsplit

LIMIT = 262144

def valid_location(value):
    try:
        u = urlsplit(value)
        return (not u.username and not u.password and not u.query and not u.fragment
                and u.path == '/metrics'
                and ((not u.scheme and not u.netloc)
                     or (u.scheme == 'http' and u.hostname == '10.1.93.50' and u.port in (None,80))))
    except ValueError:
        return False

def classify(path, status, locations, complete):
    if not complete:
        return 'INCOMPLETE_STOP'
    if status == 404:
        return 'EXPECTED_404'
    if path == '/metrics/' and status in (301,302,303,307,308) and len(locations)==1 and valid_location(locations[0]):
        return 'EXPECTED_REDIRECT_NOT_FOLLOWED'
    return 'UNEXPECTED_STOP'

FIELD=re.compile(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+")
def header(line):
    if b':' not in line: raise ValueError('MALFORMED_HEADER')
    k,v=line.split(b':',1)
    if not FIELD.fullmatch(k) or any(c<32 and c!=9 or c==127 for c in v):
        raise ValueError('MALFORMED_HEADER')
    return k.lower(),v.strip(b' \t')

def parse_wire(raw):
    """Strict framing of the entire retained HTTP/1 response; never follow URLs."""
    if len(raw)>LIMIT or b'\r\n\r\n' not in raw: raise ValueError('INCOMPLETE_HEADERS')
    head,body=raw.split(b'\r\n\r\n',1);lines=head.split(b'\r\n')
    if not re.fullmatch(rb'HTTP/1\.[01] [1-5][0-9]{2} [\t\x20-\x7e\x80-\xff]*',lines[0]):
        raise ValueError('MALFORMED_STATUS')
    status=int(lines[0].split(b' ',2)[1]);headers=[header(line) for line in lines[1:]]
    lengths=[v for k,v in headers if k==b'content-length']
    encodings=[v.lower() for k,v in headers if k==b'transfer-encoding']
    locations=[v.decode('iso-8859-1') for k,v in headers if k==b'location']
    if len(lengths)>1 or len(encodings)>1 or (lengths and encodings):raise ValueError('AMBIGUOUS_FRAMING')
    if lengths and (not re.fullmatch(rb'[0-9]+',lengths[0]) or int(lengths[0])!=len(body)):
        raise ValueError('CONTENT_LENGTH_MISMATCH')
    if encodings:
        if encodings!=[b'chunked']: raise ValueError('UNSUPPORTED_TRANSFER_ENCODING')
        pos=0
        while True:
            end=body.find(b'\r\n',pos)
            if end<0:raise ValueError('TRUNCATED_CHUNK_SIZE')
            size=body[pos:end];pos=end+2
            # Reject unneeded extensions conservatively rather than guessing grammar.
            if not re.fullmatch(rb'[0-9a-fA-F]+',size):raise ValueError('INVALID_CHUNK_SIZE')
            n=int(size,16)
            if n>LIMIT:raise ValueError('CHUNK_SIZE_LIMIT')
            if n==0:
                while True:
                    end=body.find(b'\r\n',pos)
                    if end<0:raise ValueError('TRUNCATED_TRAILER')
                    line=body[pos:end];pos=end+2
                    if not line:break
                    k,_=header(line)
                    if k in (b'content-length',b'transfer-encoding',b'location'):raise ValueError('AMBIGUOUS_TRAILER')
                if pos!=len(body):raise ValueError('EXTRA_AFTER_MESSAGE')
                break
            if pos+n+2>len(body) or body[pos+n:pos+n+2]!=b'\r\n':raise ValueError('TRUNCATED_CHUNK_DATA')
            pos+=n+2
    return status,locations

def capture(path):
    now=lambda:datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    request=('GET '+path+' HTTP/1.1\r\nHost: 10.1.93.50\r\nAccept: */*\r\nConnection: close\r\n\r\n').encode('ascii')
    raw=bytearray(); result=dict(path=path,host='10.1.93.50',destination='10.1.93.50:80',
        started_at=now(),request_b64=base64.b64encode(request).decode(),rc=1)
    def alarm(*_): raise TimeoutError('TOTAL_DEADLINE_4S')
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,4)
    try:
        with socket.create_connection(('10.1.93.50',80),timeout=4) as s:
            result['local_socket']=list(s.getsockname());s.sendall(request)
            while len(raw)<=LIMIT:
                b=s.recv(min(8192,LIMIT+1-len(raw)))
                if not b: break
                raw.extend(b)
        status,locations=parse_wire(bytes(raw));complete=True
        verdict=classify(path,status,locations,complete)
        result.update(status=status,locations=locations,complete=complete,verdict=verdict,
                      rc=0 if verdict.startswith('EXPECTED_') else 2)
    except Exception as e:
        result.update(error=type(e).__name__,complete=False,verdict='CAPTURE_ERROR_STOP')
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
    result.update(finished_at=now(),wire_bytes=len(raw),wire_sha256=hashlib.sha256(raw).hexdigest(),
                  response_wire_b64=base64.b64encode(raw).decode())
    return result

if __name__=='__main__':
    import pwd
    p=argparse.ArgumentParser();p.add_argument('--phase',required=True,choices=['pre','during']);p.add_argument('--round-id',required=True)
    a=p.parse_args()
    assert socket.gethostname()=='edge01' and pwd.getpwuid(os.getuid()).pw_name=='svc_ansible' and os.geteuid()!=0
    results=[capture(path) for path in ('/metrics','/metrics/')]
    print(json.dumps(dict(phase=a.phase,round_id=a.round_id,source_host=socket.gethostname(),source_user='svc_ansible',
        redirects_followed=0,retries=0,results=results)))
    raise SystemExit(0 if all(r['rc']==0 for r in results) else 2)
