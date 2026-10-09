"""Reproduce importlib cache and verify only its directory is excluded."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
from unittest.mock import patch

if os.name == 'nt':
    sys.modules.setdefault('fcntl', types.SimpleNamespace())
path = Path(__file__).with_name('export-app-recovery.py')
spec = importlib.util.spec_from_file_location('export_recovery', path)
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    (work / 'trial.py').write_bytes(b'VALUE = 1\n')
    spec = importlib.util.spec_from_file_location('fixture_trial', work / 'trial.py')
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    assert (work / '__pycache__').is_dir(), 'IMPORT_CACHE_NOT_REPRODUCED'
    with patch.object(export, 'read', side_effect=lambda p: p.read_bytes()):
        rows = export.inventory(work)
        assert rows == [{'file': '__pycache__', 'status': 'EXCLUDED_DERIVED_PYTHON_CACHE'},
                        {'file': 'trial.py', 'bytes': 10, 'sha256': export.sha(b'VALUE = 1\n')}]
        (work / 'unexpected').mkdir()
        try:
            export.inventory(work)
        except ValueError as exc:
            assert str(exc) == 'UNEXPECTED_WORK_ENTRY'
        else:
            raise AssertionError('UNEXPECTED_DIRECTORY_ALLOWED')
        (work / 'unexpected').rmdir()
        with patch.object(Path, 'is_symlink', autospec=True,
                          side_effect=lambda p: p.name == '__pycache__'):
            try:
                export.inventory(work)
            except ValueError as exc:
                assert str(exc) == 'UNEXPECTED_WORK_ENTRY'
            else:
                raise AssertionError('CACHE_SYMLINK_ALLOWED')
print('PASS: import cache reproduced; originals hashed; unexpected directory/cache symlink rejected')
