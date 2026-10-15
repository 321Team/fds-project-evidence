#!/usr/bin/env python3
"""#11 network Apply 5~6단계 — 확인받은 Plan 파일 그대로 Apply + readback.

💰 비용 발생: NAT Gateway·NAT EIP가 생성 시점부터 과금된다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, 1~3단계 WORKDIR 안에서 실행.
보안: MFA 코드와 임시 자격증명은 메모리에서만 쓰고 파일에 쓰지 않는다.
재실행 금지: 실패·중단 시 다시 돌리지 말고 RESULT를 그대로 보고(복구 절차 v2).
"""
import datetime, getpass, hashlib, json, os, subprocess, sys, tempfile
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
PLAN_SHA256 = "e5e775ceb4dcec64b050eaeab0f84d3f6bd0f5765554cdfc61d9f213898383b8"
TF_SHA_SOURCE = "terraform 1.16.4 (1~3단계에서 zip SHA256 검증 후 설치한 bin/terraform)"
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "ae904de11034f1f847757c3bf1e2131cc8d4d1666a5676f5b2fdac89c6b987f0",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
    "terraform/network/tests/network.tftest.hcl": "490d2e5a9f03db2f712a94c2f46618c318b8b83071dfc80fa2df3a56ef3b8735",
}
EXPECTED_SUBNETS = {  # key: (cidr, zone_id, az name)
    "private_a": ("10.20.10.0/24", "apne2-az1", "ap-northeast-2a"),
    "private_b": ("10.20.20.0/24", "apne2-az2", "ap-northeast-2b"),
    "private_c": ("10.20.30.0/24", "apne2-az3", "ap-northeast-2c"),
    "public_transport_a": ("10.20.110.0/24", "apne2-az1", "ap-northeast-2a"),
}
TAG_FILTER = ["Name=tag:Project,Values=fds-hybrid"]

P = Path.cwd()
S = P / "source"
E = P / "evidence-apply"
TF = P / "bin" / "terraform"
os.umask(0o077)
records = []
base = dict(os.environ)
roleenv = None
summary = {"executor": ME, "plan_sha256": PLAN_SHA256, "apply": "NOT_STARTED", "status": "STARTED", "checks": {}, "prechecks": {}}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def save(name, data):
    (E / name).write_bytes(data)


def call(name, args, env=None, allowed=(0,), timeout=60, shown=None):
    t = now()
    print("RUN", name, flush=True)
    try:
        r = subprocess.run(args, env=env or base, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        records.append({"name": name, "argv": shown or args, "started_utc": t, "finished_utc": now(), "rc": None, "result": "TIMEOUT"})
        raise RuntimeError(name + " timeout — 재실행 금지, 복구 절차 v2")
    save(name + ".stdout", r.stdout)
    save(name + ".stderr", r.stderr)
    records.append({"name": name, "argv": shown or args, "started_utc": t, "finished_utc": now(), "rc": r.returncode,
                    "stdout_sha256": hashlib.sha256(r.stdout).hexdigest(), "stderr_sha256": hashlib.sha256(r.stderr).hexdigest()})
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
    return [o["Key"] for o in d.get("Contents", [])]


def readback(env, handoff):
    ck = summary["checks"]
    vpc_id = handoff["vpc_id"]
    vpc = aws("rb-vpc", ["ec2", "describe-vpcs", "--vpc-ids", vpc_id], env)["Vpcs"][0]
    ck["vpc_cidr"] = vpc["CidrBlock"] == "10.20.0.0/16"
    for attr, key in (("enableDnsSupport", "EnableDnsSupport"), ("enableDnsHostnames", "EnableDnsHostnames")):
        a = aws("rb-vpc-" + attr, ["ec2", "describe-vpc-attribute", "--vpc-id", vpc_id, "--attribute", attr], env)
        ck["vpc_" + attr] = a[key]["Value"] is True
    subnets = {s["SubnetId"]: s for s in aws("rb-subnets", ["ec2", "describe-subnets", "--filters", f"Name=vpc-id,Values={vpc_id}"], env)["Subnets"]}
    ck["subnet_count_4"] = len(subnets) == 4
    for key, (cidr, zid, az) in EXPECTED_SUBNETS.items():
        h = handoff["subnets"][key]
        s = subnets.get(h["id"], {})
        ck[f"subnet_{key}"] = (s.get("CidrBlock") == cidr and s.get("AvailabilityZoneId") == zid
                               and s.get("AvailabilityZone") == az and s.get("MapPublicIpOnLaunch") is False)
    igw = aws("rb-igw", ["ec2", "describe-internet-gateways", "--internet-gateway-ids", handoff["igw_id"]], env)["InternetGateways"][0]
    ck["igw_attached"] = any(a["VpcId"] == vpc_id and a["State"] == "available" for a in igw.get("Attachments", []))
    nat = aws("rb-nat", ["ec2", "describe-nat-gateways", "--nat-gateway-ids", handoff["nat_id"]], env)["NatGateways"][0]
    ck["nat_available"] = nat["State"] == "available"
    ck["nat_in_transport"] = nat["SubnetId"] == handoff["subnets"]["public_transport_a"]["id"]
    nat_eip = nat["NatGatewayAddresses"][0].get("AllocationId")
    eips = aws("rb-eips", ["ec2", "describe-addresses", "--filters", *TAG_FILTER], env)["Addresses"]
    ck["eip_1_on_nat"] = len(eips) == 1 and eips[0].get("AllocationId") == nat_eip
    rts = {r["RouteTableId"]: r for r in aws("rb-rts", ["ec2", "describe-route-tables", "--filters", f"Name=vpc-id,Values={vpc_id}"], env)["RouteTables"]}
    for key in EXPECTED_SUBNETS:
        h = handoff["subnets"][key]
        rt = rts.get(h["route_table_id"], {})
        assoc = [a for a in rt.get("Associations", []) if a.get("SubnetId") == h["id"]]
        default = [r for r in rt.get("Routes", []) if r.get("DestinationCidrBlock") == "0.0.0.0/0"]
        target = default[0].get("GatewayId") if key == "public_transport_a" and default else (default[0].get("NatGatewayId") if default else None)
        want = handoff["igw_id"] if key == "public_transport_a" else handoff["nat_id"]
        ck[f"route_{key}"] = len(assoc) == 1 and len(default) == 1 and target == want and default[0].get("State") == "active"
        ck[f"no_onprem_route_{key}"] = not any(r.get("DestinationCidrBlock") == "10.1.93.0/24" for r in rt.get("Routes", []))
    summary["handoff"] = handoff
    summary["nat_public_ip"] = nat["NatGatewayAddresses"][0].get("PublicIp")
    failed = [k for k, v in ck.items() if v is not True]
    summary["readback_failed"] = failed
    return not failed


try:
    E.mkdir(exist_ok=False)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("iac11_network_apply.py", Path(__file__).read_bytes())
    assert (P / "network.tfplan").exists() and TF.exists() and S.exists(), "1~3단계 WORKDIR에서 실행하세요"
    got = hashlib.sha256((P / "network.tfplan").read_bytes()).hexdigest()
    assert got == PLAN_SHA256, f"Plan 파일 해시 불일치 {got} — STOP"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    call("terraform-version", [str(TF), "version", "-json"])

    me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요"
    # 직전 필수 조회 재확인 (조회 거부는 0/부재로 쓰지 않고 STOP)
    role = aws("pre-trust", ["iam", "get-role", "--role-name", ROLE_NAME])["Role"]
    doc = role["AssumeRolePolicyDocument"]
    doc = json.loads(doc) if isinstance(doc, str) else doc
    stmts = doc["Statement"] if isinstance(doc["Statement"], list) else [doc["Statement"]]
    allows = [s for s in stmts if s.get("Effect") == "Allow"]
    assert allows and role["RoleId"] == ROLE_ID, "trust/RoleId 변경 — STOP"
    for s in allows:
        assert s.get("Condition", {}).get("Bool", {}).get("aws:MultiFactorAuthPresent") in ("true", True), "trust MFA 조건 없음 — STOP"
    summary["prechecks"]["pre_trust_mfa"] = True
    for u in ("321team-gwonuk", "321team-hayeoung", "321team-jaehwan"):
        n = len(aws("pre-access-keys-" + u, ["iam", "list-access-keys", "--user-name", u])["AccessKeyMetadata"])
        assert n == 0, f"{u} Access Key {n}개 — STOP"
    summary["prechecks"]["pre_access_keys_0"] = True
    q = int(aws("pre-eip-quota", ["service-quotas", "get-service-quota", "--service-code", "ec2", "--quota-code", "L-0263D0A3"])["Quota"]["Value"])
    used = len(aws("pre-eips", ["ec2", "describe-addresses"])["Addresses"])
    assert used + 1 <= q, f"EIP quota 부족 {used}/{q} — STOP"
    summary["prechecks"]["pre_eip_quota"] = f"{used}/{q}"
    ver = aws("pre-versioning", ["s3api", "get-bucket-versioning", "--bucket", BUCKET])
    assert ver.get("Status") == "Enabled", f"state bucket versioning {ver.get('Status')} — STOP"
    summary["prechecks"]["pre_versioning_enabled"] = True
    serial = subprocess.run(aws_args(["iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"]),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
    code = getpass.getpass("MFA 6자리 (화면에 안 보임): ").strip()
    t = now()
    r = subprocess.run(aws_args(["sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                                 "--serial-number", serial, "--token-code", code, "--duration-seconds", "3600"]),
                       capture_output=True, timeout=45)
    code = None
    shown = aws_args(["sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                      "--serial-number", serial, "--token-code", "REDACTED", "--duration-seconds", "3600"])
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
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac11-apply-tfdata-", dir="/tmp"))
    summary["session_expiration"] = c["Expiration"]
    c = r = None

    ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    summary["before_keys"] = listing("before-keys", roleenv)
    assert summary["before_keys"] == [], "state 또는 lock이 이미 있음 — STOP"
    vpcs = aws("pre-tag-vpcs", ["ec2", "describe-vpcs", "--filters", *TAG_FILTER], roleenv)["Vpcs"]
    nats = aws("pre-tag-nats", ["ec2", "describe-nat-gateways", "--filter", *TAG_FILTER,
                                "Name=state,Values=pending,available,failed,deleting"], roleenv)["NatGateways"]
    assert not vpcs and not nats, "프로젝트 태그 자원이 이미 있음 — STOP"

    cmd = [str(TF), "-chdir=" + str(S / "terraform/network")]
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"

    print("💰 APPLY 시작 — NAT 생성에 수 분 걸립니다. 창을 닫거나 다시 실행하지 마세요.", flush=True)
    summary["apply"] = "STARTED"
    summary["apply_started_kst"] = kst()
    ap = call("apply", cmd + ["apply", "-input=false", "-lock-timeout=60s", "-no-color", str(P / "network.tfplan")],
              roleenv, allowed=(0, 1), timeout=1800)
    summary["apply_finished_kst"] = kst()
    summary["apply_rc"] = ap.returncode
    tail = [ln for ln in ap.stdout.decode(errors="replace").splitlines() if "Apply complete!" in ln]
    summary["apply_line"] = tail[-1] if tail else None
    if ap.returncode != 0:
        summary["apply"] = "FAILED"
        raise RuntimeError("apply rc=1 — 재실행 금지, 복구 절차 v2 (evidence-apply/apply.stderr)")
    summary["apply"] = "COMPLETE"
    assert summary["apply_line"] and "20 added, 0 changed, 0 destroyed" in summary["apply_line"], "Apply 결과 수 불일치"

    out = json.loads(call("output", cmd + ["output", "-json", "network_handoff"], roleenv).stdout)
    call("state-list", cmd + ["state", "list"], roleenv)
    ok = readback(roleenv, out)
    summary["status"] = "APPLY_AND_READBACK_PASS" if ok else "APPLY_DONE_READBACK_MISMATCH"
except Exception as exc:
    if summary["status"] == "STARTED":
        summary["status"] = "STOP"
    summary["error"] = str(exc)
    print("STOP", exc, flush=True)
finally:
    if roleenv:
        try:
            summary["after_keys"] = listing("after-keys", roleenv)
            summary["lock_current_absent"] = LOCK_KEY not in summary["after_keys"]
            summary["state_created"] = STATE_KEY in summary["after_keys"]
        except Exception as exc:
            summary["after_check_error"] = str(exc)
    roleenv = None
    summary.update(finished_utc=now(), finished_kst=kst(), records=records, credentials_saved=False)
    if E.exists():
        save("execution-summary.json", json.dumps(summary, indent=2, ensure_ascii=False).encode())
        files = sorted(f for f in E.iterdir() if f.is_file() and f.name != "SHA256SUMS")
        save("SHA256SUMS", "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n" for f in files).encode())
    print()
    print("RESULT", json.dumps({k: summary.get(k) for k in (
        "status", "error", "role_arn", "apply", "apply_rc", "apply_line", "apply_started_kst", "apply_finished_kst",
        "prechecks", "readback_failed", "checks", "handoff", "nat_public_ip", "before_keys", "after_keys",
        "lock_current_absent", "state_created", "started_kst", "finished_kst")}, ensure_ascii=False, indent=2), flush=True)
    print("EVIDENCE_DIR", E, flush=True)
    sys.exit(0 if summary["status"] == "APPLY_AND_READBACK_PASS" else 1)
