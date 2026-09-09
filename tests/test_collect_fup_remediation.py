"""FUP 보완 수집기의 로컬 fixture 테스트."""

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "collect-fup-01-02-remediation.py"
SPEC = importlib.util.spec_from_file_location("fup_collector", SCRIPT)
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class FupCollectorTests(unittest.TestCase):
    def test_fup02_preserves_originals_and_builds_alias(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {
                "05h_ssh_key_lifecycle_record.md": b"approved 05h\n",
                "05j_review_approval_record.md": b"approved 05j\n",
            }
            current = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
            legacy_values = {name: "0" * 64 for name in files}
            manifest = "".join(
                f"{value}  docs/evidence/P1-ANS-01/{name}\n"
                for name, value in legacy_values.items()
            ).encode()
            files["99_SHA256SUMS.txt"] = manifest
            current["99_SHA256SUMS.txt"] = hashlib.sha256(manifest).hexdigest()
            for name, data in files.items():
                (root / name).write_bytes(data)
            with patch.object(C, "P1_ANS_CURRENT", current), patch.object(C, "P1_ANS_LEGACY", legacy_values):
                payload, report = C.collect_fup02(root)
            self.assertEqual(
                payload["FUP-02/originals/05h_ssh_key_lifecycle_record.md"],
                files["05h_ssh_key_lifecycle_record.md"],
            )
            alias = json.loads(payload["FUP-02/FILENAME_ALIAS.json"])
            self.assertEqual(alias["designated_name"], "05j_reviewer_approver_record.md")
            self.assertEqual(report["past_server_verification"], "NOT_CLAIMED")

    def test_fup01_collects_five_stable_root_owned_files_without_rollback(self):
        state_data = {
            host: json.dumps({"change_id": C.CHANGE_ID, "inventory_hostname": host}).encode()
            for host in C.ROLLBACK_HOSTS
        }
        stat_records = {
            host: {"stat": {
                "checksum": hashlib.sha256(data).hexdigest(), "size": len(data),
                "inode": index + 1, "mtime": 1.0, "ctime": 1.0,
                "mode": "0600", "uid": 0, "gid": 0,
            }}
            for index, (host, data) in enumerate(state_data.items())
        }
        slurp_records = {
            host: {"content": base64.b64encode(data).decode()}
            for host, data in state_data.items()
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            evidence = root / "docs" / "evidence" / C.CHANGE_ID
            evidence.mkdir(parents=True)
            refinalization = evidence / "refinalization.md"
            refinalization.write_bytes(b"fixed record\n")
            with patch.object(C, "REFINALIZATION_SHA256", hashlib.sha256(refinalization.read_bytes()).hexdigest()), patch.object(
                C, "run_ansible_tree", side_effect=[stat_records, slurp_records, stat_records]
            ) as runner:
                payload, report = C.collect_fup01(root, None)
        self.assertEqual(runner.call_count, 3)
        self.assertEqual(report["rollback_execution"], "NOT_RUN")
        self.assertEqual(report["status"], "READY_FOR_IMPORT")
        self.assertEqual(len(report["hosts"]), 5)
        self.assertIn("FUP-01/refinalization/refinalization.md", payload)

    def test_changed_remote_source_is_rejected(self):
        host = C.ROLLBACK_HOSTS[0]
        state = json.dumps({"change_id": C.CHANGE_ID, "inventory_hostname": host}).encode()
        stable = {name: {"stat": {
            "checksum": hashlib.sha256(state).hexdigest(), "size": len(state),
            "inode": 1, "mtime": 1.0, "ctime": 1.0,
            "mode": "0600", "uid": 0, "gid": 0,
        }} for name in C.ROLLBACK_HOSTS}
        changed = json.loads(json.dumps(stable))
        changed[host]["stat"]["mtime"] = 2.0
        slurp = {name: {"content": base64.b64encode(state).decode()} for name in C.ROLLBACK_HOSTS}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs" / "evidence" / C.CHANGE_ID).mkdir(parents=True)
            with patch.object(C, "run_ansible_tree", side_effect=[stable, slurp, changed]):
                with self.assertRaisesRegex(ValueError, "REMOTE_SOURCE_CHANGED"):
                    C.collect_fup01(root, None)


if __name__ == "__main__":
    unittest.main()
