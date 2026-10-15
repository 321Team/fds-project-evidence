#!/usr/bin/env python3
"""#11 vpn(Relay) Apply — 직전 확인 + 승인 saved Plan 그대로 Apply + readback.

💰 비용 발생: Relay EC2 t3.medium·EBS gp3·Relay EIP가 생성 시점부터 과금된다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, vpn Plan WORKDIR(~/iac11-vpn-20261012-020352)에서 실행.
보안: MFA 코드와 임시 자격증명은 메모리에서만 쓰고 파일에 쓰지 않는다.
재실행 금지: 실패·중단 시 다시 돌리지 말고 RESULT를 그대로 보고(복구 절차 v2).
"""
import datetime, getpass, gzip, hashlib, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import urlopen

ACCOUNT = "774055931866"
REGION = "ap-northeast-2"
ME = "321team-hayeoung"
USERS = ("321team-gwonuk", "321team-hayeoung", "321team-jaehwan")
ROLE_NAME = "FDS-IaC-Operator"
ROLE = f"arn:aws:iam::{ACCOUNT}:role/{ROLE_NAME}"
ROLE_ID = "AROA3IOKUF7NEM6P7ZKPK"
BUCKET = f"fds-tfstate-{ACCOUNT}-{REGION}"
STATE_KEY = "phase2/vpn/terraform.tfstate"
LOCK_KEY = STATE_KEY + ".tflock"
NETWORK_STATE_KEY = "phase2/network/terraform.tfstate"
PLAN_SHA256 = "0bb10dc983b46b0145c94f8e26f553fe2487d175452d6f40a17e3d1116c01e23"
TFVARS_SHA256 = "bc658c60569a106fc77a062dda2e983d1775862f54f329ef2f28840996683ee3"
SESSION_DOC = "SSM-SessionManagerRunShell"
AMI = "ami-08d855918a18d0cf9"
RELAY_IP = "10.20.110.10"
LIBRESWAN = ("4.15", "10.el9")
REPO = "https://mirror.stream.centos.org/9-stream/AppStream/x86_64/os"
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
E = P / "evidence-apply"
TF = P / "bin" / "terraform"
os.umask(0o077)
records = []
base = dict(os.environ)
roleenv = None
summary = {"executor": ME, "plan_sha256": PLAN_SHA256, "apply": "NOT_STARTED", "status": "STARTED",
           "prechecks": {}, "checks": {}, "observed": {}}


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
    r = call(name, aws_args(args), env, allowed, 45)
    return r, (json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {})


def listing(name, env, key):
    _, d = aws(name, ["s3api", "list-objects-v2", "--bucket", BUCKET, "--prefix", key, "--max-keys", "10", "--no-paginate"], env)
    assert not d.get("IsTruncated")
    return [o["Key"] for o in d.get("Contents", [])]


def libreswan_in_repo():
    """CentOS Stream 9 AppStream repodata에서 exact NEVRA 존재 확인 (없으면 STOP, 대체 없음)."""
    t = kst()
    repomd = urlopen(REPO + "/repodata/repomd.xml", timeout=60).read()
    save("libreswan-repomd.xml", repomd)
    href = re.search(rb'href="(repodata/[^"]*primary\.xml\.gz)"', repomd).group(1).decode()
    prim = urlopen(REPO + "/" + href, timeout=180).read()
    text = gzip.decompress(prim).decode("utf-8", errors="replace")
    found = re.findall(r'<name>libreswan</name>\s*<arch>x86_64</arch>\s*<version epoch="0" ver="([^"]+)" rel="([^"]+)"/>', text)
    save("libreswan-versions.json", json.dumps({"checked_kst": t, "repomd_url": REPO + "/repodata/repomd.xml",
                                                "primary_url": REPO + "/" + href,
                                                "primary_sha256": hashlib.sha256(prim).hexdigest(),
                                                "x86_64_versions": sorted(set(found))}, indent=2).encode())
    assert LIBRESWAN in found, f"libreswan-{LIBRESWAN[0]}-{LIBRESWAN[1]} 이 repo에 없음 {sorted(set(found))} — STOP (대체 금지)"
    return {"checked_kst": t, "nevra": f"libreswan-{LIBRESWAN[0]}-{LIBRESWAN[1]}.x86_64", "primary": href}


def readback(rh, sds):
    ck, ob = summary["checks"], summary["observed"]
    iid = rh["instance_id"]
    _, d = aws("rb-instance", ["ec2", "describe-instances", "--instance-ids", iid])
    i = d["Reservations"][0]["Instances"][0]
    ck["instance_running"] = i["State"]["Name"] == "running"
    ck["instance_type"] = i["InstanceType"] == "t3.medium"
    ck["instance_ami"] = i["ImageId"] == AMI
    ck["instance_private_ip"] = i.get("PrivateIpAddress") == RELAY_IP
    ck["instance_subnet"] = i["SubnetId"] == rh["subnet_id"]
    ck["imdsv2_required"] = i.get("MetadataOptions", {}).get("HttpTokens") == "required"
    ck["source_dest_check_false"] = i.get("SourceDestCheck") is False
    ck["instance_profile"] = (i.get("IamInstanceProfile") or {}).get("Arn") == rh["instance_profile_arn"]
    ck["public_ip_is_eip"] = i.get("PublicIpAddress") == rh["eip"]
    root = [b for b in i.get("BlockDeviceMappings", []) if b.get("DeviceName") == i.get("RootDeviceName")]
    ck["root_delete_on_termination"] = bool(root) and root[0]["Ebs"].get("DeleteOnTermination") is True
    _, v = aws("rb-volume", ["ec2", "describe-volumes", "--volume-ids", rh["root_volume_id"]])
    vol = v["Volumes"][0]
    ck["root_gp3_le40_encrypted"] = vol["VolumeType"] == "gp3" and vol["Size"] <= 40 and vol["Encrypted"] is True
    ob["root_volume"] = {"type": vol["VolumeType"], "size": vol["Size"], "encrypted": vol["Encrypted"], "kms": vol.get("KmsKeyId")}
    _, r = aws("rb-sg-rules", ["ec2", "describe-security-group-rules", "--filters", f"Name=group-id,Values={rh['security_group_id']}"])
    rules = r["SecurityGroupRules"]
    ing = sorted((x["IpProtocol"], x["FromPort"], x["ToPort"], x.get("CidrIpv4")) for x in rules if not x["IsEgress"])
    egr = sorted((x["IpProtocol"], x["FromPort"], x["ToPort"], x.get("CidrIpv4")) for x in rules if x["IsEgress"])
    ck["sg_ingress_exact"] = ing == [("udp", 500, 500, "0.0.0.0/0"), ("udp", 4500, 4500, "0.0.0.0/0")]
    ck["sg_egress_exact"] = egr == [("tcp", 443, 443, "0.0.0.0/0")]
    ob["sg_rules"] = {"ingress": ing, "egress": egr}
    _, a = aws("rb-eip", ["ec2", "describe-addresses", "--allocation-ids", rh["eip_allocation_id"]])
    addr = a["Addresses"][0]
    ck["eip_on_primary_eni"] = addr.get("NetworkInterfaceId") == rh["primary_eni_id"] and addr.get("PrivateIpAddress") == RELAY_IP
    _, rts = aws("rb-rts", ["ec2", "describe-route-tables", "--filters", f"Name=vpc-id,Values={rh['vpc_id']}"])
    ck["no_onprem_route"] = not any(x.get("DestinationCidrBlock") == "10.1.93.0/24" for t in rts["RouteTables"] for x in t.get("Routes", []))
    ck["route_targets_empty"] = rh.get("route_targets") == {}
    _, doc = aws("rb-ssm-doc", ["ssm", "describe-document", "--name", SESSION_DOC])
    dd = doc["Document"]
    _, gd = aws("rb-ssm-doc-content", ["ssm", "get-document", "--name", SESSION_DOC])
    content_sha = hashlib.sha256(gd["Content"].encode()).hexdigest()
    ck["ssm_doc_owner_type"] = dd.get("Owner") == ACCOUNT and dd.get("DocumentType") == "Session" and dd.get("Status") == "Active"
    ck["ssm_doc_content_sha"] = content_sha == sds["content_sha256"]
    ob["ssm_doc"] = {"owner": dd.get("Owner"), "type": dd.get("DocumentType"), "status": dd.get("Status"),
                     "default_version": dd.get("DefaultVersion"), "content_sha256": content_sha,
                     "session_type": json.loads(gd["Content"]).get("sessionType")}
    # SSM Agent: bootstrap이 설치하므로 최대 15분 대기 (실패를 PASS로 바꾸지 않음)
    online, info = False, {}
    for n in range(31):
        _, ii = aws(f"rb-ssm-agent-{n:02d}", ["ssm", "describe-instance-information", "--filters", f"Key=InstanceIds,Values={iid}"])
        lst = ii.get("InstanceInformationList", [])
        if lst:
            info = {k: lst[0].get(k) for k in ("PingStatus", "AgentVersion", "PlatformName", "PlatformVersion", "LastPingDateTime")}
            if lst[0].get("PingStatus") == "Online":
                online = True
                break
        time.sleep(30)
    ck["ssm_agent_online"] = online
    ob["ssm_agent"] = info or "NOT_REGISTERED_WITHIN_15MIN"
    failed = [k for k, v in ck.items() if v is not True]
    summary["readback_failed"] = failed
    return not failed


try:
    E.mkdir(exist_ok=False)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("iac11_vpn_apply.py", Path(__file__).read_bytes())
    assert (P / "vpn.tfplan").exists() and TF.exists() and S.exists(), "vpn Plan WORKDIR에서 실행하세요"
    got = hashlib.sha256((P / "vpn.tfplan").read_bytes()).hexdigest()
    assert got == PLAN_SHA256, f"Plan 파일 해시 불일치 {got} — STOP"
    tv = (P / "vpn.plan.tfvars.json").read_bytes()
    assert hashlib.sha256(tv).hexdigest() == TFVARS_SHA256, "tfvars 해시 불일치 — STOP"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    call("terraform-version", [str(TF), "version", "-json"])
    tfv = json.loads(tv)

    _, me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요"
    _, role = aws("pre-trust", ["iam", "get-role", "--role-name", ROLE_NAME])
    role = role["Role"]
    doc = role["AssumeRolePolicyDocument"]
    doc = json.loads(doc) if isinstance(doc, str) else doc
    stmts = doc["Statement"] if isinstance(doc["Statement"], list) else [doc["Statement"]]
    allows = [s for s in stmts if s.get("Effect") == "Allow"]
    assert allows and role["RoleId"] == ROLE_ID, "trust/RoleId 변경 — STOP"
    for s in allows:
        assert s.get("Condition", {}).get("Bool", {}).get("aws:MultiFactorAuthPresent") in ("true", True), "trust MFA 조건 없음 — STOP"
    summary["prechecks"]["trust_mfa"] = True
    for u in USERS:
        _, k = aws("pre-access-keys-" + u, ["iam", "list-access-keys", "--user-name", u])
        assert len(k["AccessKeyMetadata"]) == 0, f"{u} Access Key 있음 — STOP"
    summary["prechecks"]["access_keys_0"] = True
    _, q = aws("pre-eip-quota", ["service-quotas", "get-service-quota", "--service-code", "ec2", "--quota-code", "L-0263D0A3"])
    _, eips = aws("pre-eips", ["ec2", "describe-addresses"])
    used, quota = len(eips["Addresses"]), int(q["Quota"]["Value"])
    assert used + 1 <= quota, f"EIP quota 부족 {used}/{quota} — STOP"
    summary["prechecks"]["eip"] = f"{used}/{quota}"
    summary["prechecks"]["libreswan"] = libreswan_in_repo()

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
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac11-vpn-apply-tfdata-", dir="/tmp"))
    summary["session_expiration"] = c["Expiration"]
    c = r = None

    _, ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    summary["before_keys"] = listing("before-keys", roleenv, STATE_KEY)
    assert summary["before_keys"] == [], "vpn state 또는 lock이 이미 있음 — STOP"
    assert listing("network-keys", roleenv, NETWORK_STATE_KEY) == [NETWORK_STATE_KEY], "network state/lock 예상과 다름 — STOP"
    nh = tfv["network_handoff"]
    _, sn = aws("pre-transport-subnet", ["ec2", "describe-subnets", "--subnet-ids", nh["subnets"]["public_transport_a"]["id"]], roleenv)
    s0 = sn["Subnets"][0]
    assert s0["VpcId"] == nh["vpc_id"] and s0["CidrBlock"] == "10.20.110.0/24" and s0["AvailabilityZoneId"] == "apne2-az1", "network handoff 불일치 — STOP"
    _, inst = aws("pre-tag-instances", ["ec2", "describe-instances", "--filters", "Name=tag:Project,Values=fds-hybrid",
                                        "Name=instance-state-name,Values=pending,running,stopping,stopped"], roleenv)
    assert sum(len(x["Instances"]) for x in inst["Reservations"]) == 0, "프로젝트 태그 EC2 이미 있음 — STOP"
    dr, _ = aws("pre-ssm-document", ["ssm", "describe-document", "--name", SESSION_DOC], roleenv, allowed=(0, 254, 255))
    if dr.returncode == 0:
        raise RuntimeError(f"{SESSION_DOC} 문서가 이미 있음 — 생성·import·덮어쓰기 없이 STOP")
    assert "InvalidDocument" in dr.stderr.decode(errors="replace"), "문서 조회가 InvalidDocument가 아님(거부/오류) — STOP"
    summary["prechecks"]["session_document"] = "ABSENT (InvalidDocument)"

    cmd = [str(TF), "-chdir=" + str(S / "terraform/vpn")]
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"

    print("💰 APPLY 시작 — Relay 생성에 수 분 걸립니다. 창을 닫거나 다시 실행하지 마세요.", flush=True)
    summary["apply"] = "STARTED"
    summary["apply_started_kst"] = kst()
    ap = call("apply", cmd + ["apply", "-input=false", "-lock-timeout=60s", "-no-color", str(P / "vpn.tfplan")],
              roleenv, allowed=(0, 1), timeout=1800)
    summary["apply_finished_kst"] = kst()
    summary["apply_rc"] = ap.returncode
    tail = [ln for ln in ap.stdout.decode(errors="replace").splitlines() if "Apply complete!" in ln]
    summary["apply_line"] = tail[-1] if tail else None
    if ap.returncode != 0:
        summary["apply"] = "FAILED"
        raise RuntimeError("apply rc=1 — 재실행 금지, 복구 절차 v2 (evidence-apply/apply.stderr)")
    summary["apply"] = "COMPLETE"
    assert summary["apply_line"] and "8 added, 0 changed, 0 destroyed" in summary["apply_line"], "Apply 결과 수 불일치"

    rh = json.loads(call("output-relay", cmd + ["output", "-json", "relay_handoff"], roleenv).stdout)
    sds = json.loads(call("output-session-doc", cmd + ["output", "-json", "session_document_source"], roleenv).stdout)
    call("state-list", cmd + ["state", "list"], roleenv)
    summary["relay_handoff"] = rh
    print("readback 중 — SSM Agent Online 대기 최대 15분. 기다려 주세요.", flush=True)
    ok = readback(rh, sds)
    summary["status"] = "APPLY_AND_READBACK_PASS" if ok else "APPLY_DONE_READBACK_MISMATCH"
except Exception as exc:
    if summary["status"] == "STARTED":
        summary["status"] = "STOP"
    summary["error"] = str(exc)
    print("STOP", exc, flush=True)
finally:
    if roleenv:
        try:
            summary["after_keys"] = listing("after-keys", roleenv, STATE_KEY)
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
        "prechecks", "readback_failed", "checks", "observed", "relay_handoff", "before_keys", "after_keys",
        "lock_current_absent", "state_created", "started_kst", "finished_kst")}, ensure_ascii=False, indent=2), flush=True)
    print("EVIDENCE_DIR", E, flush=True)
    sys.exit(0 if summary["status"] == "APPLY_AND_READBACK_PASS" else 1)
