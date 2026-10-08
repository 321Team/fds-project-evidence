import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path('/root/if05c-20261008-oo0o4gd4');sys.path.insert(0,str(root))
from runtime import Session,notified
s=Session(root,'readonly-followup');result={}
try:
 s.health();cm=s.cm();result['cm_sha256']=hashlib.sha256(cm['data']['p0-test-alert.yml'].encode()).hexdigest();result['projected_sha256']=s.projected()
 assert result['cm_sha256']==result['projected_sha256']==s.input['original_sha256']
 snap=s.snap('post-cleanup-resolved');original=json.loads((root/'original.json').read_text());assert cm['data']==original['data']
 events=[json.loads(l) for l in (root/'run-events.jsonl').read_text().splitlines()]
 before=next(x['data'] for x in events if x['kind']=='snapshot' and x['data']['tag']=='before')
 firing=json.loads((root/'firing.json').read_text())
 failed=[x for x in snap['notification_metrics'] if 'discord' in x and 'failed_total' in x and float(x.rsplit(' ',1)[1])!=0]
 result.update(snapshot=snap,original_bytes_restored=True,other_rules_unchanged=before['other_rules_sha256']==snap['other_rules_sha256'],discord_notifications_before=notified(before),discord_notifications_firing=notified(firing),discord_notifications_after=notified(snap),discord_failed_nonzero=failed,external_channel_read='NOT_VERIFIED')
 assert snap['rule']['state']=='inactive' and snap['rule']['query']=='vector(1) == 0' and snap['rule']['health']=='ok'
 assert not snap['am_alerts'] and result['other_rules_unchanged']
 assert notified(snap)==notified(before)+2 and notified(firing)==notified(before)+1 and not failed
 unit='if05c-recover-20261008-oo0o4gd4'
 q=subprocess.run(['systemctl','show',unit+'.timer',unit+'.service','-p','ActiveState','-p','SubState','-p','LoadState'],capture_output=True,timeout=10)
 result['recovery_units']={'rc':q.returncode,'stdout':q.stdout.decode(),'stderr':q.stderr.decode()};assert q.returncode==0 and q.stdout.decode().count('ActiveState=inactive')==2
 result['followup_rc']=0
except Exception as e:result.update(followup_rc=2,error=type(e).__name__+':'+str(e))
finally:s.save('post-observation.json',result);s.close()
print(json.dumps(result,indent=2));raise SystemExit(result['followup_rc'])
