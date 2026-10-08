import json,pathlib
from guard import corroborate
c={'expect':'BLOCKED','source_ip':'10.1.93.105','source_port':56105}
r={'actual':'EPERM','errno':1,'stage':'send','bound':['10.1.93.105',56105]}
a=['[5:300] -A host -j DROP'];b=['[6:357] -A host -j DROP']
checks={
'EPERM_send_with_drop':corroborate(c,r,a,b),
'EPERM_bind_rejected':not corroborate(c,{**r,'stage':'bind'},a,b),
'EPERM_without_drop_rejected':not corroborate(c,r,a,a),
'wrong_errno_rejected':not corroborate(c,{**r,'errno':13},a,b),
'wrong_source_rejected':not corroborate(c,{**r,'bound':['10.1.93.107',56105]},a,b),
'connected_rejected':not corroborate(c,{**r,'actual':'CONNECTED'},a,b),
'timeout_without_drop_rejected':not corroborate(c,{**r,'actual':'TIMEOUT','stage':'connect'},a,a),
'timeout_with_drop':corroborate(c,{**r,'actual':'TIMEOUT','stage':'connect'},a,b),
'rule_change_rejected':not corroborate(c,r,a,['[6:357] -A another -j DROP']),
'DNS_error_rejected':not corroborate({'expect':'DNS_REPLY'},{'actual':'DNS_REPLY','rcode':2},a,a)}
pathlib.Path(__file__).with_name('guard-mock.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(sum(checks.values()),'/',len(checks));assert all(checks.values())
