#!/usr/bin/env python3
"""U1-I2 — 하영 본인 MFA IaC 역할로 network init/validate/plan (Apply 없음).

실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인.
비용: 없음. Plan은 계획서만 만든다. state 파일은 만들지 않고, native lock(.tflock)만 잠깐 생겼다 지워진다.
보안: MFA 코드와 임시 자격증명은 메모리에서만 쓰고 파일에 쓰지 않는다(AssumeRole 응답은 저장 전에 Credentials 제거).
"""
import base64, datetime, getpass, hashlib, io, json, os, subprocess, sys, tarfile, tempfile, zipfile
from pathlib import Path
from urllib.request import urlopen

ACCOUNT = "774055931866"
REGION = "ap-northeast-2"
ME = "321team-hayeoung"
ROLE = f"arn:aws:iam::{ACCOUNT}:role/FDS-IaC-Operator"
ROLE_ID = "AROA3IOKUF7NEM6P7ZKPK"
BUCKET = f"fds-tfstate-{ACCOUNT}-{REGION}"
STATE_KEY = "phase2/network/terraform.tfstate"
LOCK_KEY = STATE_KEY + ".tflock"
SOURCE_MAIN = "81162467bb2f99a099cb7067fbc3f63e1c0dbed8"
SOURCE_CHECKED_ON = "cca0388 (infra-terraform main 2026-10-09, network 6파일 81162467와 동일)"
TF_VERSION = "1.16.4"
TF_ZIP = f"terraform_{TF_VERSION}_linux_amd64.zip"
TF_ZIP_SHA256 = "dc94af0eef1147718ad7c8daea792ed199e3e0492eec180d0adafa2a65a879df"
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "ae904de11034f1f847757c3bf1e2131cc8d4d1666a5676f5b2fdac89c6b987f0",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
    "terraform/network/tests/network.tftest.hcl": "490d2e5a9f03db2f712a94c2f46618c318b8b83071dfc80fa2df3a56ef3b8735",
}
EXPECTED_ACTIONS = {"create": 20}

P = Path(__file__).resolve().parent
S = P / "source"
E = P / "evidence"
TF = P / "bin" / "terraform"
os.umask(0o077)
records = []
base = dict(os.environ)
roleenv = None
summary = {"executor": ME, "source_main": SOURCE_MAIN, "source_checked_on": SOURCE_CHECKED_ON,
           "apply": "NOT_RUN", "lock_fixture": "NOT_RUN", "status": "STARTED"}


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
        raise RuntimeError(name + " timeout; 본인 lock 상태부터 확인하고 재실행하지 마세요")
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
    return call(name, aws_args(args), env, allowed, 45)


def listing(name, env):
    r = aws(name, ["s3api", "list-objects-v2", "--bucket", BUCKET, "--prefix", STATE_KEY, "--max-keys", "10", "--no-paginate"], env)
    d = json.loads(r.stdout or b"{}")
    assert not d.get("IsTruncated")
    return [o["Key"] for o in d.get("Contents", [])]


def install_terraform():
    url = f"https://releases.hashicorp.com/terraform/{TF_VERSION}/{TF_ZIP}"
    data = urlopen(url, timeout=60).read()
    h = hashlib.sha256(data).hexdigest()
    summary["terraform_zip_sha256"] = h
    assert h == TF_ZIP_SHA256, f"terraform zip sha256 mismatch: {h}"
    TF.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        TF.write_bytes(z.read("terraform"))
    TF.chmod(0o700)


def extract_source():
    raw = base64.b64decode((P / "network-source.tar.gz.b64").read_text().replace("\n", ""))
    summary["source_bundle_sha256"] = hashlib.sha256(raw).hexdigest()
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
        names = sorted(m.name for m in t.getmembers() if m.isfile())
        assert names == sorted(MANIFEST), f"unexpected source files: {names}"
        for m in t.getmembers():
            assert not m.name.startswith("/") and ".." not in m.name.split("/")
        try:
            t.extractall(S, filter="data")
        except TypeError:  # Python < 3.12 without the filter backport; names were checked above
            t.extractall(S)
    for n, h in MANIFEST.items():
        got = hashlib.sha256((S / n).read_bytes()).hexdigest()
        assert got == h, f"source hash mismatch {n}: {got}"
    save("source-manifest.json", json.dumps(MANIFEST, indent=2).encode())


try:
    E.mkdir(exist_ok=True)
    summary["started_utc"], summary["started_kst"] = now(), kst()
    save("u1_i2_hayeoung.py", Path(__file__).read_bytes())
    bad_env = [k for k in base if k.startswith(("TF_", "AWS_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN"))
               or k in ("AWS_CA_BUNDLE", "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_DATA_PATH")]
    assert not bad_env, f"unexpected env: {bad_env}"
    assert not (Path.home() / ".terraformrc").exists(), "~/.terraformrc exists"

    extract_source()
    assert not (S / "terraform/network/terraform.tfvars").exists()
    assert not list((S / "terraform/network").glob("*.auto.tfvars*"))
    install_terraform()
    call("terraform-version", [str(TF), "version", "-json"])

    me = json.loads(aws("pre-caller", ["sts", "get-caller-identity"]).stdout)
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요 (root/타인 금지)"
    serial = subprocess.run(aws_args(["iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"]),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
    if not serial or serial == "null":
        serial = input("MFA 장치 ARN 입력: ").strip()
    summary["mfa_serial"] = serial

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
    save("assume-role.stderr", r.stderr)
    records.append({"name": "assume-role", "argv": shown, "started_utc": t, "finished_utc": now(), "rc": 0,
                    "stdout_sha256": hashlib.sha256(red).hexdigest(), "note": "Credentials removed in memory before write"})
    roleenv = dict(base)
    roleenv.update(AWS_ACCESS_KEY_ID=c["AccessKeyId"], AWS_SECRET_ACCESS_KEY=c["SecretAccessKey"],
                   AWS_SESSION_TOKEN=c["SessionToken"], AWS_MAX_ATTEMPTS="1", TF_IN_AUTOMATION="1",
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-u1-i2-tfdata-", dir="/tmp"))
    summary["session_expiration"] = c["Expiration"]
    c = r = None

    ident = json.loads(aws("role-caller", ["sts", "get-caller-identity"], roleenv).stdout)
    assert ident["Arn"] == f"arn:aws:sts::{ACCOUNT}:assumed-role/FDS-IaC-Operator/{ME}"
    assert ident["UserId"].startswith(ROLE_ID + ":")
    summary["role_arn"] = ident["Arn"]

    summary["before_keys"] = listing("before-keys", roleenv)
    assert summary["before_keys"] == [], "state 또는 lock이 이미 있음 (다른 사람이 작업 중일 수 있음) — 중단하고 권욱 님과 확인"

    cmd = [str(TF), "-chdir=" + str(S / "terraform/network")]
    call("fmt", cmd + ["fmt", "-check", "-recursive"], roleenv)
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"
    v = json.loads(call("validate", cmd + ["validate", "-json"], roleenv).stdout)
    assert v["valid"]
    call("plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode",
                        "-var=execution_enabled=true", "-out=" + str(P / "network.tfplan")], roleenv, allowed=(0, 2), timeout=180)
    plan = json.loads(subprocess.run(cmd + ["show", "-json", str(P / "network.tfplan")], env=roleenv,
                                     capture_output=True, timeout=60, check=True).stdout)
    counts = {}
    for rc in plan.get("resource_changes", []):
        if rc["mode"] == "managed":
            k = "/".join(rc["change"]["actions"])
            counts[k] = counts.get(k, 0) + 1
    summary["managed_actions"] = counts
    summary["planned_addresses"] = sorted(rc["address"] for rc in plan.get("resource_changes", []) if rc["mode"] == "managed")
    summary["plan_sha256"] = hashlib.sha256((P / "network.tfplan").read_bytes()).hexdigest()
    assert counts == EXPECTED_ACTIONS, f"unexpected planned changes: {counts}"
    summary["status"] = "PLAN_CAPTURED"
except Exception as exc:
    summary.update(status="STOP", error=str(exc))
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
    print("RESULT", json.dumps({k: summary.get(k) for k in ("status", "error", "role_arn", "managed_actions",
                                                             "before_keys", "after_keys", "lock_current_absent",
                                                             "state_created", "plan_sha256", "started_kst", "finished_kst")},
                               ensure_ascii=False, indent=2), flush=True)
    print("EVIDENCE_DIR", E, flush=True)
    sys.exit(0 if summary["status"] == "PLAN_CAPTURED" else 1)
