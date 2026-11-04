"""Local regression checks. No owner credentials, TV calls or remote providers."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import addon_manager
import server_bandwidth
import tvctl


class AddonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.private = patch.object(tvctl, 'PRIVATE', Path(self.temp.name))
        self.private.start()
        tvctl.save_private('tv.json', {'certificate_sha256': 'fixture-device'})
        self.addon = {'transportUrl': 'https://example.invalid/fixture-secret/manifest.json',
                      'manifest': {'id': 'fixture', 'name': 'Fixture', 'version': '1.0.0'},
                      'flags': {'protected': False}}
        self.request = {'nonce': 'fixture-nonce', 'operation': 'install',
                        'expires': time.time() + 60, 'tv_identity': 'fixture-device', 'addon': self.addon}
        tvctl.save_private(addon_manager.PENDING, self.request)

    def tearDown(self):
        self.private.stop()
        self.temp.cleanup()

    def test_install_links_and_rejected_schemes(self):
        self.assertEqual(addon_manager.manifest_url('stremio://example.invalid/manifest.json'),
                         'https://example.invalid/manifest.json')
        for url in ['file:///etc/passwd', 'ftp://example.invalid/manifest.json',
                    'https://user:password@example.invalid/manifest.json', 'javascript:alert(1)']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                addon_manager.manifest_url(url)

    def test_nonce_expiry_and_device_identity(self):
        with self.assertRaises(ValueError):
            addon_manager.pending_request('wrong')
        for key, value in [('expires', 0), ('tv_identity', 'different-device')]:
            tvctl.save_private(addon_manager.PENDING, dict(self.request, **{key: value}))
            with self.assertRaises(ValueError):
                addon_manager.pending_request(self.request['nonce'])

    def test_confirmed_install_remove_and_private_summary(self):
        def report(addons):
            addon_manager.receive_report({'nonce': self.request['nonce'], 'addons': addons, 'error': None})
        with self.assertRaises(ValueError):
            report([])
        report([self.addon])
        summary = addon_manager.summary()
        self.assertNotIn('fixture-secret', json.dumps(summary))
        self.assertEqual(addon_manager.selected_addon(summary[0]['key']), self.addon)
        tvctl.save_private(addon_manager.PENDING, dict(self.request, operation='remove'))
        with self.assertRaises(ValueError):
            report([self.addon])
        report([])
        self.assertEqual(addon_manager.summary(), [])


class BandwidthTests(unittest.TestCase):
    line = ('ESTAB 0 0 192.0.2.10:11470 192.0.2.20:5000 '
            'users:(("server",pid=42,fd=5)) uid:1000 ino:99 bytes_sent:1000 bytes_received:400')

    def test_service_only_and_local_health_exclusion(self):
        foreign = self.line.replace('pid=42', 'pid=999').replace('ino:99', 'ino:100')
        local = self.line.replace('192.0.2.20', '192.0.2.10')
        self.assertEqual(server_bandwidth.parse_counters('\n'.join([self.line, foreign, local]), {42}),
                         {'99': (400, 1000)})

    def test_inactive_services_do_not_scan_host_cgroup(self):
        with patch('server_bandwidth.subprocess.run', return_value=subprocess.CompletedProcess([], 0, '\n\n', '')):
            self.assertEqual(server_bandwidth.server_pids(), set())

    def test_rates_new_connections_and_counter_resets(self):
        values = iter([{'a': (100, 200)}, {'a': (2100, 4200)}, {'a': (10, 20), 'b': (1000, 1000)}])
        clock = iter([0, 2, 4])
        sampler = server_bandwidth.Sampler(lambda: next(values), lambda: next(clock))
        self.assertEqual(sampler.sample()['receive_bps'], 0)
        result = sampler.sample()
        self.assertEqual((result['receive_bps'], result['send_bps']), (1000, 2000))
        result = sampler.sample()
        self.assertEqual((result['receive_bps'], result['send_bps']), (500, 500))


if __name__ == '__main__':
    unittest.main()
