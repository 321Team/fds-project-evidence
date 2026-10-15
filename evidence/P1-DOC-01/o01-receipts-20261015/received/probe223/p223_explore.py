"""O01 Probe223 원본 탐색 보조: 지정 원본 파일의 필드를 판정 없이 출력한다(원본 수정·서버 호출 없음).
실행: 저장소 루트(C:\\o01\\ev)에서  python -I -B C:\\o01\\result-probe223\\p223_explore.py
"""
import datetime as dt
import json
from pathlib import Path

A = Path('evidence/P1-K8S-01/http-probe-runtime-20261014T0950')
KST = dt.timezone(dt.timedelta(hours=9))


def load(rel):
    return json.loads((A / rel).read_text(encoding='utf-8'))


def kst(utc):
    return dt.datetime.fromisoformat(utc.replace('Z', '+00:00')).astimezone(KST).strftime('%H:%M:%S')


print('== 1. 실행 계정·명령·시각·rc  [apply-once/receipt.json, remote-originals/input.json]')
r = load('apply-once/receipt.json')
print('  started_at_kst :', r['started_at_kst'], '| finished_at_kst:', r['finished_at_kst'], '| rc:', r['rc'])
print('  route          :', r['route'])
b = load('remote-originals/input.json')['binding']
print('  target binding :', {k: b.get(k) for k in ('host', 'namespace', 'pod_name', 'pod_uid', 'container_name', 'pid', 'boot_id')})
print('  container_id   :', b.get('container_id'))
print('  arguments      :', json.dumps(load('remote-originals/input.json')['arguments'], ensure_ascii=False)[:300])

print('\n== 2. STOP·CONT와 원 프로세스 종료  [remote-originals/events.jsonl]')
for line in (A / 'remote-originals/events.jsonl').read_text(encoding='utf-8').splitlines():
    e = json.loads(line)
    print('  ', kst(e['utc']), 'KST', e['event'])

print('\n== 3. Ready·Endpoint·liveness·동일 Pod 재시작  [observer.jsonl 300 tick]')
ticks = [json.loads(l) for l in (A / 'observer.jsonl').read_text(encoding='utf-8').splitlines()]
uid = b.get('pod_uid')
prev = None
seen_events = set()
for t in ticks:
    pod = next((p for p in t['queries']['pods']['items'] if p['uid'] == uid), None)
    ready = next((c['status'] for c in (pod or {}).get('conditions', []) if c['type'] == 'Ready'), None)
    c0 = ((pod or {}).get('containers') or [{}])[0]
    in_ep = any(ep.get('targetRef', {}).get('uid') == uid and ep.get('conditions', {}).get('ready')
                for s in t['queries']['endpoints']['items'] if s['name'].startswith('fds-engine-') and 'metrics' not in s['name']
                for ep in s.get('endpoints', []))
    state = (ready, in_ep, c0.get('restartCount'), c0.get('containerID', '')[-12:], pod is not None and pod.get('uid'))
    if state != prev:
        print('  tick', t['tick'], kst(t['utc']), 'KST | Ready=', ready, '| engine Endpoint ready=', in_ep,
              '| restartCount=', c0.get('restartCount'), '| containerID ..', c0.get('containerID', '')[-12:], '| same UID=', pod is not None)
        prev = state
    for ev in t['queries']['events']['items']:
        io = ev.get('involvedObject', {})
        key = (ev.get('reason'), ev.get('metadata', {}).get('name'), ev.get('count'))
        if io.get('uid') == uid and key not in seen_events and ev.get('reason') in ('Unhealthy', 'Killing', 'Started', 'Created', 'Pulled'):
            seen_events.add(key)
            print('     event', ev.get('reason'), '| count', ev.get('count'), '| last', ev.get('lastTimestamp'), '|', (ev.get('message') or '')[:110])
print('  observer receipt:', {k: load('observer.receipt.json')[k] for k in ('start_utc', 'end_utc', 'rc', 'review')})
print('  ticks:', len(ticks), '| other_workloads_healthy 모두 True:', all(t.get('other_workloads_healthy') for t in ticks),
      '| nodes_healthy 모두 True:', all(t.get('nodes_healthy') for t in ticks))

print('\n== 4. 실패 관측과 회복 보충  [worker-http.*, http-recovery/stdout.json]')
w = load('worker-http.receipt.json')
print('  worker-http receipt:', {k: w[k] for k in ('start_utc', 'end_utc', 'rc', 'review')})
print('  worker-http.jsonl 줄 수:', len((A / 'worker-http.jsonl').read_text(encoding='utf-8').splitlines()))
print('  worker-http.stderr 마지막:', (A / 'worker-http.stderr').read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1])
h = load('http-recovery/stdout.json')
print('  http-recovery:', 'scope', h['scope'], '| stable60_pass', h['stable60_pass'], '| rows', len(h['rows']), '| signals', json.dumps(h['signals'], ensure_ascii=False)[:200])
print('  첫 행 / 마지막 행:', json.dumps(h['rows'][0], ensure_ascii=False)[:200], '/', json.dumps(h['rows'][-1], ensure_ascii=False)[:200])

print('\n== 5. MON·영향 범위·회복  [mon-during, mon-stable, recovery-edge]')
md = load('mon-during/stdout.json')
print('  mon-during: scope', md.get('scope'), '| forwarder_stopped', md.get('forwarder_stopped'), '| queries', list(md['queries'])[:8] if isinstance(md['queries'], dict) else len(md['queries']))
ms = load('mon-stable/stdout.json')
print('  mon-stable:', ms['started_utc'], '~', ms['finished_utc'], '| stable60_pass', ms['stable60_pass'], '| rows', len(ms['rows']), '| review', ms.get('review'))
re_ = load('recovery-edge/stdout.json')
print('  recovery-edge:', re_['host'], re_['started_at_utc'], '| api_mutations', re_['api_mutations'], '| db_writes', re_['db_writes'], '| http', json.dumps(re_['http'], ensure_ascii=False)[:250])

print('\n== 6. 실행기 공급·수신 바이트와 리뷰  [remote-originals-receipt, GITHUB_MERGE_REVIEW_RECEIPT.json]')
ro = load('remote-originals-receipt/stdout.json')
print('  remote-originals-receipt:', ro['utc'], '| files', json.dumps(ro['files'], ensure_ascii=False)[:300], '| new_container', ro.get('new_container'))
g = load('GITHUB_MERGE_REVIEW_RECEIPT.json')
print('  GitHub receipt read_utc:', g['read_utc'])
for rec in g['records'] if isinstance(g['records'], list) else g['records'].values():
    print('   ', json.dumps(rec, ensure_ascii=False)[:220])

print('\n== 7. kubelet journal  [kubelet-journal-utc/stdout.json]')
k = load('kubelet-journal-utc/stdout.json')
print('  rc', k['rc'], '| stdout:', (k['stdout'] or '').strip()[:120], '| stderr:', (k['stderr'] or '').strip()[:120])
