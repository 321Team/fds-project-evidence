RAW=b'{\n  "schema": "P1-CICD-delivery-gate-1",\n  "template_only": false,\n  "status": "APPROVED_FOR_DELIVERY",\n  "source": {\n    "approval_reference": "https://github.com/321Team/fds-msa/pull/27#pullrequestreview-5465278143",\n    "approved_by": "supreme33-kr",\n    "commit": "affbc69beef9967f7977d09a6fec14f7fb6c0e94",\n    "repository": "321Team/fds-msa"\n  },\n  "workflow": {\n    "repository": "321Team/infra-cicd",\n    "ref": "refs/heads/main",\n    "commit": "c9eff5fb2e50a690818a3e67347ab4a1bfc88f51",\n    "run_id": 37890963668,\n    "run_attempt": 1\n  },\n  "build_scan": {\n    "result": "PASS",\n    "source_commit": "affbc69beef9967f7977d09a6fec14f7fb6c0e94",\n    "workflow_commit": "c9eff5fb2e50a690818a3e67347ab4a1bfc88f51",\n    "run_id": 37890963668,\n    "run_attempt": 1,\n    "input_sha256": "72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3",\n    "scan_result_sha256": "75e24b4c3881eae5bb76e3c31d8436fcb23e56c7f513e38470d8c1dd03f27ef1",\n    "images": {\n      "transaction-api": {\n        "archive_sha256": "70da457069443c8b7af55d93d4e942ab4788bcfb9fe11506ee0482cd17bfaec3",\n        "manifest_digest": "sha256:ef0afe42feb0f9e50f54b5aaab99a34bbeb01f10bc9fb8a0580519101645dc39",\n        "config_digest": "sha256:64a98e1fce2934498b0a34328931370667133a938863f90f2b04d385be150445"\n      },\n      "fds-engine": {\n        "archive_sha256": "bb5951c6bb2cf113f0d7815fddc41c2b1e2c9cd69ccbd8794f13f2bc277d405f",\n        "manifest_digest": "sha256:de34afb7a557d6ccc844fb74613ebc971eb493260236acc35ef3051935122813",\n        "config_digest": "sha256:1662d1a6f2c8b06708f0e336936054f2db8f9c4ea37f6a8f3fb59e34777adc06"\n      }\n    },\n    "scan": {\n      "transaction-api": {\n        "scan": "PASS",\n        "exit_code": 0,\n        "counts": {\n          "HIGH": 0,\n          "CRITICAL": 0\n        },\n        "manifest_digest": "sha256:ef0afe42feb0f9e50f54b5aaab99a34bbeb01f10bc9fb8a0580519101645dc39",\n        "report_sha256": "a71cd8327c370a53a69976062eb45e68457786804de32d28432eb3c7cdbac39a"\n      },\n      "fds-engine": {\n        "scan": "PASS",\n        "exit_code": 0,\n        "counts": {\n          "HIGH": 0,\n          "CRITICAL": 0\n        },\n        "manifest_digest": "sha256:de34afb7a557d6ccc844fb74613ebc971eb493260236acc35ef3051935122813",\n        "report_sha256": "726cad9ff555e6f0100b85e0f519398a54e7861a874b24321e290e38f2102c87"\n      }\n    }\n  },\n  "harbor": {\n    "endpoint": "https://10.1.93.54",\n    "runner_tls_trust": "PASS",\n    "if09_ac02": "PASS",\n    "handoff_reference": "https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947371286",\n    "credential_reference": "actions-secret:HARBOR_CI_ROBOT_USERNAME/HARBOR_CI_ROBOT_TOKEN",\n    "repositories": {\n      "transaction-api": "10.1.93.54/fds/transaction-api",\n      "fds-engine": "10.1.93.54/fds/fds-engine"\n    }\n  },\n  "app_result_sha256": "e5e1416a5d62294f89cb30f19b685d3fc137cd52a5beda897ae9b9248a23e80f",\n  "source_evidence_directory": "FDS_CICD_AppWorkflow.57rithja",\n  "push_authorization": {\n    "workflow_sha": "2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7",\n    "reference": "https://github.com/321Team/fds-project-evidence/pull/208#issuecomment-6130830892",\n    "expires_at": "2026-10-13T12:00:00+09:00"\n  }\n}\n'

from pathlib import Path
from datetime import datetime, timezone
import os,pwd,socket,stat,hashlib,json
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000
assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-13T10:00:00+09:00')
home=Path(pwd.getpwuid(os.getuid()).pw_dir)
assert str(home)=='/home/server01_cicd-runner'
directory=home/'FDS_CICD_PushInputs'
for path in (home,directory):
 for q in (path,*path.parents):assert not q.is_symlink()
 s=path.stat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==1000 and stat.S_IMODE(s.st_mode)==0o700
name='push-20261013-window1200.json'
digest=hashlib.sha256(RAW).hexdigest()
assert digest=='13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89'
assert not os.path.lexists(home/'FDS_CICD_PushClaims'/(digest+'.json'))
os.umask(0o077)
dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
 fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=dfd)
 with os.fdopen(fd,'wb') as f:
  f.write(RAW);f.flush();os.fsync(f.fileno());before=os.fstat(f.fileno())
 os.fsync(dfd)
 fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=dfd)
 with os.fdopen(fd,'rb') as f:
  actual=f.read();after=os.fstat(f.fileno())
 assert actual==RAW and before.st_ino==after.st_ino
 assert stat.S_ISREG(after.st_mode) and after.st_uid==1000 and stat.S_IMODE(after.st_mode)==0o600 and after.st_nlink==1
 print(json.dumps(dict(status='STAGED',path=str(directory/name),bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),uid=after.st_uid,mode=oct(stat.S_IMODE(after.st_mode)),nlink=after.st_nlink,finished_at_utc=datetime.now(timezone.utc).isoformat())))
finally:os.close(dfd)
