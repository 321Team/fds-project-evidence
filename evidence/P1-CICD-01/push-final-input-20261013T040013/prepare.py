"""One-shot local preparation and publication of the user's execution decision.
No server files, credentials or workflow dispatch. Do not rerun after success.
"""
from pathlib import Path
from datetime import datetime, timezone
import base64, hashlib, importlib.util, json, shutil, subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OLD = P.parent / 'p1-push-precheck-20261013'
MAIN = '2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
assert not (P / 'PREPARED.json').exists()
(P / 'github').mkdir()
(P / 'robot-metadata').mkdir()
rows = []
def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(name, data):
    (P / name).write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())
def api(name, endpoint):
    at = datetime.now(timezone.utc).isoformat()
    r = subprocess.run(['gh','api',endpoint], capture_output=True, check=True)
    (P / 'github' / (name + '.json')).write_bytes(r.stdout)
    rows.append({'name':name,'endpoint':endpoint,'at_utc':at,'sha256':sha(r.stdout)})
    return json.loads(r.stdout)

main = api('main','repos/321Team/infra-cicd/commits/main')
assert main['sha'] == MAIN
pr = api('pr208','repos/321Team/fds-project-evidence/pulls/208')
assert pr['state'] == 'open' and pr['head']['sha'] == 'e4d934bb2b15c1027db2389989bf5238064462f5'
reviews = api('pr208-reviews','repos/321Team/fds-project-evidence/pulls/208/reviews')
collabs = api('collaborators','repos/321Team/infra-cicd/collaborators')
secrets = api('secret-names','repos/321Team/infra-cicd/actions/secrets')
runners = api('runners','repos/321Team/infra-cicd/actions/runners')
running = api('running','repos/321Team/infra-cicd/actions/runs?status=in_progress&per_page=100')
queued = api('queued','repos/321Team/infra-cicd/actions/runs?status=queued&per_page=100')
workflows = api('workflows','repos/321Team/infra-cicd/contents/.github/workflows?ref=' + MAIN)
uses = []
for f in workflows:
    obj = api('workflow-' + Path(f['path']).stem, 'repos/321Team/infra-cicd/contents/' + f['path'] + '?ref=' + MAIN)
    raw = base64.b64decode(obj['content'])
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == obj['sha']
    keys = [n for n in ('HARBOR_CI_ROBOT_USERNAME','HARBOR_CI_ROBOT_TOKEN') if n.encode() in raw]
    if keys: uses.append({'path':f['path'],'git_blob':obj['sha'],'secret_names':keys})
assert len(uses) == 1 and uses[0]['path'] == '.github/workflows/app-push.yml'
for name in ('robot_metadata_read.py','receipt.json','RESULT.md'):
    shutil.copyfile(P.parent / 'p1-robot-metadata-20261013' / name, P / 'robot-metadata' / name)
r = json.loads((P / 'robot-metadata/receipt.json').read_bytes())
assert r['rc'] == 0 and r['observation']['rc'] == 0
assert sha((P / 'robot-metadata/robot_metadata_read.py').read_bytes()) == r['source_sha256']
robot = r['observation']['observation']['robots']
assert len(robot) == 1
robot = robot[0]
assert robot['id'] == 3 and robot['stored_name'] == 'push' and robot['disabled'] is False and robot['expired'] is False
assert {(p['project_name'],p['resource'],p['action'],p['effect']) for p in robot['permissions']} == {('fds','repository','pull',''),('fds','repository','push','')}
assert robot['expires_at_epoch'] == 1792311415

decision = '''## Phase 1 APP Push 실행 범위 결정 — 사용자 직접 허용 기록

CODEX_ASSISTED / 이권욱(GWONUK). 현재 Codex 대화에서 구체 실행 범위를 제시했고, 사용자가 **“일괄 허용 — 해당 창·동시 변경 배제·Secret 2개 회수”**로 직접 답했습니다. 이 기록은 그 결정을 옮긴 것이며, 이하영/이재환의 독립 입력 검토나 이미 실행된 Push 결과를 대신하지 않습니다.

- 기존 infra-cicd main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`, APP Source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, TBS Run37890963668/1 공급을 사용합니다. 기존 입력을 검토한 뒤 새0600 record 배치 → execute=false 1회 → 성공 시 fresh Scan/두 이미지 Push execute=true 1회입니다.
- 유효 종료 **2026-10-13 09:00 KST**, 실제 Push Job 시작 한도 **07:15 KST**. 코드90분 제한과 정리15분을 고려합니다. 늦으면 시작하지 않고, 대기 Job은 취소합니다. 만료가 실행 중 요청의 자동 종료 장치는 아니므로 실제 Run/Attempt·정리를 추적합니다.
- Harbor 변경·사후 관측 비중첩, TLS/health, main 일치와 idle 확인 후 시작합니다. Repository Secret이 main 전용 경계가 아니라는 기존 잔여 범위를 수용하고, 해당 Secret/Workflow의 회차 중 다른 사용·변경을 배제합니다.
- 종료 후 이번에 직접 등록한 Actions Secret `HARBOR_CI_ROBOT_USERNAME`(18:34:05Z), `HARBOR_CI_ROBOT_TOKEN`(18:34:27Z) 두 개를 회수합니다. 정리 시 갱신·공유 소비가 발견되면 임의 삭제하지 않고 인수합니다. Harbor Robot 자체·원 보관 credential·다른 Secret은 유지합니다.
- 새 delivery nonce/tag 두 개만 쓰며 배포/기존 태그/Pod·서비스/Robot권한/Phase2는 변경하지 않습니다. 부분 실패면 claim·receipt·원격 상태를 보존하며 자동 retry/태그 삭제를 하지 않습니다.

03:49:19 KST 실측으로 `robot$push` 활성·fds Pull/Push·만료10/18 17:16:55를 확인했습니다. 계정 보유자/권한/만료 재회신은 필요 없습니다. GitHub에 저장한 token과 실제 인증 성공은 아직 관측하지 않았습니다.

**다음 독립 검토는 이번 exact JSON/SHA·유효창·Secret 통제에 한정하여 이 PR에서 요청합니다.** 병합된 실행 코드의 재리뷰·새 PR·별도 Harbor Lead GO를 추가하지 않습니다. 아직 Runner 입력 배치, dispatch, fresh Scan, Push/Deploy를 실행하지 않았습니다. 최종 exact hash는 다음 커밋/요청에 연결합니다.
'''
save('USER_AUTHORIZATION.json', {'source':'DIRECT_USER_REPLY_IN_THIS_CODEX_CHAT',
    'reply':'일괄 허용 — 해당 창·동시 변경 배제·Secret 2개 회수',
    'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'execution_scope_sha256':sha((P / 'EXECUTION_SCOPE.md').read_bytes()),
    'expires_at':'2026-10-13T09:00:00+09:00','latest_execution_job_start':'2026-10-13T07:15:00+09:00',
    'independent_input_review':'PENDING','actual_push_executed':False})
save('request-user-decision-comment.json', {'body':decision})
response = subprocess.run(['gh','api','repos/321Team/fds-project-evidence/issues/208/comments',
    '--method','POST','--input',str(P / 'request-user-decision-comment.json')],capture_output=True,check=True)
save('USER_DECISION_COMMENT.json',json.loads(response.stdout))
comment = json.loads(response.stdout)['html_url']

# Keep the unapproved flags until independent review, as required by the scope.
# Reviewers receive an exact, deterministic activation diff and its output hash.
record = json.loads((OLD / 'push.draft.json').read_bytes())
record['push_authorization']['reference'] = comment
record['push_authorization']['expires_at'] = '2026-10-13T09:00:00+09:00'
save('push.pending.json',record)
activated = json.loads(json.dumps(record))
activated['template_only'] = False
activated['status'] = 'APPROVED_FOR_DELIVERY'
raw = (json.dumps(activated,ensure_ascii=False,indent=2)+'\n').encode()
plan = {'schema':'P1-PUSH-EXACT-INPUT-REVIEW-1','status':'PENDING_INDEPENDENT_REVIEW',
    'pending_file':'push.pending.json','pending_sha256':sha((P/'push.pending.json').read_bytes()),
    'changes_after_independent_review_only':[
        {'pointer':'/template_only','before':True,'after':False},
        {'pointer':'/status','before':record['status'],'after':'APPROVED_FOR_DELIVERY'}],
    'serialization':'UTF-8 without BOM; json.dumps(ensure_ascii=False, indent=2) + LF',
    'target_filename':'push-20261013-0400.json','target_sha256':sha(raw),
    'target_file_materialized':False,'runner_record_placed':False,
    'user_execution_authorization':comment,'workflow_sha':MAIN,
    'latest_execution_job_start':'2026-10-13T07:15:00+09:00','expires_at':'2026-10-13T09:00:00+09:00'}
save('ACTIVATION_PLAN.json',plan)
spec = importlib.util.spec_from_file_location('reviewed_gate', OLD/'source/delivery_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
pending_verdict = gate.evaluate(record,'pre_push')
assert set(pending_verdict['reasons']) == {'TEMPLATE_OR_UNCONFIRMED_INPUT','DELIVERY_INPUT_NOT_APPROVED'}
target_verdict = gate.evaluate(activated,'pre_push')
assert target_verdict['decision'] == 'CONDITIONS_MATCH'
save('VERIFICATION.json',{'result':'PREPARED_PENDING_INDEPENDENT_INPUT_REVIEW',
    'robot_metadata':'OBSERVED','robot_authentication':'NOT_RUN',
    'main':MAIN,'same_main_secret_references':uses,'other_branch_secret_use':'NOT_PROVEN_ABSENT',
    'current_repo_roles':[{'login':x['login'],'role_name':x['role_name']} for x in collabs],
    'active_runs':running['total_count'],'queued_runs':queued['total_count'],
    'pending_gate':pending_verdict,'post_review_candidate_static_gate':target_verdict,
    'post_review_candidate_sha256':sha(raw),'candidate_runtime_approval_proven_by_gate':False,
    'adapter_validation':'NOT_RUN','fresh_scan':'NOT_RUN','push':'NOT_EXECUTED',
    'independent_input_review':'PENDING','user_execution_authorized':True,
    'phase2_work':False,'secret_values_read':False})
save('GITHUB_RECEIPTS.json',rows)
save('PREPARED.json',{'decision_comment':comment,'pending_sha256':plan['pending_sha256'],
    'target_sha256':plan['target_sha256'],'prepared_at_utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'decision_comment':comment,'target_sha256':plan['target_sha256'],
    'record_placed':False,'input_review':'PENDING'},ensure_ascii=False))
