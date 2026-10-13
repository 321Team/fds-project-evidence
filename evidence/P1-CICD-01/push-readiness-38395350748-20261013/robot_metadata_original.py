"""Read only selected Robot/RBAC metadata. No credential columns or API token."""
import datetime, hashlib, json, os, shutil, socket, stat, subprocess, time
from pathlib import Path

assert os.geteuid() == 0 and socket.gethostname() == 'harbor01'
identity = {'hostname':socket.gethostname(), 'product_uuid':Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower(),
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
assert identity['product_uuid'] == '1e864d56-61f9-c443-d8f4-0ece2755a850'
docker = os.path.realpath(shutil.which('docker', path='/usr/sbin:/usr/bin:/sbin:/bin'))
s = os.stat(docker)
assert stat.S_ISREG(s.st_mode) and s.st_uid == 0 and not s.st_mode & 0o022
env = {'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/','LC_ALL':'C'}
fmt = '{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Config.Image}},"image_id":{{json .Image}},"status":{{json .State.Status}},"health":{{json .State.Health.Status}},"pid":{{json .State.Pid}},"started":{{json .State.StartedAt}},"restart_count":{{json .RestartCount}}}'
def inspect(target):
    p = subprocess.run([docker,'--host','unix:///run/docker.sock','inspect','--type','container','--format',fmt,target],
                       capture_output=True,timeout=8,env=env,cwd='/')
    assert p.returncode == 0
    return json.loads(p.stdout)
before = inspect('harbor-db')
assert before['id'] == 'e813fd25de4cd682061545470674284228512fe6a212cbd67f956d9782600b98'
assert before['name'] == '/harbor-db' and before['image'] == 'goharbor/harbor-db:v2.13.1'
assert before['status'] == 'running' and before['health'] == 'healthy'
sql = """BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='1s';
SELECT json_build_object(
 'observed_at',clock_timestamp(),
 'transaction_read_only',current_setting('transaction_read_only'),
 'robots',COALESCE((SELECT json_agg(json_build_object(
   'id',r.id,'stored_name',r.name,'project_id',r.project_id,'disabled',r.disabled,'visible',r.visible,
   'duration_days',r.duration,'expires_at_epoch',r.expiresat,
   'expires_at_kst',CASE WHEN r.expiresat=-1 THEN 'NEVER' ELSE to_char(to_timestamp(r.expiresat) AT TIME ZONE 'Asia/Seoul','YYYY-MM-DD HH24:MI:SS')||' KST' END,
   'expired',CASE WHEN r.expiresat=-1 THEN false ELSE r.expiresat <= extract(epoch FROM clock_timestamp()) END,
   'created_at',r.creation_time,'updated_at',r.update_time,
   'permissions',COALESCE((SELECT json_agg(json_build_object('scope',pp.scope,'project_name',pr.name,
       'resource',pp.resource,'action',pp.action,'effect',pp.effect) ORDER BY pp.scope,pp.resource,pp.action)
     FROM role_permission rp JOIN permission_policy pp ON pp.id=rp.permission_policy_id
     LEFT JOIN project pr ON pp.scope='/project/'||pr.project_id::text
     WHERE rp.role_type='robotaccount' AND rp.role_id=r.id),'[]'::json)
 ) ORDER BY r.id) FROM robot r WHERE r.name IN ('push','robot$push')),'[]'::json));
ROLLBACK;
"""
argv=[docker,'--host','unix:///run/docker.sock','exec','-i','--user','999:999',before['id'],
      '/usr/bin/psql','-X','-w','-v','ON_ERROR_STOP=1','--dbname=registry','--pset=pager=off','-A','-t','--file=-']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=subprocess.run(argv,input=sql.encode(),capture_output=True,timeout=12,env=env,cwd='/')
assert len(p.stdout) < 65536 and len(p.stderr) < 65536
out={'identity':identity,'before':before,'started_at_utc':started,'rc':p.returncode,
     'argv':argv,'sql':sql,'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(),
     'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),
     'read_only':True,'credential_fields_selected':False,'credential_authentication_test':False,
     'services_restarted':False,'files_placed':False}
if p.returncode == 0:
    rows=[json.loads(line) for line in p.stdout.decode().splitlines() if line.startswith('{')]
    assert len(rows)==1
    out['observation']=rows[0]
    assert out['observation']['transaction_read_only']=='on'
else:
    out['error_markers']={word:word.encode() in p.stderr.lower() for word in ('authentication','password','permission','does not exist','timeout')}
after=inspect(before['id'])
out.update(after=after,container_unchanged=before==after,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
assert before==after
assert identity['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
print(json.dumps(out))
