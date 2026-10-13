#!/usr/bin/env python3
"""#13 — vpn 재실행 무변경(AC-5) 확인. Plan만, Apply 없음.

비용: 없음. 조회와 Plan만 한다. state는 쓰지 않고 native lock(.tflock)만 잠깐 생겼다 지워진다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, vpn WORKDIR(~/iac11-vpn-20261012-020352) 안에서 실행.
같은 source·입력: #11 vpn Apply에 쓴 source/ 10파일(36c18e2a)·vpn.plan.tfvars.json(bc658c60)·bin/terraform 1.16.4를 그대로 쓴다.
보안: MFA 코드와 임시 자격증명은 메모리에서만 쓰고 파일에 쓰지 않는다. state 원문은 내려받지 않는다.
판정: plan -detailed-exitcode 0 = No changes(PASS) / 2 = 변경 있음(STOP, 차이 기록) / 그 외 = STOP.
"""
import datetime, getpass, hashlib, json, os, subprocess, sys, tarfile, tempfile
from pathlib import Path

ACCOUNT = "774055931866"
REGION = "ap-northeast-2"
ME = "321team-hayeoung"
ROLE_NAME = "FDS-IaC-Operator"
ROLE = f"arn:aws:iam::{ACCOUNT}:role/{ROLE_NAME}"
ROLE_ID = "AROA3IOKUF7NEM6P7ZKPK"
BUCKET = f"fds-tfstate-{ACCOUNT}-{REGION}"
STATE_KEY = "phase2/vpn/terraform.tfstate"
LOCK_KEY = STATE_KEY + ".tflock"
SOURCE_MAIN = "36c18e2a3c8353314e3f618db4f0d6db578b2805"
APPLIED_PLAN_SHA256 = "0bb10dc983b46b0145c94f8e26f553fe2487d175452d6f40a17e3d1116c01e23"
TFVARS_SHA256 = "bc658c60569a106fc77a062dda2e983d1775862f54f329ef2f28840996683ee3"
TF_VERSION = "1.16.4"
AWS_PROVIDER = "6.66.0"
EXPECTED_STATE_COUNT = 8
MANIFEST = {
    "terraform/vpn/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/vpn/amazon-ssm-agent.gpg": "aaa3f054d9c0fb037e3e110e213cf721392429baa4a65c9e5e8b558b64c80fba",
    "terraform/vpn/backend.hcl.example": "abdda61dea092f7c3ce467e3db2faf9393d7a0b3634f4353c0fe93bf4e8cfc46",
    "terraform/vpn/bootstrap.sh.tftpl": "0acde3c1787b5c3a52b8f4f5329d2bf71c97f3c5c6bd596e93d5a324a7698e93",
    "terraform/vpn/main.tf": "29054493be43ce63720ffa5592e10bba728e39c053dd99267c301c168867f2b3",
    "terraform/vpn/outputs.tf": "ea9f3d9a5e2be0a339f515ef11cac05efc4ae593f3968cdf7e3cab1aa24e8367",
    "terraform/vpn/session-document.tf": "60adebd8f88a4326096cc383594e17053402105f206765fa5556b831bf83b96c",
    "terraform/vpn/tests/vpn.tftest.hcl": "8d9ea6dd3ab7d3e500c481efc19823b85e8ef037abed3b78e763f150f8b858d6",
    "terraform/vpn/variables.tf": "620f24ff58a4aa4c347b2b82fb9c92ce86450ef51555f1b9c28b66dce755be4e",
    "terraform/vpn/versions.tf": "10834006cf0aeca35c112e635b752fecf154da3a0c5ea87c40cb54504870fcca",
}

P = Path.cwd()
S = P / "source"
TF = P / "bin" / "terraform"
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d-%H%M%S")
E = P / f"evidence-vpn-replan-{STAMP}"
os.umask(0o077)
records = []
base = dict(os.environ)
roleenv = None
summary = {"executor": ME, "source_main": SOURCE_MAIN, "applied_plan_sha256": APPLIED_PLAN_SHA256,
           "apply": "NOT_RUN", "status": "STARTED", "checks": {}, "warnings": []}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def save(name, data):
    (E / name).write_bytes(data)


def call(name, args, env=None, allowed=(0,), timeout=60, shown=None, stdout_dir=None):
    t = now()
    print("RUN", name, flush=True)
    try:
        r = subprocess.run(args, env=env or base, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        records.append({"name": name, "argv": shown or args, "started_utc": t, "finished_utc": now(), "rc": None, "result": "TIMEOUT"})
        raise RuntimeError(name + " timeout — lock 상태부터 확인")
    if stdout_dir:  # state 사본이 들어가는 출력은 증적 묶음 밖에 두고 해시만 기록
        (stdout_dir / (name + ".stdout")).write_bytes(r.stdout)
    else:
        save(name + ".stdout", r.stdout)
    save(name + ".stderr", r.stderr)
    records.append({"name": name, "argv": shown or args, "started_utc": t, "finished_utc": now(), "rc": r.returncode,
                    "stdout_kept_outside_evidence": bool(stdout_dir), "stdout_sha256": hashlib.sha256(r.stdout).hexdigest(), "stderr_sha256": hashlib.sha256(r.stderr).hexdigest()})
    print("RC", name, r.returncode, flush=True)
    if r.returncode not in allowed:
        raise RuntimeError(f"{name} rc={r.returncode}")
    return r


def aws_args(args):
    return ["aws", *args, "--region", REGION, "--output", "json", "--no-cli-pager",
            "--cli-connect-timeout", "10", "--cli-read-timeout", "20"]


def aws(name, args, env=None, allowed=(0,)):
    return json.loads(call(name, aws_args(args), env, allowed, 45).stdout or b"{}")


def listing(name, env):
    d = aws(name, ["s3api", "list-objects-v2", "--bucket", BUCKET, "--prefix", STATE_KEY, "--max-keys", "10", "--no-paginate"], env)
    assert not d.get("IsTruncated")
    return sorted(o["Key"] for o in d.get("Contents", []))


def state_head(name, env):
    h = aws(name, ["s3api", "head-object", "--bucket", BUCKET, "--key", STATE_KEY], env)
    return {k: h.get(k) for k in ("VersionId", "ETag", "LastModified", "ContentLength", "ServerSideEncryption")}


try:
    E.mkdir(exist_ok=False)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("iac13_vpn_replan.py", Path(__file__).read_bytes())
    assert TF.exists() and S.exists(), "vpn WORKDIR(~/iac11-vpn-20261012-020352)에서 실행하세요 (source/, bin/terraform 필요)"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    summary["checks"]["source_10_files_match_36c18e2a"] = True
    VF = P / "vpn.plan.tfvars.json"
    assert VF.exists() and hashlib.sha256(VF.read_bytes()).hexdigest() == TFVARS_SHA256, "tfvars 해시 불일치 — STOP"
    summary["checks"]["tfvars_match_bc658c60"] = True
    if (P / "vpn.tfplan").exists():
        summary["applied_plan_file_sha256_recheck"] = hashlib.sha256((P / "vpn.tfplan").read_bytes()).hexdigest()
    assert not (S / "terraform/vpn/terraform.tfvars").exists()
    assert not list((S / "terraform/vpn").glob("*.auto.tfvars*"))
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    assert not (Path.home() / ".terraformrc").exists(), "~/.terraformrc exists"
    summary["terraform_binary_sha256"] = hashlib.sha256(TF.read_bytes()).hexdigest()

    me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요 (root/타인 금지)"
    summary["account_guard"] = me["Account"] == ACCOUNT
    assert summary["account_guard"], "계정 불일치 — STOP"
    # 버킷 설정 조회는 IaC 역할에 없음(GetBucketLocation만) → Apply 때와 같이 본인 사용자 권한으로 조회
    ver = aws("pre-versioning", ["s3api", "get-bucket-versioning", "--bucket", BUCKET])
    summary["checks"]["bucket_versioning_enabled"] = ver.get("Status") == "Enabled"
    serial = subprocess.run(aws_args(["iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"]),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
    if not serial or serial == "null":
        serial = input("MFA 장치 ARN 입력: ").strip()

    code = getpass.getpass("MFA 6자리 (화면에 안 보임): ").strip()
    t = now()
    r = subprocess.run(aws_args(["sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                                 "--serial-number", serial, "--token-code", code, "--duration-seconds", "1800"]),
                       capture_output=True, timeout=45)
    code = None
    shown = aws_args(["sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                      "--serial-number", serial, "--token-code", "REDACTED", "--duration-seconds", "1800"])
    if r.returncode != 0:
        save("assume-role.stderr", r.stderr)
        records.append({"name": "assume-role", "argv": shown, "started_utc": t, "finished_utc": now(), "rc": r.returncode})
        raise RuntimeError(f"assume-role rc={r.returncode}")
    obj = json.loads(r.stdout)
    c = obj.pop("Credentials")
    obj["Credentials"] = {"redacted": True, "Expiration": c["Expiration"]}
    red = json.dumps(obj, indent=2).encode()
    save("assume-role.stdout", red)
    records.append({"name": "assume-role", "argv": shown, "started_utc": t, "finished_utc": now(), "rc": 0,
                    "stdout_sha256": hashlib.sha256(red).hexdigest(), "note": "Credentials removed in memory before write"})
    roleenv = dict(base)
    roleenv.update(AWS_ACCESS_KEY_ID=c["AccessKeyId"], AWS_SECRET_ACCESS_KEY=c["SecretAccessKey"],
                   AWS_SESSION_TOKEN=c["SessionToken"], AWS_MAX_ATTEMPTS="1", TF_IN_AUTOMATION="1",
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac13-vpn-replan-tfdata-", dir="/tmp"))
    c = r = None

    ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    # state 무결성 (AC-4 일부): key 있음, lock 없음, versioning, 현재 버전 기록
    summary["before_keys"] = listing("before-keys", roleenv)
    assert STATE_KEY in summary["before_keys"], "vpn state가 없음 — STOP"
    assert LOCK_KEY not in summary["before_keys"], "lock이 남아 있음(다른 writer?) — STOP, 권욱 님과 확인"
    summary["state_before"] = state_head("state-head-before", roleenv)

    cmd = [str(TF), "-chdir=" + str(S / "terraform/vpn")]
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"
    tv = json.loads(call("terraform-version", cmd + ["version", "-json"], roleenv).stdout)
    summary["terraform_version"] = tv.get("terraform_version")
    summary["aws_provider"] = (tv.get("provider_selections") or {}).get("registry.terraform.io/hashicorp/aws")
    summary["checks"]["tool_versions"] = summary["terraform_version"] == TF_VERSION and summary["aws_provider"] == AWS_PROVIDER
    assert summary["checks"]["tool_versions"], f"버전 불일치 {summary['terraform_version']} / {summary['aws_provider']} — STOP"
    v = json.loads(call("validate", cmd + ["validate", "-json"], roleenv).stdout)
    assert v["valid"]
    sl = call("state-list", cmd + ["state", "list"], roleenv).stdout.decode().splitlines()
    managed = [x for x in sl if x.strip() and not x.startswith("data.")]
    summary["state_list_count"] = {"managed": len(managed), "data": len(sl) - len(managed)}
    summary["checks"]["state_managed_count_8"] = len(managed) == EXPECTED_STATE_COUNT

    summary["plan_started_kst"] = kst()
    pl = call("plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode", "-no-color",
                             "-var-file=" + str(VF), "-out=" + str(P / f"vpn-replan-{STAMP}.tfplan")],
              roleenv, allowed=(0, 2), timeout=300)
    summary["plan_finished_kst"] = kst()
    summary["plan_rc"] = pl.returncode
    summary["plan_line"] = next((ln for ln in pl.stdout.decode(errors="replace").splitlines()
                                 if ln.startswith(("No changes.", "Plan:"))), None)
    show = call("show-json", cmd + ["show", "-json", str(P / f"vpn-replan-{STAMP}.tfplan")], roleenv, stdout_dir=P)
    plan = json.loads(show.stdout)
    summary["plan_sha256"] = hashlib.sha256((P / f"vpn-replan-{STAMP}.tfplan").read_bytes()).hexdigest()
    summary["plan_json_sha256"] = hashlib.sha256(show.stdout).hexdigest()
    changed = [{"address": rc["address"], "actions": rc["change"]["actions"]}
               for rc in plan.get("resource_changes", []) if rc["change"]["actions"] != ["no-op"]]
    out_changed = [k for k, oc in (plan.get("output_changes") or {}).items() if oc.get("actions") != ["no-op"]]
    drift = [{"address": d["address"], "actions": d["change"]["actions"]} for d in plan.get("resource_drift", [])]
    summary.update(changed_resources=changed, changed_outputs=out_changed, resource_drift=drift)
    if drift:
        summary["warnings"].append(f"Terraform 밖 변경 감지 {len(drift)}건 — 계획 변경과 별개로 기록")
    if pl.returncode == 0 and not changed and not out_changed:
        summary["status"] = "NO_CHANGES_PASS"
    else:
        summary["status"] = "CHANGES_STOP"
        print("STOP 변경이 있습니다. Apply하지 말고 RESULT를 그대로 보고하세요.", flush=True)
except Exception as exc:
    summary.update(status="STOP", error=str(exc))
    print("STOP", exc, flush=True)
finally:
    if roleenv:
        try:
            summary["after_keys"] = listing("after-keys", roleenv)
            summary["checks"]["lock_absent_after"] = LOCK_KEY not in summary["after_keys"]
            if summary.get("state_before"):
                summary["state_after"] = state_head("state-head-after", roleenv)
                summary["checks"]["state_version_unchanged"] = (
                    summary["state_after"]["VersionId"] == summary["state_before"]["VersionId"]
                    and summary["state_after"]["ETag"] == summary["state_before"]["ETag"])
        except Exception as exc:
            summary["after_check_error"] = str(exc)
    roleenv = None
    failed = [k for k, v in summary["checks"].items() if v is not True]
    summary["checks_failed"] = failed
    if summary["status"] == "NO_CHANGES_PASS" and failed:
        summary["status"] = "NO_CHANGES_BUT_CHECK_FAILED"
    summary.update(finished_utc=now(), finished_kst=kst(), records=records, credentials_saved=False, state_body_saved=False,
                   plan_file_and_json_in_evidence=False)
    if E.exists():
        save("execution-summary.json", json.dumps(summary, indent=2, ensure_ascii=False).encode())
        files = sorted(f for f in E.iterdir() if f.is_file() and f.name != "SHA256SUMS")
        save("SHA256SUMS", "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n" for f in files).encode())
        tgz = P / f"{E.name}.tar.gz"
        with tarfile.open(tgz, "w:gz") as t:
            t.add(E, arcname=E.name)
        summary["evidence_tgz"] = str(tgz)
        summary["evidence_tgz_sha256"] = hashlib.sha256(tgz.read_bytes()).hexdigest()
        summary["evidence_tgz_bytes"] = tgz.stat().st_size
    print()
    print("RESULT", json.dumps({k: summary.get(k) for k in (
        "status", "error", "warnings", "role_arn", "account_guard", "terraform_version", "aws_provider",
        "state_list_count", "plan_rc", "plan_line", "plan_sha256", "plan_json_sha256",
        "changed_resources", "changed_outputs", "resource_drift", "state_before", "state_after",
        "checks", "checks_failed", "before_keys", "after_keys", "plan_started_kst", "plan_finished_kst",
        "started_kst", "finished_kst", "evidence_tgz", "evidence_tgz_sha256", "evidence_tgz_bytes")},
        ensure_ascii=False, indent=2), flush=True)
    sys.exit(0 if summary["status"] == "NO_CHANGES_PASS" else 1)
