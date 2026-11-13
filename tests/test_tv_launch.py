"""Launch recovery checks with mocked hosting and TV control; no device calls."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tv_control_panel import Backend


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.backend = Backend()
        self.backend.start = Mock()
        self.backend.wait_ready = Mock(return_value=True)
        self.backend.bind = Mock(return_value='192.0.2.10')
        self.request = patch('tv_control_panel.tvctl.request').start()
        self.launch = patch('tv_control_panel.tvctl.launch').start()
        patch('tv_control_panel.time.sleep').start()
        self.addCleanup(patch.stopall)

    def state(self, input_name):
        return {'CURRENT_INPUT': {'NAME': input_name}}

    def test_existing_smartcast_opens_directly_without_home_key(self):
        self.request.return_value = self.state('SMARTCAST')
        message = self.backend.open_tv()
        self.backend.start.assert_called_once_with()
        self.request.assert_called_once_with('GET', '/state_extended')
        self.launch.assert_called_once_with('http://192.0.2.10:8099/stremio/#/')
        self.assertIn('request accepted', message)

    def test_hdmi_waits_for_confirmed_smartcast_before_launch(self):
        self.request.side_effect = [self.state('HDMI-3'), {},
                                    self.state('HDMI-3'), self.state('SMARTCAST')]
        def launch(_):
            self.assertEqual(self.request.call_count, 4)
        self.launch.side_effect = launch
        self.backend.open_tv()
        self.assertEqual(self.request.call_args_list[1].args,
                         ('PUT', '/key_command/', {'KEYLIST': [
                             {'CODESET': 4, 'CODE': 3, 'ACTION': 'KEYPRESS'}]}))
        self.launch.assert_called_once()

    def test_failed_switch_does_not_send_launch(self):
        self.request.return_value = self.state('HDMI-3')
        with self.assertRaisesRegex(RuntimeError, 'did not switch'):
            self.backend.open_tv()
        self.launch.assert_not_called()

    def test_unready_host_does_not_contact_tv(self):
        self.backend.wait_ready.return_value = False
        with self.assertRaisesRegex(RuntimeError, 'still starting'):
            self.backend.open_tv()
        self.request.assert_not_called()
        self.launch.assert_not_called()

    def test_unreachable_or_rejecting_tv_reports_failure(self):
        for error in (OSError('fixture offline'), RuntimeError('TV returned non-JSON (HTTP 400)')):
            with self.subTest(error=type(error).__name__):
                self.request.side_effect = error
                with self.assertRaises(RuntimeError):
                    self.backend.open_tv()
                self.launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
