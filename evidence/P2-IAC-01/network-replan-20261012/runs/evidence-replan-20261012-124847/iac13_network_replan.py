#!/usr/bin/env python3
"""#13 G4 입력 2 — network 재실행 무변경(AC-5) 확인. Plan만, Apply 없음.

비용: 없음. 조회와 Plan만 한다. state는 쓰지 않고 native lock(.tflock)만 잠깐 생겼다 지워진다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, #11 network WORKDIR 안에서 실행.
같은 source: #11 Apply에 쓴 source/ 6파일(81162467)과 bin/terraform 1.16.4를 그대로 쓴다.
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
STATE_KEY = "phase2/network/terraform.tfstate"
LOCK_KEY = STATE_KEY + ".tflock"
SOURCE_MAIN = "81162467bb2f99a099cb7067fbc3f63e1c0dbed8"
APPLIED_PLAN_SHA256 = "e5e775ceb4dcec64b050eaeab0f84d3f6bd0f5765554cdfc61d9f213898383b8"
TF_VERSION = "1.16.4"
AWS_PROVIDER = "6.66.0"
EXPECTED_STATE_COUNT = 20
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "ae904de11034f1f847757c3bf1e2131cc8d4d1666a5676f5b2fdac89c6b987f0",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
    "terraform/network/tests/network.tftest.hcl": "490d2e5a9f03db2f712a94c2f46618c318b8b83071dfc80fa2df3a56ef3b8735",
}

P = Path.cwd()
S = P / "source"
TF = P / "bin" / "terraform"
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d-%H%M%S")
E = P / f"evidence-replan-{STAMP}"
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
    save("iac13_network_replan.py", Path(__file__).read_bytes())
    assert TF.exists() and S.exists(), "#11 network WORKDIR에서 실행하세요 (source/, bin/terraform 필요)"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    summary["checks"]["source_6_files_match_81162467"] = True
    if (P / "network.tfplan").exists():
        summary["applied_plan_file_sha256_recheck"] = hashlib.sha256((P / "network.tfplan").read_bytes()).hexdigest()
    assert not (S / "terraform/network/terraform.tfvars").exists()
    assert not list((S / "terraform/network").glob("*.auto.tfvars*"))
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    assert not (Path.home() / ".terraformrc").exists(), "~/.terraformrc exists"
    summary["terraform_binary_sha256"] = hashlib.sha256(TF.read_bytes()).hexdigest()

    me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요 (root/타인 금지)"
    summary["account_guard"] = me["Account"] == ACCOUNT
    assert summary["account_guard"], "계정 불일치 — STOP"
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
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac13-replan-tfdata-", dir="/tmp"))
    c = r = None

    ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    # state 무결성 (AC-4 일부): key 있음, lock 없음, versioning, 현재 버전 기록
    summary["before_keys"] = listing("before-keys", roleenv)
    assert STATE_KEY in summary["before_keys"], "network state가 없음 — STOP"
    assert LOCK_KEY not in summary["before_keys"], "lock이 남아 있음(다른 writer?) — STOP, 권욱 님과 확인"
    ver = aws("pre-versioning", ["s3api", "get-bucket-versioning", "--bucket", BUCKET], roleenv)
    summary["checks"]["bucket_versioning_enabled"] = ver.get("Status") == "Enabled"
    summary["state_before"] = state_head("state-head-before", roleenv)

    cmd = [str(TF), "-chdir=" + str(S / "terraform/network")]
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
    summary["checks"]["state_managed_count_20"] = len(managed) == EXPECTED_STATE_COUNT

    summary["plan_started_kst"] = kst()
    pl = call("plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode", "-no-color",
                             "-var=execution_enabled=true", "-out=" + str(P / f"replan-{STAMP}.tfplan")],
              roleenv, allowed=(0, 2), timeout=300)
    summary["plan_finished_kst"] = kst()
    summary["plan_rc"] = pl.returncode
    summary["plan_line"] = next((ln for ln in pl.stdout.decode(errors="replace").splitlines()
                                 if ln.startswith(("No changes.", "Plan:"))), None)
    show = call("show-json", cmd + ["show", "-json", str(P / f"replan-{STAMP}.tfplan")], roleenv, stdout_dir=P)
    plan = json.loads(show.stdout)
    summary["plan_sha256"] = hashlib.sha256((P / f"replan-{STAMP}.tfplan").read_bytes()).hexdigest()
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
