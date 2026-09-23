import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'FDS_Ansible_Export_Fix_Start_v1_0'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, KIT / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


preflight = module('preflight', 'preflight.py')
readiness = module('readiness', 'check-readiness.py')
E = json.loads((KIT / 'EXPECTED.json').read_text())
LIVE = json.loads((ROOT / 'LIVE_SNAPSHOT.json').read_text())
ORDER = ('pr', 'run', 'jobs', 'queued', 'active')


class PreflightTests(unittest.TestCase):
    def test_current_exact_get_snapshot(self):
        preflight.validate(E, *(LIVE[k] for k in ORDER))

    def test_target_changes_and_incomplete_queries_rejected(self):
        cases = [
            ('pr', ('number',), 20), ('pr', ('draft',), False), ('pr', ('state',), 'closed'),
            ('pr', ('head', 'sha'), '0'*40), ('pr', ('head', 'ref'), 'old-branch'),
            ('pr', ('head', 'repo', 'full_name'), 'foreign/repo'), ('pr', ('base','ref'), 'other'),
            ('run', ('id',), 35139314896), ('run', ('run_attempt',), 2),
            ('run', ('head_sha',), '0'*40), ('run', ('head_branch',), 'other'),
            ('run', ('event',), 'pull_request_target'), ('run', ('status',), 'completed'),
            ('run', ('conclusion',), 'success'), ('run', ('path',), 'other.yml'),
            ('run', ('head_repository','full_name'), 'foreign/repo'),
            ('jobs', ('total_count',), 2), ('jobs', ('jobs',0,'id'), 104963520513),
            ('jobs', ('jobs',0,'run_id'), 35139314896), ('jobs', ('jobs',0,'run_attempt'), 2),
            ('jobs', ('jobs',0,'head_sha'), '0'*40), ('jobs', ('jobs',0,'name'), 'deploy'),
            ('jobs', ('jobs',0,'status'), 'in_progress'), ('jobs', ('jobs',0,'runner_id'), 7),
            ('jobs', ('jobs',0,'runner_name'), 'assigned'), ('jobs', ('jobs',0,'labels'), ['self-hosted']),
            ('jobs', ('jobs',0,'labels'), E['labels']+[E['labels'][0]]),
            ('jobs', ('jobs',0,'check_run_url'), 'https://example.invalid/check'),
            ('queued', ('total_count',), 101), ('queued', ('workflow_runs',), []),
            ('queued', ('workflow_runs',0,'id'), 35139314896),
            ('active', ('total_count',), 1), ('active', ('workflow_runs',), [{'id':1}]),
            ('jobs', ('total_count',), True), ('run', ('run_attempt',), True),
        ]
        for area, keys, value in cases:
            with self.subTest(area=area, keys=keys):
                data = copy.deepcopy(LIVE); target = data[area]
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value
                with self.assertRaises(preflight.Stop):
                    preflight.validate(E, *(data[k] for k in ORDER))
        self.assertEqual(len(cases), 35)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(preflight.Stop):
            preflight.decode('{"id":1,"id":2}')

    def test_get_only_collect_and_state_failure(self):
        for bad in (False, True):
            values = copy.deepcopy(LIVE)
            if bad:
                values['run']['status'] = 'completed'
            responses = [subprocess.CompletedProcess([], 0, json.dumps(values[k]).encode(), b'') for k in ORDER]
            calls = []
            def fake(args, **kwargs):
                calls.append(args)
                self.assertEqual(args[args.index('--method')+1], 'GET')
                self.assertNotIn('GH_DEBUG', kwargs['env'])
                return responses[len(calls)-1]
            with tempfile.TemporaryDirectory() as tmp, patch.object(preflight.shutil,'which',return_value='/mock/gh'), patch.object(preflight.subprocess,'run',side_effect=fake), patch.dict(os.environ, {'GH_DEBUG':'api'}):
                if bad:
                    with self.assertRaises(preflight.Stop): preflight.collect(E, Path(tmp))
                else:
                    preflight.collect(E, Path(tmp))
                self.assertEqual(len(calls), 5)

    def test_transport_error_stops_before_next_get(self):
        p = subprocess.CompletedProcess([], 1, b'', b'synthetic diagnostic')
        with tempfile.TemporaryDirectory() as tmp, patch.object(preflight.shutil,'which',return_value='/mock/gh'), patch.object(preflight.subprocess,'run',return_value=p) as api:
            with self.assertRaises(preflight.Stop): preflight.collect(E, Path(tmp))
            self.assertEqual(api.call_count, 1)
            self.assertEqual(list(Path(tmp).iterdir()), [])


class ReadinessTests(unittest.TestCase):
    def test_receipt_and_image_binding(self):
        prepared = {'status':'PASS_PREPARE','repository':E['repository'],'runner_version':'2.337.0',
                    'bundle_sha256':E['runner_bundle_sha256'],'image_id':E['image_id'],'container_cleanup':'REMOVED'}
        image = {'Id':E['image_id'],'Architecture':'amd64','Os':'linux','Config':{'Labels':{'io.fds.bundle':E['runner_bundle_sha256']}}}
        readiness.validate_prepared(prepared); readiness.validate_image([image])
        for field in prepared:
            with self.subTest(prepared_field=field):
                changed=copy.deepcopy(prepared); changed[field]='mismatch'
                with self.assertRaises(RuntimeError): readiness.validate_prepared(changed)
        for field in ('Id','Architecture','Os'):
            with self.subTest(image_field=field):
                changed=copy.deepcopy(image); changed[field]='mismatch'
                with self.assertRaises(RuntimeError): readiness.validate_image([changed])
        changed=copy.deepcopy(image); changed['Config']['Labels']['io.fds.bundle']='wrong'
        with self.assertRaises(RuntimeError): readiness.validate_image([changed])
        for values in ([],[image,image]):
            with self.assertRaises(RuntimeError): readiness.validate_image(values)

    def test_wrong_identity_has_no_file_or_podman_access(self):
        with patch.object(readiness.os,'getuid',return_value=0), patch.object(readiness.os,'open') as opened, patch.object(readiness.subprocess,'run') as process:
            with self.assertRaises(RuntimeError): readiness.check()
            opened.assert_not_called(); process.assert_not_called()

    def test_linked_prepared_path_never_reads_or_inspects_image(self):
        with patch.object(readiness.os,'getuid',return_value=1001), patch.object(readiness.os,'geteuid',return_value=1001), patch.object(readiness.os,'getgid',return_value=1002), patch.object(readiness.pwd,'getpwuid') as user, patch.object(readiness.socket,'gethostname',return_value='cicd-runner01'), patch.object(readiness.Path,'is_symlink',return_value=True), patch.object(readiness.os,'open') as opened, patch.object(readiness.subprocess,'run') as process:
            user.return_value.pw_name='ansible-verify'
            with self.assertRaises(RuntimeError): readiness.check()
            opened.assert_not_called(); process.assert_not_called()

    def test_wrong_receipt_never_inspects_image(self):
        from types import SimpleNamespace
        import stat
        raw=b'{"status":"FAIL"}'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'PREPARED.json'; p.write_bytes(raw)
            info=SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_nlink=1,st_uid=1001,st_size=len(raw))
            with patch.object(readiness,'PREPARED',p), patch.object(readiness.os,'getuid',return_value=1001), patch.object(readiness.os,'geteuid',return_value=1001), patch.object(readiness.os,'getgid',return_value=1002), patch.object(readiness.pwd,'getpwuid') as user, patch.object(readiness.socket,'gethostname',return_value='cicd-runner01'), patch.object(readiness.os,'chdir'), patch.object(readiness.os,'fstat',return_value=info), patch.object(readiness.subprocess,'run') as process:
                user.return_value.pw_name='ansible-verify'
                with self.assertRaises(RuntimeError): readiness.check()
                process.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
