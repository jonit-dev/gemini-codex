"""The gateway must identify the installed CLI, since Argon rejects IDE clients."""
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class CLIIdentity(unittest.TestCase):
    def identity(self):
        self.assertTrue((ROOT / 'cli_identity.py').is_file(), 'Gateway CLI identity support is missing')
        return runpy.run_path(str(ROOT / 'cli_identity.py'))['cli_user_agent']

    def test_installed_version_and_consumer_identity(self):
        identity = self.identity()
        with tempfile.TemporaryDirectory() as directory:
            agy = Path(directory) / 'agy'
            agy.write_text('#!/bin/sh\necho 1.4.0\n')
            agy.chmod(0o700)
            with patch.dict(os.environ, PATH=directory), patch('platform.system', return_value='Linux'), patch('platform.machine', return_value='x86_64'):
                self.assertEqual(identity(), 'antigravity/cli/1.4.0 (aidev_client; os_type=linux; arch=amd64; auth_method=consumer)')
                agy.unlink()
                self.assertIn('/1.4.0 ', identity())

    def test_bad_version_fails_instead_of_using_ide_identity(self):
        identity = self.identity()
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '1.4.0\nInjected: header', '')):
            with self.assertRaisesRegex(RuntimeError, 'version'):
                identity()

    def test_missing_cli_has_actionable_error(self):
        identity = self.identity()
        with patch('subprocess.run', side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, 'agy'):
                identity()
