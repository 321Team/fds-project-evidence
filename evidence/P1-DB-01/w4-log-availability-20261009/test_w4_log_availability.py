import importlib.util
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('w4-log-availability.py'))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class ScanTests(unittest.TestCase):
    def setUp(self):
        # Windows fixtures exercise parsing/bounds, not Linux nofollow semantics.
        # Production collector retains mandatory O_NOFOLLOW and O_NONBLOCK.
        if collector.os.name == 'nt':
            for name in ('O_NOFOLLOW', 'O_NONBLOCK'):
                mock = patch.object(collector.os, name, 0, create=True)
                mock.start()
                self.addCleanup(mock.stop)

    def test_timestamp_window_without_payload_export(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '0.log'
            p.write_bytes(b'2026-10-08T11:26:48Z stdout F PRIVATE_BEFORE\n'
                          b'2026-10-08T11:26:49.000000000Z stderr F PRIVATE_WINDOW\n'
                          b'2026-10-08T11:27:52+00:00 stdout F PRIVATE_END\n'
                          b'2026-10-08T11:27:53Z stdout F PRIVATE_AFTER\n')
            row, used = collector.scan(p, 4096, time.monotonic()+2)
            self.assertEqual(row['records_in_w4_interval'], 2)
            self.assertEqual(row['status'], 'COMPLETE')
            self.assertEqual(used, p.stat().st_size)
            self.assertNotIn('PRIVATE_', str(row))

    def test_truncation_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '0.log'
            p.write_bytes(b'x'*256)
            row, used = collector.scan(p, 64, time.monotonic()+2)
            self.assertEqual(used, 64)
            self.assertEqual(row['status'], 'PARTIAL_OR_CHANGED')

    def test_compressed_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '0.log.gz'
            p.write_bytes(b'not-a-log')
            row, used = collector.scan(p, 4096, time.monotonic()+2)
            self.assertEqual(row['status'], 'SKIPPED_COMPRESSED')
            self.assertEqual(used, 0)

    def test_expired_deadline(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '0.log'
            p.write_bytes(b'x')
            row, used = collector.scan(p, 4096, time.monotonic()-1)
            self.assertEqual(used, 0)
            self.assertEqual(row['status'], 'PARTIAL_OR_CHANGED')

if __name__ == '__main__':
    unittest.main()
