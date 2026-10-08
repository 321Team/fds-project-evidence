import copy,json,pathlib
from guard import patch_for
o={'metadata':{'uid':'fixed','resourceVersion':'1'},'data':{'rule':'inactive'}};candidate={'rule':'active'}
c=copy.deepcopy(o);c['metadata']['resourceVersion']='2';c['data']=candidate
def rejected(f):
 try:f();return False
 except AssertionError:return True
checks={
'activation_CAS':patch_for(o,o,candidate)[1]['value']=='1',
'restoration_CAS':patch_for(o,c,candidate,True)[1]['value']=='2',
'restoration_exact_original':patch_for(o,c,candidate,True)[-1]['value']==o['data'],
'already_original_noop':patch_for(o,o,candidate,True)==[],
'foreign_UID_rejected':rejected(lambda:patch_for(o,{**c,'metadata':{'uid':'foreign','resourceVersion':'2'}},candidate,True)),
'foreign_data_rejected':rejected(lambda:patch_for(o,{**c,'data':{'rule':'someone_else'}},candidate,True)),
'response_loss_candidate_restorable':bool(patch_for(o,c,candidate,True)),
'unrelated_data_change_rejected':rejected(lambda:patch_for(o,{**c,'data':{**candidate,'other':'new'}},candidate,True)),
'double_activation_rejected':rejected(lambda:patch_for(o,c,candidate))}
pathlib.Path(__file__).with_name('guard-tests.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8');print(sum(checks.values()),'/',len(checks));assert all(checks.values())
