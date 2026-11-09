import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import quickstart

class QuickstartTests(unittest.TestCase):
    def report(self, ready=True):
        return {'ready':ready, 'runtime_checks':{'node':{'path':'node'}}}

    def test_ready_install_is_reused(self):
        with patch.object(quickstart.environment, 'inspect', return_value=self.report()), patch.object(quickstart.environment, 'setup') as setup:
            self.assertEqual(quickstart.run(),0)
            setup.assert_not_called()

    def test_missing_runtime_stops_before_browser(self):
        with patch.object(quickstart.environment, 'inspect', return_value=self.report(False)), patch.object(quickstart.environment, 'setup', return_value=self.report(False)), patch.object(quickstart.subprocess, 'run') as run:
            self.assertEqual(quickstart.run(browser=True),1)
            run.assert_not_called()

    def test_failed_browser_stops_before_smoke(self):
        with patch.object(quickstart.environment, 'inspect', return_value=self.report()), patch.object(quickstart.subprocess, 'run') as run:
            run.return_value.returncode=7
            self.assertEqual(quickstart.run(smoke=True),7)
            self.assertEqual(run.call_count,1)
