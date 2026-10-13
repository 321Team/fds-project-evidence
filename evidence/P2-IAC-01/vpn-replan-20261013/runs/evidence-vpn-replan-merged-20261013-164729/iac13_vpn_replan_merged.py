#!/usr/bin/env python3
"""#13 공식 — 병합 source(infra-terraform main 6847d906, PR #30 병합)로 vpn 재실행 무변경(AC-5) 확인 + terraform test(mock). Apply 없음.

비용: 없음. 조회와 Plan만 한다. state는 쓰지 않고 native lock(.tflock)만 잠깐 생겼다 지워진다.
실행 위치: AWS CloudShell 서울, 321team-hayeoung 콘솔 MFA 로그인, vpn WORKDIR(~/iac11-vpn-20261012-020352) 안에서 실행.
source: 원본 source/(36c18e2a, 10파일)를 source-6847d906-<시각>/로 복사하고 main.tf만 병합본(871c0bba)으로 교체 → 병합 커밋 6847d906의 terraform/vpn 10파일과 해시 동일(원본 source/는 건드리지 않음). 입력 vpn.plan.tfvars.json(bc658c60)·bin/terraform 1.16.4는 그대로.
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
E = P / f"evidence-vpn-replan-merged-{STAMP}"
PR30_COMMIT = "192401e"
MERGED_MAIN = "6847d906f974136a5a4aad5ffe47d45930f142e7"
PR30_MAIN_SHA256 = "871c0bbad90f145cf153d0694f3f4ec126ea089123a79e2ec3f636c3a80bf5f6"
PR30_MAIN_B64 = "ZGF0YSAiYXdzX3ZwYyIgIm5ldHdvcmsiIHsKICBpZCA9IHZhci5uZXR3b3JrX2hhbmRvZmYudnBjX2lkCn0KCmRhdGEgImF3c19zdWJuZXQiICJ0cmFuc3BvcnQiIHsKICBpZCA9IHZhci5uZXR3b3JrX2hhbmRvZmYuc3VibmV0cy5wdWJsaWNfdHJhbnNwb3J0X2EuaWQKfQoKZGF0YSAiYXdzX3JvdXRlX3RhYmxlIiAic2VsZWN0ZWQiIHsKICBmb3JfZWFjaCAgICAgICA9IHZhci5hY3RpdmF0ZV9vbnByZW1fcm91dGVzID8gdmFyLm9ucHJlbV9yb3V0ZV9rZXlzIDogdG9zZXQoW10pCiAgcm91dGVfdGFibGVfaWQgPSB2YXIubmV0d29ya19oYW5kb2ZmLnN1Ym5ldHNbZWFjaC5rZXldLnJvdXRlX3RhYmxlX2lkCn0KCmRhdGEgImF3c19hbWkiICJyZWxheSIgewogIG93bmVycyA9IFsiMTI1NTIzMDg4NDI5Il0KICBmaWx0ZXIgewogICAgbmFtZSAgID0gImltYWdlLWlkIgogICAgdmFsdWVzID0gWyJhbWktMDhkODU1OTE4YTE4ZDBjZjkiXQogIH0KICBmaWx0ZXIgewogICAgbmFtZSAgID0gInN0YXRlIgogICAgdmFsdWVzID0gWyJhdmFpbGFibGUiXQogIH0KfQoKZGF0YSAiYXdzX2lhbV9pbnN0YW5jZV9wcm9maWxlIiAicmVsYXkiIHsKICBuYW1lID0gIkZEUy1SZWxheS1TU00iCiAgbGlmZWN5Y2xlIHsKICAgIHBvc3Rjb25kaXRpb24gewogICAgICBjb25kaXRpb24gPSAoCiAgICAgICAgc2VsZi5hcm4gPT0gImFybjphd3M6aWFtOjo3NzQwNTU5MzE4NjY6aW5zdGFuY2UtcHJvZmlsZS9GRFMtUmVsYXktU1NNIiAmJgogICAgICAgIHNlbGYucm9sZV9hcm4gPT0gImFybjphd3M6aWFtOjo3NzQwNTU5MzE4NjY6cm9sZS9GRFMtUmVsYXktU1NNIgogICAgICApCiAgICAgIGVycm9yX21lc3NhZ2UgPSAiRXhpc3RpbmcgQ2xvdWRGb3JtYXRpb24tb3duZWQgUmVsYXkgaWRlbnRpdHkgZGlmZmVycyBmcm9tIHRoZSBhZG9wdGVkIGlkZW50aXR5LiIKICAgIH0KICB9Cn0KCmRhdGEgImF3c19rbXNfa2V5IiAiZWJzIiB7CiAga2V5X2lkID0gImFsaWFzL2F3cy9lYnMiCn0KCmRhdGEgImF3c19zdWJuZXQiICJ3b3JrZXIiIHsKICBjb3VudCA9IHZhci53b3JrZXJfc3VibmV0X2tleSA9PSAiIiA/IDAgOiAxCiAgaWQgICAgPSB2YXIubmV0d29ya19oYW5kb2ZmLnN1Ym5ldHNbdmFyLndvcmtlcl9zdWJuZXRfa2V5XS5pZAogIGxpZmVjeWNsZSB7CiAgICBwb3N0Y29uZGl0aW9uIHsKICAgICAgY29uZGl0aW9uID0gKAogICAgICAgIHNlbGYudnBjX2lkID09IHZhci5uZXR3b3JrX2hhbmRvZmYudnBjX2lkICYmCiAgICAgICAgc2VsZi5jaWRyX2Jsb2NrID09IHZhci5uZXR3b3JrX2hhbmRvZmYuc3VibmV0c1t2YXIud29ya2VyX3N1Ym5ldF9rZXldLmNpZHIgJiYKICAgICAgICBzZWxmLmF2YWlsYWJpbGl0eV96b25lX2lkID09IHZhci5uZXR3b3JrX2hhbmRvZmYuc3VibmV0c1t2YXIud29ya2VyX3N1Ym5ldF9rZXldLnpvbmVfaWQgJiYKICAgICAgICAhc2VsZi5tYXBfcHVibGljX2lwX29uX2xhdW5jaAogICAgICApCiAgICAgIGVycm9yX21lc3NhZ2UgPSAiQWN0dWFsIHdvcmtlciBzdWJuZXQgbXVzdCBtYXRjaCB0aGUgcmV2aWV3ZWQgc2luZ2xlIHByaXZhdGUgc3VibmV0IGhhbmRvZmYuIgogICAgfQogIH0KfQoKIyAjMzcgdHVwbGUgNjA0MTM2OTkyOTogZXhhY3RseSBvbmUgd29ya2VyIHN1Ym5ldDsgbm8gZGVmYXVsdCB3b3JrZXIgY2hvaWNlLgpyZXNvdXJjZSAiYXdzX3NlY3VyaXR5X2dyb3VwIiAicmVsYXkiIHsKICBuYW1lX3ByZWZpeCA9ICJmZHMtcmVsYXktIgogIGRlc2NyaXB0aW9uID0gIkQyMSBSZWxheSBvdXRlciBJS0UvTkFULVQ7IG5vdCBmdWxsIGh5YnJpZCByZWFkaW5lc3MiCiAgdnBjX2lkICAgICAgPSB2YXIubmV0d29ya19oYW5kb2ZmLnZwY19pZAogIHRhZ3MgICAgICAgID0geyBOYW1lID0gImZkcy1yZWxheSIgfQoKICBsaWZlY3ljbGUgewogICAgcHJlY29uZGl0aW9uIHsKICAgICAgY29uZGl0aW9uID0gKAogICAgICAgIHZhci5leGVjdXRpb25fZW5hYmxlZCAmJiB0ZXJyYWZvcm0ud29ya3NwYWNlID09ICJkZWZhdWx0IiAmJgogICAgICAgIGxlbmd0aCh2YXIucmVsYXlfZWdyZXNzKSA+IDAgJiYgbGVuZ3RoKHRyaW1zcGFjZSh2YXIuZWdyZXNzX2NvbnRyYWN0X3JlZmVyZW5jZSkpID4gMCAmJgogICAgICAgIChhbGx0cnVlKFtmb3IgciBpbiB2YXIucmVsYXlfZWdyZXNzIDogci5wb3J0ICE9IDgwXSkgfHwgbGVuZ3RoKHRyaW1zcGFjZSh2YXIuaHR0cF9yZXBvc2l0b3J5X2V2aWRlbmNlX3JlZmVyZW5jZSkpID4gMCkgJiYKICAgICAgICAodmFyLndvcmtlcl9zdWJuZXRfa2V5ID09ICIiIHx8IGxlbmd0aCh0cmltc3BhY2UodmFyLndvcmtlcl9zb3VyY2VfcmVmZXJlbmNlKSkgPiAwKQogICAgICApCiAgICAgIGVycm9yX21lc3NhZ2UgPSAiRGlzYWJsZWQgY2FuZGlkYXRlLCB3cm9uZyB3b3Jrc3BhY2UsIG9yIG1pc3NpbmcgcmV2aWV3ZWQgZWdyZXNzIGNvbnRyYWN0LiBFeGlzdGluZyBHTy9yb2xlL0ZyZWV6ZSByZXF1aXJlbWVudHMgc3RpbGwgYXBwbHkuIgogICAgfQogICAgcHJlY29uZGl0aW9uIHsKICAgICAgY29uZGl0aW9uID0gKAogICAgICAgIGRhdGEuYXdzX3ZwYy5uZXR3b3JrLmNpZHJfYmxvY2sgPT0gIjEwLjIwLjAuMC8xNiIgJiYKICAgICAgICBkYXRhLmF3c19zdWJuZXQudHJhbnNwb3J0LnZwY19pZCA9PSB2YXIubmV0d29ya19oYW5kb2ZmLnZwY19pZCAmJgogICAgICAgIGRhdGEuYXdzX3N1Ym5ldC50cmFuc3BvcnQuY2lkcl9ibG9jayA9PSAiMTAuMjAuMTEwLjAvMjQiICYmCiAgICAgICAgZGF0YS5hd3Nfc3VibmV0LnRyYW5zcG9ydC5hdmFpbGFiaWxpdHlfem9uZSA9PSAiYXAtbm9ydGhlYXN0LTJhIiAmJgogICAgICAgIGRhdGEuYXdzX3N1Ym5ldC50cmFuc3BvcnQuYXZhaWxhYmlsaXR5X3pvbmVfaWQgPT0gImFwbmUyLWF6MSIgJiYKICAgICAgICAhZGF0YS5hd3Nfc3VibmV0LnRyYW5zcG9ydC5tYXBfcHVibGljX2lwX29uX2xhdW5jaAogICAgICApCiAgICAgIGVycm9yX21lc3NhZ2UgPSAiTGl2ZSBWUEMvc3VibmV0IGlkZW50aXR5LCBnZW9tZXRyeSwgQVogb3IgYXV0b21hdGljIHB1YmxpYyBJUCBkaWZmZXJzIGZyb20gdGhlIGhhbmRvZmYuIgogICAgfQogICAgcHJlY29uZGl0aW9uIHsKICAgICAgY29uZGl0aW9uID0gIXZhci5hY3RpdmF0ZV9vbnByZW1fcm91dGVzIHx8ICgKICAgICAgICB2YXIud29ya2VyX3N1Ym5ldF9rZXkgIT0gIiIgJiYKICAgICAgICB2YXIub25wcmVtX3JvdXRlX2tleXMgPT0gdG9zZXQoW3Zhci53b3JrZXJfc3VibmV0X2tleV0pICYmCiAgICAgICAgbGVuZ3RoKHRyaW1zcGFjZSh2YXIudHVubmVsX3JlYWRpbmVzc19yZWZlcmVuY2UpKSA+IDAKICAgICAgKQogICAgICBlcnJvcl9tZXNzYWdlID0gIkRvIG5vdCBhY3RpdmF0ZSByb3V0ZXMgYmVmb3JlIGV4YWN0IHRhcmdldCBrZXlzIGFuZCBhY3R1YWwgdHVubmVsIHJlYWRpbmVzcyBldmlkZW5jZSBhcmUgc3VwcGxpZWQuIgogICAgfQogIH0KfQoKcmVzb3VyY2UgImF3c192cGNfc2VjdXJpdHlfZ3JvdXBfaW5ncmVzc19ydWxlIiAiaWtlIiB7CiAgZm9yX2VhY2ggICAgICAgICAgPSB0b3NldChbIjUwMCIsICI0NTAwIl0pCiAgc2VjdXJpdHlfZ3JvdXBfaWQgPSBhd3Nfc2VjdXJpdHlfZ3JvdXAucmVsYXkuaWQKICBjaWRyX2lwdjQgICAgICAgICA9ICIwLjAuMC4wLzAiCiAgaXBfcHJvdG9jb2wgICAgICAgPSAidWRwIgogIGZyb21fcG9ydCAgICAgICAgID0gdG9udW1iZXIoZWFjaC5rZXkpCiAgdG9fcG9ydCAgICAgICAgICAgPSB0b251bWJlcihlYWNoLmtleSkKICBkZXNjcmlwdGlvbiAgICAgICA9ICJEMjEgb3V0ZXIgSUtFL05BVC1UIG9ubHkiCn0KCnJlc291cmNlICJhd3NfdnBjX3NlY3VyaXR5X2dyb3VwX2luZ3Jlc3NfcnVsZSIgIndvcmtlcl9kYiIgewogIGNvdW50ICAgICAgICAgICAgID0gdmFyLndvcmtlcl9zdWJuZXRfa2V5ID09ICIiID8gMCA6IDEKICBzZWN1cml0eV9ncm91cF9pZCA9IGF3c19zZWN1cml0eV9ncm91cC5yZWxheS5pZAogIGNpZHJfaXB2NCAgICAgICAgID0gZGF0YS5hd3Nfc3VibmV0LndvcmtlclswXS5jaWRyX2Jsb2NrCiAgaXBfcHJvdG9jb2wgICAgICAgPSAidGNwIgogIGZyb21fcG9ydCAgICAgICAgID0gNTQzMgogIHRvX3BvcnQgICAgICAgICAgID0gNTQzMgogIGRlc2NyaXB0aW9uICAgICAgID0gIlJldmlld2VkIHdvcmtlciBzdWJuZXQgdG8gREIgcGF0aDsgZGVzdGluYXRpb24gZW5mb3JjZWQgYnkgaG9zdCBGT1JXQVJEIGFuZCBEQiBjb250cm9scyIKfQoKcmVzb3VyY2UgImF3c192cGNfc2VjdXJpdHlfZ3JvdXBfZWdyZXNzX3J1bGUiICJyZXZpZXdlZCIgewogIGZvcl9lYWNoICAgICAgICAgID0gdmFyLnJlbGF5X2VncmVzcwogIHNlY3VyaXR5X2dyb3VwX2lkID0gYXdzX3NlY3VyaXR5X2dyb3VwLnJlbGF5LmlkCiAgY2lkcl9pcHY0ICAgICAgICAgPSBlYWNoLnZhbHVlLmNpZHJfaXB2NAogIGlwX3Byb3RvY29sICAgICAgID0gZWFjaC52YWx1ZS5wcm90b2NvbAogIGZyb21fcG9ydCAgICAgICAgID0gZWFjaC52YWx1ZS5wb3J0CiAgdG9fcG9ydCAgICAgICAgICAgPSBlYWNoLnZhbHVlLnBvcnQKICBkZXNjcmlwdGlvbiAgICAgICA9IGVhY2gudmFsdWUuZGVzY3JpcHRpb24KfQoKcmVzb3VyY2UgImF3c19pbnN0YW5jZSIgInJlbGF5IiB7CiAgYW1pICAgICAgICAgICAgICAgICAgICAgICAgID0gZGF0YS5hd3NfYW1pLnJlbGF5LmlkCiAgaW5zdGFuY2VfdHlwZSAgICAgICAgICAgICAgID0gInQzLm1lZGl1bSIKICBzdWJuZXRfaWQgICAgICAgICAgICAgICAgICAgPSB2YXIubmV0d29ya19oYW5kb2ZmLnN1Ym5ldHMucHVibGljX3RyYW5zcG9ydF9hLmlkCiAgcHJpdmF0ZV9pcCAgICAgICAgICAgICAgICAgID0gIjEwLjIwLjExMC4xMCIKICBhc3NvY2lhdGVfcHVibGljX2lwX2FkZHJlc3MgPSBmYWxzZQogIHNvdXJjZV9kZXN0X2NoZWNrICAgICAgICAgICA9IGZhbHNlCiAgdnBjX3NlY3VyaXR5X2dyb3VwX2lkcyAgICAgID0gW2F3c19zZWN1cml0eV9ncm91cC5yZWxheS5pZF0KICBpYW1faW5zdGFuY2VfcHJvZmlsZSAgICAgICAgPSBkYXRhLmF3c19pYW1faW5zdGFuY2VfcHJvZmlsZS5yZWxheS5uYW1lCiAgdXNlcl9kYXRhID0gdGVtcGxhdGVmaWxlKCIke3BhdGgubW9kdWxlfS9ib290c3RyYXAuc2gudGZ0cGwiLCB7CiAgICBsaWJyZXN3YW5fcGFja2FnZV9zcGVjID0gdmFyLmxpYnJlc3dhbl9wYWNrYWdlX3NwZWMKICAgIGFnZW50X3NpZ25pbmdfa2V5ICAgICAgPSBmaWxlKCIke3BhdGgubW9kdWxlfS9hbWF6b24tc3NtLWFnZW50LmdwZyIpCiAgfSkKICB1c2VyX2RhdGFfcmVwbGFjZV9vbl9jaGFuZ2UgPSB0cnVlCiAgdGFncyAgICAgICAgICAgICAgICAgICAgICAgID0geyBOYW1lID0gImZkcy1yZWxheSIgfQoKICBtZXRhZGF0YV9vcHRpb25zIHsKICAgIGh0dHBfZW5kcG9pbnQgPSAiZW5hYmxlZCIKICAgIGh0dHBfdG9rZW5zICAgPSAicmVxdWlyZWQiCiAgfQogIGNyZWRpdF9zcGVjaWZpY2F0aW9uIHsKICAgIGNwdV9jcmVkaXRzID0gdmFyLmNwdV9jcmVkaXRfbW9kZQogIH0KICByb290X2Jsb2NrX2RldmljZSB7CiAgICB2b2x1bWVfdHlwZSAgICAgICAgICAgPSAiZ3AzIgogICAgdm9sdW1lX3NpemUgICAgICAgICAgID0gNDAKICAgIGVuY3J5cHRlZCAgICAgICAgICAgICA9IHRydWUKICAgIGttc19rZXlfaWQgICAgICAgICAgICA9IGRhdGEuYXdzX2ttc19rZXkuZWJzLmFybgogICAgZGVsZXRlX29uX3Rlcm1pbmF0aW9uID0gdmFyLnJvb3RfZGVsZXRlX29uX3Rlcm1pbmF0aW9uCiAgfQogIGRlcGVuZHNfb24gPSBbYXdzX3ZwY19zZWN1cml0eV9ncm91cF9pbmdyZXNzX3J1bGUuaWtlLCBhd3NfdnBjX3NlY3VyaXR5X2dyb3VwX2VncmVzc19ydWxlLnJldmlld2VkXQoKICAjIExhdW5jaC10aW1lIGludGVudCBzdGF5cyBmYWxzZS4gQWZ0ZXIgYXdzX2VpcF9hc3NvY2lhdGlvbiBhdHRhY2hlcyB0aGUgUmVsYXkgRUlQIHRoZSBwcm92aWRlcgogICMgcmVhZHMgdGhpcyBGb3JjZU5ldyBhdHRyaWJ1dGUgYmFjayBhcyB0cnVlLCBzbyBldmVyeSBsYXRlciBwbGFuIHdvdWxkIHJlcGxhY2UgdGhlIFJlbGF5ICgjMTMgcmUtcGxhbiAyMDI2LTEwLTEyKS4KICBsaWZlY3ljbGUgewogICAgaWdub3JlX2NoYW5nZXMgPSBbYXNzb2NpYXRlX3B1YmxpY19pcF9hZGRyZXNzXQogIH0KfQoKIyBFSVAgY3JlYXRpb24gaXMgZG93bnN0cmVhbSBvZiB0aGUgZ3VhcmRlZCBpbnN0YW5jZSwgbm90IGFuIGluZGVwZW5kZW50IGJ5cGFzcy4KcmVzb3VyY2UgImF3c19laXAiICJyZWxheSIgewogIGRvbWFpbiAgICAgPSAidnBjIgogIHRhZ3MgICAgICAgPSB7IE5hbWUgPSAiZmRzLXJlbGF5IiB9CiAgZGVwZW5kc19vbiA9IFthd3NfaW5zdGFuY2UucmVsYXldCn0KCnJlc291cmNlICJhd3NfZWlwX2Fzc29jaWF0aW9uIiAicmVsYXkiIHsKICBhbGxvY2F0aW9uX2lkICAgICAgICA9IGF3c19laXAucmVsYXkuaWQKICBuZXR3b3JrX2ludGVyZmFjZV9pZCA9IGF3c19pbnN0YW5jZS5yZWxheS5wcmltYXJ5X25ldHdvcmtfaW50ZXJmYWNlX2lkCiAgcHJpdmF0ZV9pcF9hZGRyZXNzICAgPSAiMTAuMjAuMTEwLjEwIgogIGFsbG93X3JlYXNzb2NpYXRpb24gID0gZmFsc2UKfQoKcmVzb3VyY2UgImF3c19yb3V0ZSIgIm9ucHJlbSIgewogIGZvcl9lYWNoICAgICAgICAgICAgICAgPSB2YXIuYWN0aXZhdGVfb25wcmVtX3JvdXRlcyA/IHZhci5vbnByZW1fcm91dGVfa2V5cyA6IHRvc2V0KFtdKQogIHJvdXRlX3RhYmxlX2lkICAgICAgICAgPSB2YXIubmV0d29ya19oYW5kb2ZmLnN1Ym5ldHNbZWFjaC5rZXldLnJvdXRlX3RhYmxlX2lkCiAgZGVzdGluYXRpb25fY2lkcl9ibG9jayA9ICIxMC4xLjkzLjAvMjQiCiAgbmV0d29ya19pbnRlcmZhY2VfaWQgICA9IGF3c19pbnN0YW5jZS5yZWxheS5wcmltYXJ5X25ldHdvcmtfaW50ZXJmYWNlX2lkCiAgZGVwZW5kc19vbiAgICAgICAgICAgICA9IFthd3NfZWlwX2Fzc29jaWF0aW9uLnJlbGF5LCBhd3NfdnBjX3NlY3VyaXR5X2dyb3VwX2luZ3Jlc3NfcnVsZS53b3JrZXJfZGJdCiAgbGlmZWN5Y2xlIHsKICAgIHByZWNvbmRpdGlvbiB7CiAgICAgIGNvbmRpdGlvbiA9ICgKICAgICAgICBkYXRhLmF3c19yb3V0ZV90YWJsZS5zZWxlY3RlZFtlYWNoLmtleV0udnBjX2lkID09IHZhci5uZXR3b3JrX2hhbmRvZmYudnBjX2lkICYmCiAgICAgICAgYW55dHJ1ZShbZm9yIGEgaW4gZGF0YS5hd3Nfcm91dGVfdGFibGUuc2VsZWN0ZWRbZWFjaC5rZXldLmFzc29jaWF0aW9ucyA6IGEuc3VibmV0X2lkID09IHZhci5uZXR3b3JrX2hhbmRvZmYuc3VibmV0c1tlYWNoLmtleV0uaWRdKQogICAgICApCiAgICAgIGVycm9yX21lc3NhZ2UgPSAiU2VsZWN0ZWQgcm91dGUgdGFibGUgbXVzdCBiZWxvbmcgdG8gdGhlIGhhbmRvZmYgVlBDIGFuZCBiZSBleHBsaWNpdGx5IGFzc29jaWF0ZWQgd2l0aCBpdHMgdGFyZ2V0IHN1Ym5ldC4iCiAgICB9CiAgfQp9Cg=="
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
    save("iac13_vpn_replan_merged.py", Path(__file__).read_bytes())
    assert TF.exists() and S.exists(), "vpn WORKDIR(~/iac11-vpn-20261012-020352)에서 실행하세요 (source/, bin/terraform 필요)"
    for n, h in MANIFEST.items():
        assert hashlib.sha256((S / n).read_bytes()).hexdigest() == h, f"source hash mismatch {n} — STOP"
    summary["checks"]["source_10_files_match_36c18e2a"] = True
    import base64, shutil
    S2 = P / f"source-6847d906-{STAMP}"
    shutil.copytree(S / "terraform/vpn", S2 / "terraform/vpn", ignore=shutil.ignore_patterns(".terraform", "*.tfstate*"))
    newmain = base64.b64decode(PR30_MAIN_B64)
    assert hashlib.sha256(newmain).hexdigest() == PR30_MAIN_SHA256, "PR30 main.tf 해시 불일치 — STOP"
    (S2 / "terraform/vpn/main.tf").write_bytes(newmain)
    for n, h in MANIFEST.items():
        want = PR30_MAIN_SHA256 if n == "terraform/vpn/main.tf" else h
        assert hashlib.sha256((S2 / n).read_bytes()).hexdigest() == want, f"pr30 source hash mismatch {n} — STOP"
    summary["checks"]["merged_6847d906_vpn_10_files_match"] = True
    summary["source_main"] = MERGED_MAIN
    summary["pr30_source_dir"] = str(S2)
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
                   CHECKPOINT_DISABLE="1", TF_DATA_DIR=tempfile.mkdtemp(prefix="fds-iac13-vpn-merged-tfdata-", dir="/tmp"))
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

    cmd = [str(TF), "-chdir=" + str(S2 / "terraform/vpn")]
    call("init", cmd + ["init", "-input=false", "-lockfile=readonly", "-backend-config=backend.hcl.example"], roleenv, timeout=240)
    assert call("workspace", cmd + ["workspace", "show"], roleenv).stdout.decode().strip() == "default"
    tv = json.loads(call("terraform-version", cmd + ["version", "-json"], roleenv).stdout)
    summary["terraform_version"] = tv.get("terraform_version")
    summary["aws_provider"] = (tv.get("provider_selections") or {}).get("registry.terraform.io/hashicorp/aws")
    summary["checks"]["tool_versions"] = summary["terraform_version"] == TF_VERSION and summary["aws_provider"] == AWS_PROVIDER
    assert summary["checks"]["tool_versions"], f"버전 불일치 {summary['terraform_version']} / {summary['aws_provider']} — STOP"
    v = json.loads(call("validate", cmd + ["validate", "-json"], roleenv).stdout)
    assert v["valid"]
    tt = call("terraform-test", cmd + ["test", "-no-color"], roleenv, allowed=(0, 1), timeout=600)
    summary["terraform_test_rc"] = tt.returncode
    summary["terraform_test_line"] = next((ln for ln in reversed(tt.stdout.decode(errors="replace").splitlines()) if "passed" in ln or "failed" in ln), None)
    summary["checks"]["terraform_test_pass"] = tt.returncode == 0
    sl = call("state-list", cmd + ["state", "list"], roleenv).stdout.decode().splitlines()
    managed = [x for x in sl if x.strip() and not x.startswith("data.")]
    summary["state_list_count"] = {"managed": len(managed), "data": len(sl) - len(managed)}
    summary["checks"]["state_managed_count_8"] = len(managed) == EXPECTED_STATE_COUNT

    summary["plan_started_kst"] = kst()
    pl = call("plan", cmd + ["plan", "-input=false", "-lock-timeout=60s", "-detailed-exitcode", "-no-color",
                             "-var-file=" + str(VF), "-out=" + str(P / f"vpn-replan-merged-{STAMP}.tfplan")],
              roleenv, allowed=(0, 2), timeout=300)
    summary["plan_finished_kst"] = kst()
    summary["plan_rc"] = pl.returncode
    summary["plan_line"] = next((ln for ln in pl.stdout.decode(errors="replace").splitlines()
                                 if ln.startswith(("No changes.", "Plan:"))), None)
    show = call("show-json", cmd + ["show", "-json", str(P / f"vpn-replan-merged-{STAMP}.tfplan")], roleenv, stdout_dir=P)
    plan = json.loads(show.stdout)
    summary["plan_sha256"] = hashlib.sha256((P / f"vpn-replan-merged-{STAMP}.tfplan").read_bytes()).hexdigest()
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
        "status", "error", "warnings", "role_arn", "terraform_test_rc", "terraform_test_line", "account_guard", "terraform_version", "aws_provider",
        "state_list_count", "plan_rc", "plan_line", "plan_sha256", "plan_json_sha256",
        "changed_resources", "changed_outputs", "resource_drift", "state_before", "state_after",
        "checks", "checks_failed", "before_keys", "after_keys", "plan_started_kst", "plan_finished_kst",
        "started_kst", "finished_kst", "evidence_tgz", "evidence_tgz_sha256", "evidence_tgz_bytes")},
        ensure_ascii=False, indent=2), flush=True)
    sys.exit(0 if summary["status"] == "NO_CHANGES_PASS" else 1)
