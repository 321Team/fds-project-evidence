import datetime,errno,json,socket,struct,sys,time
c=json.loads(sys.argv[1]);t=time.monotonic();out={'case':c,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'socket'}
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM if c['protocol']=='UDP' else socket.SOCK_STREAM);s.settimeout(3)
try:
 out['stage']='bind';s.bind((c['source_ip'],c['source_port']));out['bound']=list(s.getsockname())
 out['stage']='connect';s.connect((c['destination'],c['port']))
 if c['protocol']=='TCP':out['actual']='CONNECTED'
 else:
  ident=0x53b2;qname=c['qname'];wire=b''.join(bytes([len(x)])+x.encode('ascii') for x in qname.split('.'))+bytes([0])
  packet=struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+wire+struct.pack('!HH',1,1)
  out['stage']='send';out['sent_bytes']=s.send(packet)
  out['stage']='recv';reply=s.recv(4096);xid,flags,qd,an,ns,ar=struct.unpack('!HHHHHH',reply[:12])
  assert xid==ident and flags&0x8000 and qd==1
  out.update(actual='DNS_REPLY',rcode=flags&15,answers=an,reply_bytes=len(reply),qname=qname)
except socket.timeout:out['actual']='TIMEOUT'
except PermissionError as e:out.update(actual='EPERM' if e.errno==errno.EPERM else 'ERROR',errno=e.errno,error=str(e))
except Exception as e:out.update(actual='ERROR',error=type(e).__name__+':'+str(e))
finally:s.close()
out.update(elapsed_seconds=round(time.monotonic()-t,3),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(out))
# A zero child RC for BLOCKED is only a candidate; parent requires kernel DROP corroboration.
ok=out['actual']==c['expect'] and (out['actual']!='DNS_REPLY' or out['rcode']==0)
if c['expect']=='BLOCKED':ok=out['actual'] in ('EPERM','TIMEOUT') and out['stage'] in ('connect','send','recv')
sys.exit(0 if ok else 3)
