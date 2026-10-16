#!/usr/bin/env python3
"""#11 network subnet ROSA LB 역할 태그 2건 — 승인 saved Plan 1회 Apply + readback + 검증용 Plan.

비용: 없음(태그만). 권욱 GO 6144035652 범위, 작업 구간 확인 후에만 실행.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, ~/iac11-tagplan-20261013-101518 안에서.
보안: MFA 코드·임시 자격증명은 메모리에서만. state 원문은 메모리에서 lineage/serial만 읽고 저장하지 않는다.
재실행 금지: Apply 단계에 들어간 뒤 실패하면 다시 돌리지 말고 RESULT를 그대로 보고(실제 태그·state 먼저 확인).
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
PLAN_NAME = "tagplan-20261013-191626.tfplan"
PLAN_SHA256 = "9d65852fa85ce28a1f11dba353e41ecc415b4855d92474efa334d5fb24328a81"
STATE_BEFORE = {"VersionId": "m4zM3let2zBojqhe0Jj_h.qGyCflfMe2", "ETag": '"60e4aef535b9c5863ed5767ebce78a3f"'}
LINEAGE = "64258b91-83ed-bf3d-89fc-1d11eac31351"
SERIAL_BEFORE = 2
TF_VERSION, AWS_PROVIDER = "1.16.4", "6.66.0"
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "e79a35f5b54ac3cd68e1c32964929c6113a2ab7bfc749c7663358c950e9f481d",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/tests/network.tftest.hcl": "ead2188c20e921eb6debef38bc77205f7fdd4e06c1d466dabf9292b054dc6139",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
}
VPC = "vpc-039718404350154d9"
SUBNETS = {  # key: (id, 추가될 역할 태그 또는 None)
    "private_a": ("subnet-044ced60c3c705ac6", ("kubernetes.io/role/internal-elb", "1")),
    "private_b": ("subnet-0fc798d49bb79b248", None),
    "private_c": ("subnet-07586708a37f05d71", None),
    "public_transport_a": ("subnet-0fbc846bde668f0f3", ("kubernetes.io/role/elb", "1")),
}
BASE_TAGS = {"Project": "fds-hybrid", "ManagedBy": "terraform", "Phase": "phase2", "Component": "network"}
ROUTES = {"rtb-01e3140bb2a0b3bb6": "nat-0f0fa5d5de405fa71", "rtb-061f0b2ff25634304": "nat-0f0fa5d5de405fa71",
          "rtb-0be823c978f9da092": "nat-0f0fa5d5de405fa71", "rtb-0dd7491d1a3944217": "igw-003f907eafcc6bfb9"}
RELAY = "i-05e4b63d31d8d5ac5"
RELAY_SG = "sg-0f1e8a5dbecabccee"

P = Path.cwd()
S = P / "source"
TF = P / "bin" / "terraform"
PLAN = P / PLAN_NAME
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d-%H%M%S")
E = P / f"evidence-tagapply-{STAMP}"
os.umask(0o077)
records = []
base = {k: v for k, v in os.environ.items() if k != "TF_DATA_DIR"}  # 셸의 TF_DATA_DIR은 쓰지 않음(어제 STOP 원인)
roleenv = None
summary = {"executor": ME, "plan_sha256": PLAN_SHA256, "apply": "NOT_STARTED", "status": "STARTED",
           "prechecks": {}, "checks": {}, "observed": {}, "shell_TF_DATA_DIR_present": "TF_DATA_DIR" in os.environ}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def save(name, data):
    (E / name).write_bytes(data)


def call(name, args, env=None, allowed=(0,), timeout=60, keep_stdout=True):
    t = now()
    print("RUN", name, flush=True)
    try:
        r = subprocess.run(args, env=env or base, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        records.append({"name": name, "argv": args, "started_utc": t, "finished_utc": now(), "rc": None, "result": "TIMEOUT"})
        raise RuntimeError(name + " timeout — 재실행 금지, 실제 태그·state·lock 먼저 확인")
    if keep_stdout:
        save(name + ".stdout", r.stdout)
    save(name + ".stderr", r.stderr)
    records.append({"name": name, "argv": args, "started_utc": t, "finished_utc": now(), "rc": r.returncode,
                    "stdout_saved": keep_stdout, "stdout_sha256": hashlib.sha256(r.stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(r.stderr).hexdigest()})
    print("RC", name, r.returncode, flush=True)
    if r.returncode not in allowed:
        raise RuntimeError(f"{name} rc={r.returncode}")
    return r


def aws_args(args):
    return ["aws", *args, "--region", REGION, "--output", "json", "--no-cli-pager",
            "--cli-connect-timeout", "10", "--cli-read-timeout", "20"]


def aws(name, args, env=None):
    return json.loads(call(name, aws_args(args), env, (0,), 45).stdout or b"{}")


def listing(name, env):
    d = aws(name, ["s3api", "list-objects-v2", "--bucket", BUCKET, "--prefix", STATE_KEY, "--max-keys", "10", "--no-paginate"], env)
    assert not d.get("IsTruncated")
    return sorted(o["Key"] for o in d.get("Contents", []))


def state_meta(tag, env, cmd):
    h = aws(f"state-head-{tag}", ["s3api", "head-object", "--bucket", BUCKET, "--key", STATE_KEY], env)
    pull = call(f"state-pull-{tag}", cmd + ["state", "pull"], env, keep_stdout=False)  # 원문 저장 안 함
    st = json.loads(pull.stdout)
    pull = None
    return {"VersionId": h.get("VersionId"), "ETag": h.get("ETag"), "lineage": st.get("lineage"), "serial": st.get("serial"),
            "terraform_version": st.get("terraform_version")}


def read_targets(tag):
    """실제 AWS: 4 subnet 태그·CIDR·공인IP 설정, RT 경로, Relay SG 규칙, Relay 상태 (본인 사용자 읽기 권한)."""
    sn = {s["SubnetId"]: s for s in aws(f"rb-subnets-{tag}", ["ec2", "describe-subnets", "--filters", f"Name=vpc-id,Values={VPC}"])["Subnets"]}
    subnets = {}
    for k, (sid, _) in SUBNETS.items():
        s = sn[sid]
        subnets[k] = {"tags": {t["Key"]: t["Value"] for t in s.get("Tags", [])}, "cidr": s["CidrBlock"],
                      "map_public_ip": s["MapPublicIpOnLaunch"], "az_id": s["AvailabilityZoneId"]}
    rts = aws(f"rb-rts-{tag}", ["ec2", "describe-route-tables", "--filters", f"Name=vpc-id,Values={VPC}"])["RouteTables"]
    routes = {t["RouteTableId"]: sorted((r.get("DestinationCidrBlock"), r.get("NatGatewayId") or r.get("GatewayId"))
                                        for r in t.get("Routes", [])) for t in rts}
    rules = aws(f"rb-sg-{tag}", ["ec2", "describe-security-group-rules", "--filters", f"Name=group-id,Values={RELAY_SG}"])["SecurityGroupRules"]
    sg = sorted((x["IsEgress"], x["IpProtocol"], x["FromPort"], x["ToPort"], x.get("CidrIpv4")) for x in rules)
    inst = aws(f"rb-relay-{tag}", ["ec2", "describe-instances", "--instance-ids", RELAY])["Reservations"][0]["Instances"][0]
    return {"subnets": subnets, "routes": routes, "relay_sg": sg, "relay_state": inst["State"]["Name"]}


try:
    E.mkdir(exist_ok=False)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("iac11_network_tagapply.py", Path(__file__).read_bytes())
    assert PLAN.exists() and TF.exists() and S.exists(), "~/iac11-tagplan-20261013-101518 안에서 실행하세요"
    assert hashlib.sha256(PLAN.read_bytes()).hexdigest() == PLAN_SHA256, "saved Plan 해시 불일치 — STOP"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    assert not (Path.home() / ".terraformrc").exists(), "~/.terraformrc exists"

    me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요"
    role = aws("pre-trust", ["iam", "get-role", "--role-name", ROLE_NAME])["Role"]
    doc = role["AssumeRolePolicyDocument"]
    doc = json.loads(doc) if isinstance(doc, str) else doc
    stmts = doc["Statement"] if isinstance(doc["Statement"], list) else [doc["Statement"]]
    allows = [s for s in stmts if s.get("Effect") == "Allow"]
    assert allows and role["RoleId"] == ROLE_ID and all(
        s.get("Condition", {}).get("Bool", {}).get("aws:MultiFactorAuthPresent") in ("true", True) for s in allows), "trust 변경 — STOP"
    summary["prechecks"]["trust_mfa_roleid"] = True
    for u in ("321team-gwonuk", "321team-hayeoung", "321team-jaehwan"):
        assert len(aws("pre-access-keys-" + u, ["iam", "list-access-keys", "--user-name", u])["AccessKeyMetadata"]) == 0, f"{u} Access Key — STOP"
    summary["prechecks"]["access_keys_0"] = True
    assert aws("pre-versioning", ["s3api", "get-bucket-versioning", "--bucket", BUCKET]).get("Status") == "Enabled", "versioning — STOP"
    summary["prechecks"]["versioning_enabled"] = True

    # 실제 대상이 Plan 당시와 같은지 (역할 태그 아직 없음, 기존 태그·route·SG 그대로)
    before = read_targets("before")
    summary["observed"]["before"] = before
    for k, (sid, add) in SUBNETS.items():
        tg = before["subnets"][k]["tags"]
        assert all(tg.get(a) == b for a, b in BASE_TAGS.items()) and tg.get("Name") == f"fds-{k}", f"{k} 기존 태그 다름 — STOP"
        assert not any(x.startswith("kubernetes.io/") for x in tg), f"{k}에 kubernetes.io 태그가 이미 있음 — STOP(새 Plan 재검토)"
    for rt, tgt in ROUTES.items():
        assert before["routes"][rt] == sorted([("10.20.0.0/16", "local"), ("0.0.0.0/0", tgt)]), f"{rt} route 다름 — STOP"
    summary["prechecks"]["targets_same_as_plan"] = True

    serial = subprocess.run(aws_args(["iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"]),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
    code = getpass.getpass("MFA 6자리 (화면에 안 보임): ").strip()
    t = now()
    r = subprocess.run(aws_args(["sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                                 "--serial-number", serial, "--token-code", code, "--duration-seconds", "1800"]),
                       capture_output=True, timeout=45)
    code = None
    if r.returncode != 0:
        save("assume-role.stderr", r.stderr)
        raise RuntimeError(f"assume-role rc={r.returncode}")
    obj = json.loads(r.stdout)
    c = obj.pop("Credentials")
    obj["Credentials"] = {"redacted": True, "Expiration": c["Expiration"]}
    save("assume-role.stdout", json.dumps(obj, indent=2).encode())
    records.append({"name": "assume-role", "started_utc": t, "finished_utc": now(), "rc": 0, "note": "Credentials removed in memory"})
    roleenv = dict(base)
    roleenv.update(AWS_ACCESS_KEY_ID=c["AccessKeyId"], AWS_SECRET_ACCESS_KEY=c["SecretAccessKey"],
                   AWS_SESSION_TOKEN=c["SessionToken"], AWS_MAX_ATTEMPTS="1", TF_IN_AUTOMATION="1",
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac11-tagapply-tfdata-", dir="/tmp"))
    c = r = None
    ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}" and ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    keys = listing("before-keys", roleenv)
    assert keys == [STATE_KEY], f"state/lock 상태 다름 {keys} — STOP"
    cmd = [str(TF), "-chdir=" + str(S / "terraform/network")]
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"
    bk = json.loads((Path(roleenv["TF_DATA_DIR"]) / "terraform.tfstate").read_text())["backend"]
    bc = bk.get("config") or {}
    summary["backend_after_init"] = {"type": bk.get("type"), **{k: bc.get(k) for k in
                                     ("bucket", "key", "region", "encrypt", "use_lockfile", "allowed_account_ids")}}
    assert bk.get("type") == "s3" and bc.get("bucket") == BUCKET and bc.get("key") == STATE_KEY and bc.get("region") == REGION \
        and bc.get("encrypt") is True and bc.get("use_lockfile") is True and bc.get("allowed_account_ids") == [ACCOUNT], \
        f"init 후 backend 설정 불일치 {summary['backend_after_init']} — STOP"
    summary["prechecks"]["backend_matches"] = True
    tv = json.loads(call("terraform-version", cmd + ["version", "-json"], roleenv).stdout)
    assert tv.get("terraform_version") == TF_VERSION and (tv.get("provider_selections") or {}).get(
        "registry.terraform.io/hashicorp/aws") == AWS_PROVIDER, "버전 불일치 — STOP"
    sb = state_meta("before", roleenv, cmd)
    summary["state_before"] = sb
    assert sb["VersionId"] == STATE_BEFORE["VersionId"] and sb["ETag"] == STATE_BEFORE["ETag"], "state 버전 바뀜 — STOP, 새 Plan 재검토"
    assert sb["lineage"] == LINEAGE and sb["serial"] == SERIAL_BEFORE, "lineage/serial 다름 — STOP"
    summary["prechecks"]["state_same_as_plan"] = True

    print("APPLY 시작 — 태그 2건. 창을 닫거나 다시 실행하지 마세요.", flush=True)
    summary["apply"] = "STARTED"
    summary["apply_started_kst"] = kst()
    ap = call("apply", cmd + ["apply", "-input=false", "-lock-timeout=60s", "-no-color", str(PLAN)], roleenv, allowed=(0, 1), timeout=600)
    summary["apply_finished_kst"] = kst()
    summary["apply_rc"] = ap.returncode
    summary["apply_line"] = next((ln for ln in ap.stdout.decode(errors="replace").splitlines() if "Apply complete!" in ln), None)
    if ap.returncode != 0:
        summary["apply"] = "FAILED"
        raise RuntimeError("apply rc=1 — 재Apply 금지, 실제 태그·state 먼저 확인")
    summary["apply"] = "COMPLETE"
    assert summary["apply_line"] and "0 added, 2 changed, 0 destroyed" in summary["apply_line"], "Apply 결과 수 불일치"

    after = read_targets("after")
    summary["observed"]["after"] = after
    ck = summary["checks"]
    for k, (sid, add) in SUBNETS.items():
        want = dict(before["subnets"][k]["tags"], **({add[0]: add[1]} if add else {}))
        ck[f"tags_{k}"] = after["subnets"][k]["tags"] == want
        ck[f"attrs_{k}"] = {x: after["subnets"][k][x] for x in ("cidr", "map_public_ip", "az_id")} == \
                           {x: before["subnets"][k][x] for x in ("cidr", "map_public_ip", "az_id")}
    ck["routes_unchanged"] = after["routes"] == before["routes"]
    ck["no_onprem_route"] = not any(d == "10.1.93.0/24" for rs in after["routes"].values() for d, _ in rs)
    ck["relay_sg_unchanged"] = after["relay_sg"] == before["relay_sg"]
    ck["relay_running"] = after["relay_state"] == "running"
    sa = state_meta("after", roleenv, cmd)
    summary["state_after"] = sa
    ck["state_lineage_same_serial_up"] = sa["lineage"] == LINEAGE and sa["serial"] > SERIAL_BEFORE
    vp = call("verify-plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode", "-no-color",
                                    "-var=execution_enabled=true"], roleenv, allowed=(0, 2), timeout=300)
    summary["verify_plan_rc"] = vp.returncode
    summary["verify_plan_line"] = next((ln for ln in vp.stdout.decode(errors="replace").splitlines()
                                        if ln.startswith(("No changes.", "Plan:"))), None)
    ck["verify_plan_no_changes"] = vp.returncode == 0
    failed = [k for k, v in ck.items() if v is not True]
    summary["readback_failed"] = failed
    summary["status"] = "TAG_APPLY_AND_READBACK_PASS" if not failed else "APPLY_DONE_READBACK_MISMATCH"
except Exception as exc:
    if summary["status"] == "STARTED":
        summary["status"] = "STOP"
    summary["error"] = str(exc)
    print("STOP", exc, flush=True)
finally:
    if roleenv:
        try:
            summary["after_keys"] = listing("after-keys", roleenv)
            summary["lock_absent_after"] = LOCK_KEY not in summary["after_keys"]
        except Exception as exc:
            summary["after_check_error"] = str(exc)
    roleenv = None
    if summary["status"] == "TAG_APPLY_AND_READBACK_PASS" and (summary.get("after_check_error") or not summary.get("lock_absent_after")):
        summary["status"] = "POSTCHECK_FAILED"
    summary.update(finished_utc=now(), finished_kst=kst(), records=records, credentials_saved=False, state_body_saved=False)
    if E.exists():
        save("execution-summary.json", json.dumps(summary, indent=2, ensure_ascii=False).encode())
        files = sorted(f for f in E.iterdir() if f.is_file() and f.name != "SHA256SUMS")
        save("SHA256SUMS", "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n" for f in files).encode())
        tgz = P / f"{E.name}.tar.gz"
        with tarfile.open(tgz, "w:gz") as t:
            t.add(E, arcname=E.name)
        summary["evidence_tgz_sha256"] = hashlib.sha256(tgz.read_bytes()).hexdigest()
    print()
    print("RESULT", json.dumps({k: summary.get(k) for k in (
        "status", "error", "role_arn", "apply", "apply_rc", "apply_line", "apply_started_kst", "apply_finished_kst",
        "prechecks", "state_before", "state_after", "readback_failed", "checks", "verify_plan_rc", "verify_plan_line",
        "backend_after_init", "after_keys", "lock_absent_after", "shell_TF_DATA_DIR_present", "started_kst", "finished_kst", "evidence_tgz_sha256")},
        ensure_ascii=False, indent=2), flush=True)
    sys.exit(0 if summary["status"] == "TAG_APPLY_AND_READBACK_PASS" else 1)
