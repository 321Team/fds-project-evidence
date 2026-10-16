#!/usr/bin/env python3
"""#11/#35 network subnet ROSA LB 역할 태그 2건 — 새 Plan만 (Apply 없음).

비용: 없음. 조회와 Plan만 한다. state는 쓰지 않고 native lock(.tflock)만 잠깐 생겼다 지워진다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, **조율된 network 작업창 안에서만**.
source: infra-terraform main f1f8adf (PR27 병합 이후) terraform/network 6파일. Terraform 바이너리는 #11 network WORKDIR의 검증본 재사용.
기대: RC2, aws_subnet.project["private_a"]·["public_transport_a"] 2개만 update, 바뀌는 속성은 tags/tags_all의 역할 태그 1개씩.
      그 외 자원 no-op, output 변경 0, create/delete/replace 0. 하나라도 다르면 STOP.
보안: MFA 코드와 임시 자격증명은 메모리에서만 쓰고 파일에 쓰지 않는다. state 원문은 내려받지 않는다.
      Plan 파일·전체 JSON(prior state 사본 포함)은 증적 묶음 밖 WORKDIR에 두고 해시만 기록한다(검토 전달은 별도).
"""
import base64, datetime, getpass, hashlib, io, json, os, shutil, subprocess, sys, tarfile, tempfile
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
SOURCE_MAIN = "f1f8adf66d3b3c9348ebb919fe0dbb4f8fa54fe2"
TF_VERSION = "1.16.4"
AWS_PROVIDER = "6.66.0"
NETWORK_WORKDIR = Path.home() / "iac11-network-20261012-002405"
EXPECTED_STATE_COUNT = 20
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "e79a35f5b54ac3cd68e1c32964929c6113a2ab7bfc749c7663358c950e9f481d",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/tests/network.tftest.hcl": "ead2188c20e921eb6debef38bc77205f7fdd4e06c1d466dabf9292b054dc6139",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
}
EXPECTED_TAGS = {
    'aws_subnet.project["private_a"]': ("kubernetes.io/role/internal-elb", "1"),
    'aws_subnet.project["public_transport_a"]': ("kubernetes.io/role/elb", "1"),
}

P = Path(__file__).resolve().parent
S = P / "source"
TF = P / "bin" / "terraform"
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d-%H%M%S")
E = P / f"evidence-tagplan-{STAMP}"
PLAN = P / f"tagplan-{STAMP}.tfplan"
os.umask(0o077)
records = []
base = dict(os.environ)
roleenv = None
summary = {"executor": ME, "source_main": SOURCE_MAIN, "apply": "NOT_RUN", "status": "STARTED", "checks": {}, "warnings": []}


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
        raise RuntimeError(name + " timeout — 재실행하지 말고 lock 상태부터 확인")
    if stdout_dir:
        (stdout_dir / (name + ".stdout")).write_bytes(r.stdout)
    else:
        save(name + ".stdout", r.stdout)
    save(name + ".stderr", r.stderr)
    records.append({"name": name, "argv": shown or args, "started_utc": t, "finished_utc": now(), "rc": r.returncode,
                    "stdout_kept_outside_evidence": bool(stdout_dir), "stdout_sha256": hashlib.sha256(r.stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(r.stderr).hexdigest()})
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


def extract_source():
    raw = base64.b64decode((P / "network-tag-source.tar.gz.b64").read_text().replace("\n", ""))
    summary["source_bundle_sha256"] = hashlib.sha256(raw).hexdigest()
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
        names = sorted(m.name for m in t.getmembers() if m.isfile())
        assert names == sorted(MANIFEST), f"unexpected source files: {names}"
        for m in t.getmembers():
            assert not m.name.startswith("/") and ".." not in m.name.split("/")
        try:
            t.extractall(S, filter="data")
        except TypeError:
            t.extractall(S)
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    save("source-manifest.json", json.dumps(MANIFEST, indent=2).encode())


def judge(plan):
    """태그 2건 외 변경이 있으면 이유를 돌려준다 (빈 목록 = 기대와 일치)."""
    bad, detail = [], []
    for rc in plan.get("resource_changes", []):
        a, acts = rc["address"], rc["change"]["actions"]
        if rc["mode"] != "managed":
            continue
        if a in EXPECTED_TAGS:
            if acts != ["update"]:
                bad.append(f"{a} actions={acts}")
                continue
            before, after = rc["change"]["before"] or {}, rc["change"]["after"] or {}
            unknown = rc["change"].get("after_unknown") or {}
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k) or unknown.get(k))
            k, v = EXPECTED_TAGS[a]
            want_tags = dict(before.get("tags") or {}, **{k: v})
            want_all = dict(before.get("tags_all") or {}, **{k: v})
            ok = (set(changed) <= {"tags", "tags_all"} and after.get("tags") == want_tags
                  and after.get("tags_all") == want_all)
            detail.append({"address": a, "changed_attrs": changed, "added_tag": {k: v}, "ok": ok})
            if not ok:
                bad.append(f"{a} 예상 밖 속성 변경 {changed}")
        elif acts != ["no-op"]:
            bad.append(f"{a} actions={acts}")
    missing = [a for a in EXPECTED_TAGS if a not in {rc["address"] for rc in plan.get("resource_changes", [])}]
    bad += [f"{a} Plan에 없음" for a in missing]
    out_changed = [k for k, oc in (plan.get("output_changes") or {}).items() if oc.get("actions") != ["no-op"]]
    bad += [f"output {k} 변경" for k in out_changed]
    return bad, detail


try:
    E.mkdir(exist_ok=False)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("iac11_network_tagplan.py", Path(__file__).read_bytes())
    nw_tf = NETWORK_WORKDIR / "bin" / "terraform"
    assert nw_tf.exists(), f"{nw_tf} 없음 — #11 network WORKDIR 확인"
    TF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(nw_tf, TF)
    summary["terraform_binary_sha256"] = hashlib.sha256(TF.read_bytes()).hexdigest()
    extract_source()
    summary["checks"]["source_6_files_match_main"] = True
    assert not list((S / "terraform/network").glob("*.tfvars*")), "tfvars 있음 — STOP"
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    assert not (Path.home() / ".terraformrc").exists(), "~/.terraformrc exists"

    me = aws("pre-caller", ["sts", "get-caller-identity"])
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요 (root/타인 금지)"
    summary["account_guard"] = me["Account"] == ACCOUNT
    role = aws("pre-trust", ["iam", "get-role", "--role-name", ROLE_NAME])["Role"]
    doc = role["AssumeRolePolicyDocument"]
    doc = json.loads(doc) if isinstance(doc, str) else doc
    stmts = doc["Statement"] if isinstance(doc["Statement"], list) else [doc["Statement"]]
    allows = [s for s in stmts if s.get("Effect") == "Allow"]
    summary["checks"]["trust_mfa_roleid"] = bool(allows) and role["RoleId"] == ROLE_ID and all(
        s.get("Condition", {}).get("Bool", {}).get("aws:MultiFactorAuthPresent") in ("true", True) for s in allows)
    assert summary["checks"]["trust_mfa_roleid"], "trust/RoleId/MFA 조건 변경 — STOP"
    att = aws("pre-role-policies", ["iam", "list-attached-role-policies", "--role-name", ROLE_NAME])
    summary["role_attached_policies"] = sorted(p["PolicyName"] for p in att.get("AttachedPolicies", []))
    for u in ("321team-gwonuk", "321team-hayeoung", "321team-jaehwan"):
        n = len(aws("pre-access-keys-" + u, ["iam", "list-access-keys", "--user-name", u])["AccessKeyMetadata"])
        assert n == 0, f"{u} Access Key {n}개 — STOP"
    summary["checks"]["access_keys_0"] = True
    ver = aws("pre-versioning", ["s3api", "get-bucket-versioning", "--bucket", BUCKET])
    summary["checks"]["bucket_versioning_enabled"] = ver.get("Status") == "Enabled"
    assert summary["checks"]["bucket_versioning_enabled"], "state bucket versioning 아님 — STOP"

    serial = subprocess.run(aws_args(["iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"]),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
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
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac11-tagplan-tfdata-", dir="/tmp"))
    c = r = None

    ident = aws("role-caller", ["sts", "get-caller-identity"], roleenv)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE_NAME}/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    summary["before_keys"] = listing("before-keys", roleenv)
    assert STATE_KEY in summary["before_keys"], "network state가 없음 — STOP"
    assert LOCK_KEY not in summary["before_keys"], "lock이 남아 있음(다른 writer?) — STOP"
    summary["state_before"] = state_head("state-head-before", roleenv)

    cmd = [str(TF), "-chdir=" + str(S / "terraform/network")]
    call("fmt", cmd + ["fmt", "-check", "-recursive"], roleenv)
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"
    tv = json.loads(call("terraform-version", cmd + ["version", "-json"], roleenv).stdout)
    summary["terraform_version"] = tv.get("terraform_version")
    summary["aws_provider"] = (tv.get("provider_selections") or {}).get("registry.terraform.io/hashicorp/aws")
    summary["checks"]["tool_versions"] = summary["terraform_version"] == TF_VERSION and summary["aws_provider"] == AWS_PROVIDER
    assert summary["checks"]["tool_versions"], "버전 불일치 — STOP"
    assert json.loads(call("validate", cmd + ["validate", "-json"], roleenv).stdout)["valid"]
    sl = call("state-list", cmd + ["state", "list"], roleenv).stdout.decode().splitlines()
    managed = [x for x in sl if x.strip() and not x.startswith("data.")]
    summary["state_list_count"] = {"managed": len(managed), "data": len(sl) - len(managed)}
    summary["checks"]["state_managed_count_20"] = len(managed) == EXPECTED_STATE_COUNT

    summary["plan_started_kst"] = kst()
    pl = call("plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode", "-no-color",
                             "-var=execution_enabled=true", "-out=" + str(PLAN)], roleenv, allowed=(0, 2), timeout=300)
    summary["plan_finished_kst"] = kst()
    summary["plan_rc"] = pl.returncode
    summary["plan_line"] = next((ln for ln in pl.stdout.decode(errors="replace").splitlines()
                                 if ln.startswith(("No changes.", "Plan:"))), None)
    show = call("show-json", cmd + ["show", "-json", str(PLAN)], roleenv, stdout_dir=P)
    plan = json.loads(show.stdout)
    summary["plan_file"] = str(PLAN)
    summary["plan_sha256"] = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    summary["plan_json_sha256"] = hashlib.sha256(show.stdout).hexdigest()
    summary["resource_drift"] = [{"address": d["address"], "actions": d["change"]["actions"]} for d in plan.get("resource_drift", [])]
    if summary["resource_drift"]:
        summary["warnings"].append(f"Terraform 밖 변경 감지 {len(summary['resource_drift'])}건 — 검토 필요")
    bad, detail = judge(plan)
    summary["tag_changes"] = detail
    summary["unexpected"] = bad
    save("plan-judgement.json", json.dumps({"tag_changes": detail, "unexpected": bad}, indent=2, ensure_ascii=False).encode())
    if pl.returncode == 2 and not bad and summary["plan_line"] == "Plan: 0 to add, 2 to change, 0 to destroy.":
        summary["status"] = "TAG_PLAN_READY_FOR_REVIEW"
    else:
        summary["status"] = "UNEXPECTED_PLAN_STOP"
        print("STOP 기대와 다른 Plan입니다. Apply하지 말고 RESULT를 그대로 보고하세요.", flush=True)
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
    if summary["status"] == "TAG_PLAN_READY_FOR_REVIEW" and (failed or summary.get("after_check_error")):
        summary["status"] = "POSTCHECK_FAILED"
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
    print()
    print("RESULT", json.dumps({k: summary.get(k) for k in (
        "status", "error", "warnings", "role_arn", "account_guard", "role_attached_policies", "terraform_version", "aws_provider",
        "state_list_count", "plan_rc", "plan_line", "plan_sha256", "plan_json_sha256", "tag_changes", "unexpected",
        "resource_drift", "state_before", "state_after", "checks", "checks_failed", "before_keys", "after_keys",
        "plan_started_kst", "plan_finished_kst", "started_kst", "finished_kst", "plan_file", "evidence_tgz",
        "evidence_tgz_sha256")}, ensure_ascii=False, indent=2), flush=True)
    sys.exit(0 if summary["status"] == "TAG_PLAN_READY_FOR_REVIEW" else 1)
