"""Cross-check two mutually exclusive MicroPython boot modes and installer docs.

These checks do not claim a real hardware deployment; they guard against the
previous dangerous documentation contradiction about which main.py to copy.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PicoDeploymentDocsTests(unittest.TestCase):
    def test_two_distinct_entry_points(self):
        self.assertIn('from dashboard_bridge import serve', (ROOT/'main_dashboard.py').read_text())
        self.assertIn('from monitor import main', (ROOT/'main.py').read_text())

    def test_powershell_defaults_dashboard(self):
        text = (ROOT/'INSTALL_PICO.ps1').read_text()
        self.assertIn("[string]$Mode = 'Dashboard'", text)
        self.assertIn("$entrySource = if ($Mode -eq 'Dashboard') { 'main_dashboard.py' } else { 'main.py' }", text)
        self.assertIn("$copySequence += @{ source=$entrySource; target='main.py' }", text)
        self.assertIn("File-SHA256", text)
        self.assertIn("Backing up existing Pico files", text)
        self.assertIn("if ($WhatIfPreference)", text)

    def test_batch_wraps_powershell(self):
        self.assertIn('INSTALL_PICO.ps1', (ROOT/'INSTALL_PICO_WINDOWS.bat').read_text())

    def test_all_docs_name_dashboard_source(self):
        for name in ['README.md','docs/INSTALL.md','docs/OPERATOR.md',
                     'docs/DASHBOARD_PROTOCOL.md','docs/PICO_DEPLOYMENT.md',
                     'START_HERE_DASHBOARD.txt']:
            with self.subTest(name=name):
                t = (ROOT/name).read_text().lower()
                self.assertIn('main_dashboard.py', t)
                self.assertIn('main.py', t)

    def test_manual_generator_contains_correct_mapping(self):
        source = (ROOT/'build_manual.py').read_text()
        self.assertIn('main_dashboard.py', source)
        self.assertIn('Do not install the repository main.py for Chrome mode', source)

if __name__ == '__main__':
    unittest.main()
