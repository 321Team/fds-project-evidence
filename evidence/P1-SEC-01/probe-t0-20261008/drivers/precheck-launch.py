import base64,datetime,hashlib,json,os,pathlib,socket,subprocess,sys
root=pathlib.Path('/root/sec01-probe-20261008-98hudpso')
JOB='aW1wb3J0IGRhdGV0aW1lLGpzb24sb3MscGF0aGxpYixzdWJwcm9jZXNzLHN5cwpyb290PXBhdGhsaWIuUGF0aChfX2ZpbGVfXykucmVzb2x2ZSgpLnBhcmVudDttb2RlPXN5cy5hcmd2WzFdCmFzc2VydCBtb2RlIGluICgncHJlY2hlY2snLCdydW4nKTtvcy51bWFzaygwbzA3NykKbWFya2VyPXJvb3QvKG1vZGUrJy5vbmNlJyk7bWFya2VyLm9wZW4oJ3gnKS5jbG9zZSgpCmNvZGU9cm9vdC8nc291cmNlJztjaGVjaz1zdWJwcm9jZXNzLnJ1bihbJ3NoYTI1NnN1bScsJy1jJywnU0hBMjU2U1VNUyddLGN3ZD1jb2RlLGNhcHR1cmVfb3V0cHV0PVRydWUsdGltZW91dD0xMCkKYXNzZXJ0IGNoZWNrLnJldHVybmNvZGU9PTAsJ1NPVVJDRV9EUklGVCcKZW52PW9zLmVudmlyb24uY29weSgpO2VudlsnS0MnXT0na3ViZWN0bCAtLWt1YmVjb25maWc9L2V0Yy9rdWJlcm5ldGVzL2FkbWluLmNvbmYgLS1yZXF1ZXN0LXRpbWVvdXQ9MTBzJztlbnZbJ0NPTkZJUk0nXT0nWUVTJwphcmd2PVsnYmFzaCcsc3RyKGNvZGUvJ3Byb2JlLnNoJyksbW9kZV07c3RhcnQ9ZGF0ZXRpbWUuZGF0ZXRpbWUubm93KGRhdGV0aW1lLnRpbWV6b25lLnV0YykuaXNvZm9ybWF0KCkKd2l0aCAocm9vdC8obW9kZSsnLnN0ZG91dCcpKS5vcGVuKCd4YicpIGFzIG91dCwocm9vdC8obW9kZSsnLnN0ZGVycicpKS5vcGVuKCd4YicpIGFzIGVycjoKIHE9c3VicHJvY2Vzcy5ydW4oYXJndixjd2Q9cm9vdCxlbnY9ZW52LHN0ZG91dD1vdXQsc3RkZXJyPWVycikKcmVzdWx0PXsnbW9kZSc6bW9kZSwnYXJndic6YXJndiwnc291cmNlX2NvbW1pdCc6J2Q2ODY2MTg3YWUzMmFmMjg2Y2Q1ZDljNjUxY2RjYjRkNzA2ZjVmNTknLCdzdGFydGVkX3V0Yyc6c3RhcnQsJ2ZpbmlzaGVkX3V0Yyc6ZGF0ZXRpbWUuZGF0ZXRpbWUubm93KGRhdGV0aW1lLnRpbWV6b25lLnV0YykuaXNvZm9ybWF0KCksJ3JjJzpxLnJldHVybmNvZGV9Cihyb290Lyhtb2RlKycucmVzdWx0Lmpzb24nKSkud3JpdGVfdGV4dChqc29uLmR1bXBzKHJlc3VsdCxpbmRlbnQ9MikrJ1xuJykK'
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-control01'
os.umask(0o077)
for proc in pathlib.Path('/proc').glob('[0-9]*'):
 try: raw=(proc/'cmdline').read_bytes()
 except OSError: continue
 assert not (b'/probe.sh\0' in raw or b'/backup.sh\0' in raw),'EXISTING_TEST_PROCESS'
(root/'job.py').write_bytes(base64.b64decode(JOB))
with (root/'precheck-launch.stdout').open('xb') as out,(root/'precheck-launch.stderr').open('xb') as err:
 q=subprocess.Popen([sys.executable,str(root/'job.py'),'precheck'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
result={'pid':q.pid,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'job_sha256':hashlib.sha256((root/'job.py').read_bytes()).hexdigest()};(root/'precheck-launch.json').write_text(json.dumps(result));print(json.dumps(result))
