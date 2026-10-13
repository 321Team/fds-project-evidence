"""Record the explicit user window change; prepare local review inputs only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess
P=Path(__file__).resolve().parent
OLD=P.parent/'p1-push-final-input-20261013'
assert not (P/'WINDOW_CHANGE.json').exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def save(n,x): (P/n).write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
body='''## Push 실행창 변경 — 사용자 지시 반영

CODEX_ASSISTED / 이권욱 / 2026-10-13 KST. 사용자가 현재 대화에서 “리뷰어의 요청이 있어야만 한다면 시작한도를 10:00 종료창을 12:00로 맞춰야 할듯”이라고 지시했습니다. 기존 [일괄 허용](https://github.com/321Team/fds-project-evidence/pull/208#issuecomment-6130701774)의 시간만 아래와 같이 변경합니다.

- **실제 Push Job 시작 한도: 오늘10:00 KST**, 종료창 및 입력 만료: **오늘12:00 KST**.10:00 이후 시작은 금지하며 그때까지 대기열에 남은 실제 Push Job은 취소합니다. 사전검증과 입력 독립 검토는 실제 실행 전에 완료해야 합니다.
- 현 Workflow의 최대90분 뒤 결과 확인·정리에30분 여유를 둡니다. 입력 만료가 실행 중 요청을 벽시계에 자동 종료하는 장치는 아니므로 기존 상태 추적·중단·정리 책임은 유지합니다.
- 기존 두 이미지·고정 Source/Workflow·1회 실행·Harbor 비중첩·다른 Secret/Workflow 사용·변경 배제·종료 후 Actions Robot Secret2개 회수 조건은 같습니다. 새 Robot·권한 확대·Deploy는 포함하지 않습니다.
- 필요한 것은 리뷰어의 별도 착수 요청이나 새 Lead GO가 아니라 기존 실행기 계약의 **exact 입력 독립 검토**입니다. 변경된 만료/이 결정 URL 때문에 입력 해시는 다시 계산하며 새 hash를 후속 커밋에 연결합니다. 기존 `28ae13b5…665d`/07:15·09:00 입력을 실행하지 않습니다.

기존 입력에 아직 독립 리뷰가 없는 상태를 확인했습니다. 원본 공급·Robot 관측·코드 검증을 다시 수행하지 않고 **시간 변경과 새 해시만** 기존 PR208의 검토 요청에 반영합니다. 실제 Runner 입력 배치/dispatch/Scan/Push/Secret 삭제는 하지 않았습니다.
'''
save('request-window-comment.json',{'body':body})
out=subprocess.run(['gh','api','repos/321Team/fds-project-evidence/issues/208/comments','--method','POST','--input',str(P/'request-window-comment.json')],capture_output=True,check=True)
comment=json.loads(out.stdout)
save('WINDOW_DECISION_COMMENT.json',comment)
url=comment['html_url']
previous=read(OLD/'push.pending.json')
pending=json.loads(json.dumps(previous))
pending['push_authorization']['reference']=url
pending['push_authorization']['expires_at']='2026-10-13T12:00:00+09:00'
save('push.pending.json',pending)
plan=read(OLD/'ACTIVATION_PLAN.json')
old_target=plan['target_sha256']
candidate=json.loads(json.dumps(pending))
for change in plan['changes_after_independent_review_only']:
    key=change['pointer'][1:]
    assert candidate[key]==change['before']
    candidate[key]=change['after']
raw=(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n').encode()
target=hashlib.sha256(raw).hexdigest()
plan.update(pending_sha256=sha(P/'push.pending.json'),target_filename='push-20261013-window1200.json',
    target_sha256=target,user_execution_authorization=url,latest_execution_job_start='2026-10-13T10:00:00+09:00',
    expires_at='2026-10-13T12:00:00+09:00')
save('ACTIVATION_PLAN.json',plan)
for name,mode in [('DISPATCH.validate.json',False),('DISPATCH.execute.json',True)]:
    save(name,{'ref':'main','inputs':{'record_name':plan['target_filename'],'record_sha256':target,'execute':mode}})
scope=(OLD/'EXECUTION_SCOPE.md').read_text(encoding='utf-8')
scope=scope.replace('# Phase 1 APP Push 단일 회차 실행 범위','# Phase 1 APP Push 단일 회차 실행 범위 — 12:00 창 개정')
scope=scope.replace('## 제안 유효창과 시작 조건','## 사용자 변경 지시에 따른 유효창과 시작 조건')
scope=scope.replace('2026-10-13 09:00:00 KST','2026-10-13 12:00:00 KST').replace('07:15','10:00')
scope=scope.replace('결과/정리 15분 여유','결과/정리 30분 여유')
scope=scope.replace('두 Actions Secret만 회차 종료 뒤 삭제**하는 안이다.','두 Actions Secret만 회차 종료 뒤 삭제**하는 승인된 범위다.')
scope+='\n이번 창 변경: '+url+' . 이전07:15/09:00 창을 대체하며 기존 행위·정리 범위는 유지한다.\n'
(P/'EXECUTION_SCOPE.md').write_bytes(scope.encode())
card=(OLD/'RUN_CARD.md').read_text(encoding='utf-8').replace(old_target,target)
card=card.replace('push-20261013-0400.json','push-20261013-window1200.json').replace('07:15','10:00').replace('09:00','12:00')
card=card.replace('verify_bundle.py','verify_revision.py')
(P/'RUN_CARD.md').write_bytes(card.encode())
save('WINDOW_CHANGE.json',{'schema':'P1-PUSH-WINDOW-CHANGE-1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'source':'DIRECT_USER_INSTRUCTION_IN_THIS_CHAT',
    'user_instruction':'리뷰어의 요청이 있어야만 한다면 시작한도를 10:00 종료창을 12:00로 맞춰야 할듯',
    'base_collection':'evidence/P1-CICD-01/push-final-input-20261013T040013',
    'base_head':'5c15353192f53076172a4495a6e756547c3bf98a',
    'previous_pending_sha256':sha(OLD/'push.pending.json'),'previous_target_sha256':old_target,
    'previous_latest_start':'2026-10-13T07:15:00+09:00','previous_expiry':'2026-10-13T09:00:00+09:00',
    'latest_execution_job_start':plan['latest_execution_job_start'],'expires_at':plan['expires_at'],
    'user_authorization_reference':url,'execution_scope_sha256':sha(P/'EXECUTION_SCOPE.md'),
    'target_sha256':target,'input_review':'PENDING','runner_record_placed':False,
    'runtime':'NOT_RUN','credential_changes':'NONE','previous_window':'SUPERSEDED_DO_NOT_USE'})
print(json.dumps({'window_comment':url,'target_sha256':target,'latest_start':plan['latest_execution_job_start'],'expiry':plan['expires_at']}))
