"""O01 1차 원본 탐색 보조: AC07 원본 파일에서 지정 필드만 그대로 출력한다(판정 없음, 원본 수정 없음).
실행: 저장소 루트(C:\\o01\\ev)에서  python -I -B C:\\o01\\result\\o01_explore.py
"""
import json
from pathlib import Path

A = Path('evidence/P1-CICD-01/ac07-native-runtime-20261014')


def load(rel):
    return json.loads((A / rel).read_text(encoding='utf-8'))


print('== 1. 명령·실행 호스트·시각·rc  [raw/native-execute.receipt.json]')
r = load('raw/native-execute.receipt.json')
argv = r['argv']
print('  started_at_utc :', r['started_at_utc'])
print('  finished_at_utc:', r['finished_at_utc'])
print('  rc             :', r['rc'])
print('  ssh target     :', next(a for a in argv if a.startswith('fds-')))
print('  remote command :', ' '.join(argv[argv.index(next(a for a in argv if a.startswith('fds-'))) + 1:])[:240], '...')

print('\n== 2. SSAR 25건과 실제 GET 2건  [raw/native-execute.stdout]')
o = load('raw/native-execute.stdout')['runner_observation']
perms = o['permissions']
print('  basis:', o['basis'], '| RUNNER_TOKEN_AUTH:', o['RUNNER_TOKEN_AUTH'], '| EFFECTIVE_RBAC_CHECK:', o['EFFECTIVE_RBAC_CHECK'], '| DEPLOY:', o['DEPLOY'])
print('  subject:', o['credential']['subject'], '| issued', o['credential']['issued_at'], '| expires', o['credential']['expires_at'], '| server_revocation', o['credential']['server_revocation'])
print('  permissions total:', len(perms), '| allowed:', sum(p['allowed'] for p in perms), '| denied:', sum(not p['allowed'] for p in perms),
      '| allowed==expected 전부:', all(p['allowed'] == p['expected'] for p in perms))
for p in perms:
    a = p['attributes']
    print('   ', 'ALLOW' if p['allowed'] else 'deny ', a.get('verb'), (a.get('group') or 'core') + '/' + a.get('resource', '') + ('/' + a['subresource'] if a.get('subresource') else ''), a.get('namespace', '-'), a.get('name', ''))
print('  deployments GET:', [(d['namespace'], d['name'], d['uid']) for d in o['deployments']])

print('\n== 3. 실패 수집과 성공 재조회  [raw/rbac-before/, raw/rbac-before-r2/]')
for rel in ('raw/rbac-before/receipt.json', 'raw/rbac-before-r2/receipt.json'):
    d = load(rel)
    print(' ', rel, '| rc', d['rc'], '|', d['started_at_utc'], '| classification', d.get('classification'), '| token_issued', d.get('token_issued'), '| server_files_written', d.get('server_files_written'))
print('  rbac-before stderr 앞부분:', (A / 'raw/rbac-before/stderr.txt').read_text(encoding='utf-8', errors='replace')[:300].replace('\n', ' / '))

print('\n== 4. 코드·리뷰·병합 결속  [raw/SOURCE_BINDING.json, references/pr82-reviews.json]')
b = load('raw/SOURCE_BINDING.json')
print('  reviewed_head:', b['reviewed_head'], '| merge:', b['merge'], '| files:', len(b['files']), '| 모두 reviewed_head_bytes_equal:', all(f.get('reviewed_head_bytes_equal') for f in b['files']))
rv = load('references/pr82-reviews.json')
rv = rv if isinstance(rv, list) else rv.get('reviews', [])
for x in rv:
    print('  review:', (x.get('user') or {}).get('login', x.get('author')), x.get('state'), x.get('commit_id', '')[:12], x.get('submitted_at', ''))

print('\n== 5. 전후 불변·회수·점유 해제  [raw/POSTCHECK_SUMMARY.json, raw/WINDOW_RELEASE.json, raw/cleanup-*]')
print(' ', json.dumps(load('raw/POSTCHECK_SUMMARY.json'), ensure_ascii=False))
print(' ', json.dumps(load('raw/WINDOW_RELEASE.json'), ensure_ascii=False))
for rel in sorted(p.relative_to(A).as_posix() for p in (A / 'raw').glob('cleanup-*') if p.is_dir()):
    d = load(rel + '/receipt.json')
    print('  cleanup:', rel, '| rc', d.get('rc'), '|', d.get('started_at_utc'))
