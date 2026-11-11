"""Subtitle defaults use only local fixture files; no TV or service operations."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import playback_preferences
import serve_lab
import tv_control_panel
import tvctl


class PlaybackPreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.private = patch.object(tvctl, 'PRIVATE', Path(self.temp.name))
        self.private.start()

    def tearDown(self):
        self.private.stop()
        self.temp.cleanup()

    def test_default_and_persistence_without_services(self):
        self.assertEqual(playback_preferences.read(), {'subtitles_default_on': True})
        backend = tv_control_panel.Backend()
        with patch.object(backend, 'service', side_effect=AssertionError('No service changes')):
            for enabled in (False, True, False):
                backend.subtitles(enabled)
                self.assertEqual(playback_preferences.read()['subtitles_default_on'], enabled)
        path = tvctl.PRIVATE / playback_preferences.FILE
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        before = path.read_bytes()
        for invalid in (None, 1, 'false'):
            with self.assertRaises(ValueError):
                backend.subtitles(invalid)
        self.assertEqual(path.read_bytes(), before)

    def test_read_only_http_endpoint_and_live_file_updates(self):
        tvctl.save_private('tv.json', {'ip': '192.0.2.20'})
        servers = []
        def capture(address, handler):
            server = ThreadingHTTPServer(address, handler)
            servers.append(server)
            return server
        with patch.object(sys, 'argv', ['serve_lab', '--bind', '127.0.0.1', '--port', '0']), \
                patch.object(serve_lab, 'ThreadingHTTPServer', side_effect=capture):
            thread = threading.Thread(target=serve_lab.main)
            thread.start()
            try:
                # Wait for binding without touching an owner's running service.
                import time
                for _ in range(100):
                    if servers:
                        break
                    time.sleep(.01)
                self.assertTrue(servers)
                url = f'http://127.0.0.1:{servers[0].server_port}/playback-preferences'
                for enabled in (True, False, True):
                    playback_preferences.set_subtitles(enabled)
                    with urllib.request.urlopen(url, timeout=2) as response:
                        self.assertEqual(json.load(response), {'subtitles_default_on': enabled})
                        self.assertEqual(response.headers['Cache-Control'], 'no-store')
                        self.assertIsNone(response.headers.get('Access-Control-Allow-Origin'))
                for headers, expected in (({}, 403), ({'Origin': 'http://127.0.0.1:0'}, 404)):
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(urllib.request.Request(url, data=b'{}', headers=headers), timeout=2)
                    self.assertEqual(error.exception.code, expected)
                self.assertTrue(playback_preferences.read()['subtitles_default_on'])
            finally:
                if servers:
                    servers[0].shutdown()
                thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
