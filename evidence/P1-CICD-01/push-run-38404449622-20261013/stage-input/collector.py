RAW=b'{\n  "schema": "P1-CICD-delivery-gate-1",\n  "template_only": false,\n  "status": "APPROVED_FOR_DELIVERY",\n  "source": {\n    "approval_reference": "https://github.com/321Team/fds-msa/pull/27#pullrequestreview-5465278143",\n    "approved_by": "supreme33-kr",\n    "commit": "affbc69beef9967f7977d09a6fec14f7fb6c0e94",\n    "repository": "321Team/fds-msa"\n  },\n  "workflow": {\n    "repository": "321Team/infra-cicd",\n    "ref": "refs/heads/main",\n    "commit": "147f760298dd4a683ea58f2a887483769352b97d",\n    "run_id": 38395350748,\n    "run_attempt": 1\n  },\n  "build_scan": {\n    "result": "PASS",\n    "source_commit": "affbc69beef9967f7977d09a6fec14f7fb6c0e94",\n    "workflow_commit": "147f760298dd4a683ea58f2a887483769352b97d",\n    "run_id": 38395350748,\n    "run_attempt": 1,\n    "input_sha256": "72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3",\n    "scan_result_sha256": "17d9e4e08b3848c69eda4f9fb6b346e3c52971391a070a515be1c6770d374df7",\n    "images": {\n      "transaction-api": {\n        "archive_sha256": "ff3d145047f53b67f44b8a91994d7ab2b72998d9b276184b3c70a2148d52e3cf",\n        "manifest_digest": "sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0",\n        "config_digest": "sha256:ab34196baf2b878222857be47b200baed0151679a5b19fe15635ba50f77bffee"\n      },\n      "fds-engine": {\n        "archive_sha256": "319ab0af288d32a156feb1867193d3b7be0e663f2a17ee3efaa95aa505cd7031",\n        "manifest_digest": "sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d",\n        "config_digest": "sha256:b82d35a60e7a7f4a30366a926699fa4b673e69610f64fa0e7f294673ed12f4fc"\n      }\n    },\n    "scan": {\n      "transaction-api": {\n        "scan": "PASS",\n        "exit_code": 0,\n        "counts": {\n          "HIGH": 0,\n          "CRITICAL": 0\n        },\n        "manifest_digest": "sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0",\n        "report_sha256": "c44661c3c66efec190a8091019ca3aa043df39f940f9f8e9f1c36a673271a1a2"\n      },\n      "fds-engine": {\n        "scan": "PASS",\n        "exit_code": 0,\n        "counts": {\n          "HIGH": 0,\n          "CRITICAL": 0\n        },\n        "manifest_digest": "sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d",\n        "report_sha256": "446f6f389f26271ea81d9b5b1bc779fa83a6d72cd34615f0684e3c820f5d5f7c"\n      }\n    }\n  },\n  "harbor": {\n    "endpoint": "https://10.1.93.54",\n    "runner_tls_trust": "PASS",\n    "if09_ac02": "PASS",\n    "handoff_reference": "https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947371286",\n    "credential_reference": "actions-secret:HARBOR_CI_ROBOT_USERNAME/HARBOR_CI_ROBOT_TOKEN",\n    "repositories": {\n      "transaction-api": "10.1.93.54/fds/transaction-api",\n      "fds-engine": "10.1.93.54/fds/fds-engine"\n    }\n  },\n  "app_result_sha256": "239513de0766f9807f0503fac30fe0ea39d7255b793c2f561b23bb3d9b8bfd9d",\n  "source_evidence_directory": "FDS_CICD_AppWorkflow.3_geu2kf",\n  "push_authorization": {\n    "workflow_sha": "147f760298dd4a683ea58f2a887483769352b97d",\n    "reference": "https://github.com/321Team/fds-project-evidence/pull/217#issuecomment-6145950204",\n    "expires_at": "2026-10-14T00:30:00+09:00"\n  }\n}\n'

from pathlib import Path
from datetime import datetime, timezone
import os,pwd,socket,stat,hashlib,json
assert socket.gethostname()=='cicd-runner01' and os.geteuid()==1000
assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-13T22:30:00+09:00')
home=Path(pwd.getpwuid(os.getuid()).pw_dir)
assert str(home)=='/home/server01_cicd-runner'
directory=home/'FDS_CICD_PushInputs'
for path in (home,directory):
 for q in (path,*path.parents):assert not q.is_symlink()
 s=path.stat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==1000 and stat.S_IMODE(s.st_mode)==0o700
name='push-tbs38395350748-window0030.json'
digest=hashlib.sha256(RAW).hexdigest()
assert digest=='8b7b4f4e64c271b54167bc768e4e3afc1b2326c480683aaaf4aa0ff3e18c2b06'
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
