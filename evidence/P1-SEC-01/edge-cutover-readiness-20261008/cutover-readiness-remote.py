import datetime,difflib,hashlib,json,os,pathlib,re,socket,subprocess
assert socket.gethostname().split('.')[0]=='edge01'
result={'hostname':socket.gethostname(),'uid':os.geteuid(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidates':[],'errors':[]}
for p in sorted(pathlib.Path('/etc/nginx').rglob('*')):
 if not p.is_file() or not (p.suffix=='.conf' or p.name=='nginx.conf'):continue
 try:
  raw=p.read_bytes(); text=raw.decode('utf8');lines=text.split('\n')
 except (OSError,UnicodeError) as e:result['errors'].append({'path':str(p),'error':str(e)});continue
 start=[i for i,l in enumerate(lines) if re.match(r'^\s*upstream\s+transaction_api\s*\{',l)]
 if not start:continue
 item={'path':str(p),'before_sha256':hashlib.sha256(raw).hexdigest(),'mode':oct(p.stat().st_mode&0o777),'uid':p.stat().st_uid,'mtime_ns':p.stat().st_mtime_ns,'start_count':len(start)}
 if len(start)==1:
  s=start[0];e=next((i for i in range(s+1,len(lines)) if re.match(r'^\s*\}',lines[i])),None)
  item['upstream_block']=lines[s:e+1] if e is not None else []
  item['shape_ready']=False
  if e is not None:
   changed=lines.copy();old=[];new={};extra=[]
   for i in range(s+1,e):
    l=lines[i];cr='\r' if l.endswith('\r') else '';l=l[:-1] if cr else l
    m=re.match(r'^(\s*)(server\s+10\.1\.93\.50:30080\b[^;]*;.*)$',l)
    if m:old.append(i);changed[i]=m.group(1)+'# '+m.group(2)+'  # E-K3S, Edge Cutover <RUN>'+cr;continue
    m=re.match(r'^(\s*)#\s*(server\s+10\.1\.93\.(105|107|108):30080\b[^;]*;.*)$',l)
    if m:new.setdefault(m.group(3),[]).append(i);changed[i]=m.group(1)+m.group(2)+cr;continue
    if re.match(r'^\s*server\s',l):extra.append(i+1)
   item['shape_ready']=len(old)==1 and sorted(new)==['105','107','108'] and all(len(v)==1 for v in new.values()) and not extra
   if item['shape_ready']:
    diff=list(difflib.unified_diff(lines,changed,fromfile=str(p),tofile=str(p)+' (candidate, not applied)',n=0,lineterm=''))
    item['candidate_diff']='\n'.join(diff)
    item['candidate_note']='RUN unresolved; candidate is not an execution input or applied file'
 result['candidates'].append(item)
for unit in ('nginx','k3s'):
 p=subprocess.run(['systemctl','is-active',unit],capture_output=True,timeout=8)
 result[unit]={'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(result,ensure_ascii=False,indent=2))
