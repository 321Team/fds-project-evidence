"""Offline evidence correspondence checks; no network, server changes or source execution."""
import ast, base64, hashlib, json, pathlib
out=pathlib.Path(__file__).resolve().parent
originals=out/'server-originals'; drivers=out/'drivers'
def sha(b): return hashlib.sha256(b).hexdigest()
receipt=json.loads((out/'RECEIPT.json').read_text())
fetch={'recovery_unit':receipt['recovery_unit']}
checks={}
for name, info in receipt['files'].items():
    data=(originals/name).read_bytes()
    checks['received_hash:'+name]=sha(data)==info['sha256'] and len(data)==info['size']
parsed=ast.parse((drivers/'stage.py').read_text(encoding='utf-8-sig'))
stage_payloads=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FILES' for a in n.targets))
for name in ['runtime.py','guard.py','input.json']:
    checks['installed_source_matches_local:'+name] = (originals/name).read_bytes() == base64.b64decode(stage_payloads[name])
for stem in ['preflight','config','staged','launch','observation','fetched-final']:
    invocation=json.loads((drivers/(stem+'-invocation.json')).read_text(encoding='utf-8-sig'))
    checks['driver_source_hash:'+stem] = sha((drivers/invocation['source']).read_bytes()) == invocation['source_sha256']
    checks['driver_transport_rc:'+stem] = invocation['rc']==0
def read(name): return json.loads((originals/name).read_text())
events=[json.loads(l) for l in (originals/'run-events.jsonl').read_text().splitlines()]
before=next(e['data'] for e in events if e['kind']=='snapshot' and e['data']['tag']=='before')
firing=read('firing.json'); restore=read('restore-confirmed.json'); post=read('post-observation.json'); status=read('status.json')
checks.update({
 'one_real_activation_one_restoration':len([e for e in events if e['kind']=='patch_result' and not e['data']['dry_run']])==2,
 'firing_rule_and_am':firing['rule']['state']=='firing' and len(firing['am_alerts'])==1,
 'restored_inactive':restore['snapshot']['rule']['state']=='inactive' and restore['snapshot']['rule']['query']=='vector(1) == 0',
 'post_inactive_am_empty':post['snapshot']['rule']['state']=='inactive' and post['snapshot']['am_alerts']==[],
 'sender_count_0_1_2':[post[k] for k in ['discord_notifications_before','discord_notifications_firing','discord_notifications_after']]==[0,1,2],
 'discord_failure_zero':post['discord_failed_nonzero']==[],
 'original_and_projected_hash':post['cm_sha256']==post['projected_sha256']==restore['original_sha256'],
 'other_rules_unchanged':post['other_rules_unchanged'],
 'health_23_no_down':all(e['data']['up'][0]['value'][1]=='23' and e['data']['down']==[] for e in events if e['kind']=='health'),
 'original_failure_preserved':status['rc']==3 and status['restore']=='CONFIRMED' and status['restore_error']['detail']=='COMMAND_FAILED',
 'readonly_followup_rc0':post['followup_rc']==0,
 'recovery_units_inactive':fetch['recovery_unit']['rc']==0 and fetch['recovery_unit']['stdout'].count('ActiveState=inactive')==2,
 'pf_children_reaped':len([e for e in events if e['kind']=='pf_closed'])==2 and all(e['data']['reaped'] for e in events if e['kind']=='pf_closed'),
 'external_receipt_not_claimed':post['external_channel_read']=='NOT_VERIFIED',
 'no_other_active_am_at_snapshots':all(e['data']['other_am_alert_count']==0 for e in events if e['kind']=='snapshot'),
})
expected=json.loads((out/'ANALYSIS.json').read_text())['checks']
assert checks==expected, 'CORRESPONDENCE_CHANGED'
assert all(checks.values()), checks
print(json.dumps({'passed':sum(checks.values()),'total':len(checks)},indent=2))
