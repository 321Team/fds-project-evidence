#!/usr/bin/env python3
"""U1-I3 — 하영 본인용 래퍼. 권욱 실행기 tools/u1_lock_fixture.py(infra-terraform main)를 바이트 그대로 사용한다.

래퍼가 바꾸는 것은 세 가지뿐이다.
  1) 실행 주체 CALLER를 321team-hayeoung 역할 세션으로 지정
  2) 소스를 git 대신 I2 폴더의 network 소스 묶음에서 읽음 (같은 6파일, 해시 고정)
  3) 본인 MFA로 AssumeRole 해서 자격증명을 이 프로세스 메모리(환경변수)에만 둠. 파일에 쓰지 않음

사용:
  점검만(읽기 전용):  python3 u1_i3_hayeoung.py --i2-dir ~/fds-u1-i2-hayeoung-XXXX
  실제 시험(작업창):   python3 u1_i3_hayeoung.py --i2-dir ~/fds-u1-i2-hayeoung-XXXX --execute --window-confirmation <작업창 확인 댓글 URL>
비용: 없음. 생성되는 것은 network .tflock 시험 파일 1개뿐이고, 실행기가 조건부 삭제한다. Apply·state 쓰기 없음.
"""
import argparse, base64, getpass, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "u1_lock_fixture.py"
RUNNER_SHA256 = "645341054d3f5369b5950f38d1fc2fa5578f6a6a0334d6dbf3f6608a3f9aaa84"
ACCOUNT = "774055931866"
REGION = "ap-northeast-2"
ME = "321team-hayeoung"
ROLE = f"arn:aws:iam::{ACCOUNT}:role/FDS-IaC-Operator"
MANIFEST = {
    "terraform/network/.terraform.lock.hcl": "19d9d35be5e84e592d2714ebf7ecd11a75610fd3addc2c22a8d1f9445a6ca38f",
    "terraform/network/outputs.tf": "0fe4a006ac434c12856dc8c086f17bb7daf1748b8b82af3a9946ba4146fff2b7",
    "terraform/network/backend.hcl.example": "e6c4ddf2036b3d46cb7243cc3b0a2b57976d6f6f660795cd4d549417fda920ff",
    "terraform/network/main.tf": "ae904de11034f1f847757c3bf1e2131cc8d4d1666a5676f5b2fdac89c6b987f0",
    "terraform/network/versions.tf": "e653faf7197736809b47bb46b8830a3f5efbe6ddb137f36ac04f436fa0ff3bca",
    "terraform/network/tests/network.tftest.hcl": "490d2e5a9f03db2f712a94c2f46618c318b8b83071dfc80fa2df3a56ef3b8735",
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_bundle(i2_dir):
    raw = base64.b64decode((i2_dir / "network-source.tar.gz.b64").read_text().replace("\n", ""))
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
        for m in t.getmembers():
            if m.isfile():
                out[m.name] = t.extractfile(m).read()
    assert sorted(out) == sorted(MANIFEST), f"bundle file set mismatch: {sorted(out)}"
    for n, h in MANIFEST.items():
        assert sha(out[n]) == h, f"bundle hash mismatch: {n}"
    return out


def assume_role_into_env():
    def aws(*a):
        return ["aws", *a, "--region", REGION, "--output", "json", "--no-cli-pager"]
    me = json.loads(subprocess.run(aws("sts", "get-caller-identity"), capture_output=True, check=True, timeout=45).stdout)
    assert me["Arn"] == f"arn:aws:iam::{ACCOUNT}:user/{ME}", "본인 IAM 사용자로 실행하세요 (root/타인 금지)"
    serial = subprocess.run(aws("iam", "list-mfa-devices", "--user-name", ME, "--query", "MFADevices[0].SerialNumber"),
                            capture_output=True, timeout=45).stdout.decode().strip().strip('"')
    if not serial or serial == "null":
        serial = input("MFA 장치 ARN 입력: ").strip()
    code = getpass.getpass("MFA 6자리 (화면에 안 보임): ").strip()
    r = subprocess.run(aws("sts", "assume-role", "--role-arn", ROLE, "--role-session-name", ME,
                           "--serial-number", serial, "--token-code", code, "--duration-seconds", "1800"),
                       capture_output=True, timeout=45)
    code = None
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode(errors="replace"))
        raise SystemExit("AssumeRole 실패 — 중단")
    c = json.loads(r.stdout)["Credentials"]
    r = None
    os.environ["AWS_ACCESS_KEY_ID"] = c["AccessKeyId"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = c["SecretAccessKey"]
    os.environ["AWS_SESSION_TOKEN"] = c["SessionToken"]
    print("role session expires", c["Expiration"], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i2-dir", type=Path, required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--window-confirmation")
    a = ap.parse_args()
    i2 = a.i2_dir.expanduser().resolve()
    tf = i2 / "bin" / "terraform"
    assert tf.exists(), f"I2의 terraform이 없습니다: {tf}"

    body = RUNNER.read_bytes()
    assert sha(body) == RUNNER_SHA256, f"runner sha256 mismatch: {sha(body)}"
    files = load_bundle(i2)

    spec = importlib.util.spec_from_file_location("u1_lock_fixture", RUNNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.CALLER = f"arn:aws:sts::{ACCOUNT}:assumed-role/FDS-IaC-Operator/{ME}"
    m.__file__ = str(RUNNER)

    # 원본 preflight의 git 단계만 묶음 읽기로 바꾸고, 나머지 검사는 원본 그대로 실행한다.
    original = m.Live.preflight

    def preflight(self, repo):
        real_call = self.call

        def call(name, argv, timeout=45):
            if name == "source-files":
                return subprocess.CompletedProcess(argv, 0, "\n".join(sorted(files)).encode() + b"\n", b"")
            if name.startswith("source-blob-"):
                path = argv[-1].split(":", 1)[1]
                return subprocess.CompletedProcess(argv, 0, files[path], b"")
            return real_call(name, argv, timeout)
        self.call = call
        try:
            return original(self, repo)
        finally:
            self.call = real_call
    m.Live.preflight = preflight

    # CloudShell 홈(1GB)에는 AWS provider(수백 MB)가 들어가지 않는다. 실행기는 Path.home() 아래에
    # 작업 폴더를 만들므로, 실행 중에만 HOME을 /tmp의 개인 폴더로 바꾸고 끝나면 로그를 홈으로 복사한다.
    real_home = Path.home()
    work_home = Path(tempfile.mkdtemp(prefix="fds-u1-i3-home-", dir="/tmp" if os.name == "posix" else None))
    os.environ["HOME"] = os.environ["USERPROFILE"] = str(work_home)

    assume_role_into_env()
    argv = ["u1_lock_fixture.py", "--repo", str(HERE), "--terraform", str(tf)]
    if a.execute:
        argv += ["--execute", "--window-confirmation", a.window_confirmation or ""]
    sys.argv = argv
    try:
        rc = m.main()
    finally:
        for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
            os.environ.pop(k, None)
        os.environ["HOME"] = os.environ["USERPROFILE"] = str(real_home)
        results = HERE / "results"
        results.mkdir(exist_ok=True)
        for run_dir in sorted(work_home.glob("fds-u1-lock-*")):
            shutil.copytree(run_dir, results / run_dir.name, ignore=shutil.ignore_patterns(".terraform"))
            print("RESULTS_COPIED", results / run_dir.name, "(provider cache .terraform excluded)", flush=True)
    print("WRAPPER_SHA256", sha(Path(__file__).read_bytes()), "RUNNER_SHA256", sha(body), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
