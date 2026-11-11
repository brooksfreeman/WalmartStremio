"""Address-change regression checks using synthetic state and mocked services."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tv_control_panel
import tv_network
import tvctl


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name)
        private = patch.object(tvctl, 'PRIVATE', self.private)
        private.start()
        self.addCleanup(private.stop)
        verify = patch('tv_network.verify_tv')
        self.verify = verify.start()
        self.addCleanup(verify.stop)
        self.pc, self.old, self.new = '192.0.2.10', '192.0.2.20', '192.0.2.30'
        self.tv = {'ip': self.old, 'certificate_sha256': 'fixture-pin', 'model': 'fixture'}
        self.peers = ['127.0.0.1', '::1', self.pc, self.old]
        self.source = ('if (' + json.dumps(self.peers) + '.indexOf(peer) < 0) { deny(); }').encode()
        self.path = self.private / 'stremio-server/server.js'
        self.path.parent.mkdir()
        self.path.write_bytes(self.source)
        self.record = {'patched_sha256': hashlib.sha256(self.source).hexdigest(),
                       'allowed_ips': self.peers, 'frontend_origin': f'http://{self.pc}:8099',
                       'package_sha256': 'fixture-package'}
        tvctl.save_private('tv.json', self.tv)
        tvctl.save_private('stremio-server-preparation.json', self.record)
        self.backend = tv_control_panel.Backend()
        self.backend.bind = Mock(return_value=self.pc)
        self.backend.healthy = Mock(return_value=True)

    def services(self, running=(), fail_start=False):
        calls = []
        failed = False
        def service(verb, *names, check=True):
            nonlocal failed
            calls.append((verb, names))
            if fail_start and verb == 'start' and not failed:
                failed = True
                raise RuntimeError('fixture failure')
            state = 'active' if names[0] in running else 'inactive'
            return subprocess.CompletedProcess([], 0, state, '')
        self.backend.service = Mock(side_effect=service)
        return calls

    def assert_original(self):
        self.assertEqual(tvctl.read_private('tv.json'), self.tv)
        self.assertEqual(tvctl.read_private('stremio-server-preparation.json'), self.record)
        self.assertEqual(self.path.read_bytes(), self.source)

    def test_bad_input_rejected_before_network_or_service_work(self):
        self.services()
        for value in ('', 'http://192.0.2.30', '192.0.2.30:7345', '::1',
                      '127.0.0.1', '0.0.0.0', '224.0.0.1', '255.255.255.255', self.pc):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                self.backend.update_tv_ip(value)
        self.verify.assert_not_called()
        self.backend.service.assert_not_called()
        self.assert_original()

    def test_certificate_or_connection_failure_leaves_everything_untouched(self):
        self.services()
        self.verify.side_effect = RuntimeError('unverified device')
        with self.assertRaises(RuntimeError):
            self.backend.update_tv_ip(self.new)
        self.backend.service.assert_not_called()
        self.assert_original()

    def test_stopped_stays_stopped_and_all_address_consumers_update(self):
        calls = self.services()
        self.backend.update_tv_ip(' ' + self.new + ' ')
        self.verify.assert_called_once_with(self.new, 'fixture-pin')
        self.assertFalse(any(verb == 'start' for verb, _ in calls))
        self.assertEqual(tvctl.read_private('tv.json'), dict(self.tv, ip=self.new))
        record = tvctl.read_private('stremio-server-preparation.json')
        self.assertEqual(record['allowed_ips'], ['127.0.0.1', '::1', self.pc, self.new])
        self.assertEqual(record['patched_sha256'], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertNotIn(self.old.encode(), self.path.read_bytes())
        self.assertEqual(record['package_sha256'], 'fixture-package')
        backups = list(self.private.glob('tv-network-backup-*.json'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text())['tv'], self.tv)
        for path in (backups[0], self.path, self.private / 'tv.json'):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_online_services_restart_in_order_without_enablement_changes(self):
        calls = self.services(('lab', 'engine', 'watch'))
        self.backend.update_tv_ip(self.new)
        self.assertEqual(calls[3:], [('stop', ('watch', 'lab', 'engine')),
                                    ('start', ('lab', 'engine')), ('start', ('watch',))])

    def test_disabled_watcher_is_not_started(self):
        calls = self.services(('lab', 'engine'))
        self.backend.update_tv_ip(self.new)
        self.assertEqual([names for verb, names in calls if verb == 'start'], [('lab', 'engine')])

    def test_failure_restores_original_files_and_running_services(self):
        calls = self.services(('lab', 'engine', 'watch'), fail_start=True)
        with self.assertRaisesRegex(RuntimeError, 'previous address and server state were restored'):
            self.backend.update_tv_ip(self.new)
        self.assert_original()
        self.assertEqual(calls[-2:], [('start', ('lab', 'engine')), ('start', ('watch',))])

    def test_partial_write_failure_restores_all_files(self):
        self.services()
        original = tvctl.save_private
        failed = False
        def save(name, value):
            nonlocal failed
            if name == 'tv.json' and not failed:
                failed = True
                raise OSError('fixture write failure')
            original(name, value)
        with patch('tvctl.save_private', side_effect=save):
            with self.assertRaisesRegex(RuntimeError, 'were restored'):
                self.backend.update_tv_ip(self.new)
        self.assert_original()

    def test_recovery_failure_is_reported(self):
        self.services(('lab', 'engine'))
        self.backend.healthy.return_value = False
        with patch('tv_control_panel.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'recovery needs attention'):
                self.backend.update_tv_ip(self.new)
        self.assert_original()

    def test_engine_tampering_or_stale_allowlist_is_rejected_before_stop(self):
        self.services()
        for key, value in [('patched_sha256', 'wrong'), ('allowed_ips', ['wrong'])]:
            tvctl.save_private('stremio-server-preparation.json', dict(self.record, **{key: value}))
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                self.backend.update_tv_ip(self.new)
        self.backend.service.assert_not_called()

    def test_same_address_only_verifies_without_stopping(self):
        self.services(('lab', 'engine', 'watch'))
        self.backend.update_tv_ip(self.old)
        self.backend.service.assert_not_called()
        self.assert_original()


class CertificateTests(unittest.TestCase):
    def test_certificate_checked_without_sending_request_or_reading_credentials(self):
        connection = Mock()
        connection.sock.getpeercert.return_value = b'fixture-certificate'
        fingerprint = hashlib.sha256(b'fixture-certificate').hexdigest()
        with patch('tv_network.http.client.HTTPSConnection', return_value=connection), \
                patch('tvctl.read_private', side_effect=AssertionError('No credentials needed')):
            tv_network.verify_tv('192.0.2.30', fingerprint)
            connection.request.assert_not_called()
            with self.assertRaisesRegex(RuntimeError, 'different device'):
                tv_network.verify_tv('192.0.2.30', 'wrong')
            connection.connect.side_effect = OSError('fixture offline')
            with self.assertRaisesRegex(RuntimeError, 'Could not reach'):
                tv_network.verify_tv('192.0.2.30', fingerprint)
        self.assertEqual(connection.close.call_count, 3)


if __name__ == '__main__':
    unittest.main()
