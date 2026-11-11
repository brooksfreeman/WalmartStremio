#!/usr/bin/env python3
"""Local desktop controls for the owner's PC-hosted Stremio setup."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

import home_navigation
import tvctl
import addon_manager
import tv_network
import playback_preferences
from server_bandwidth import Sampler

UNITS = {name: f'vizio-stremio-{name}.service' for name in ('lab', 'engine', 'watch')}


class Backend:
    def command(self, *args, check=True):
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if check and result.returncode:
            raise RuntimeError('The service operation did not complete.')
        return result

    def service(self, verb, *names, check=True):
        return self.command('systemctl', '--user', verb, *(UNITS[n] for n in names), check=check)

    def bind(self):
        unit = (tvctl.ROOT / 'config/systemd' / UNITS['lab']).read_text()
        found = re.search(r'--bind ([0-9.]+)', unit)
        if not found:
            raise RuntimeError('Server address is not configured.')
        return str(ipaddress.IPv4Address(found.group(1)))

    def healthy(self, port, path):
        try:
            with urllib.request.urlopen(f'http://{self.bind()}:{port}{path}', timeout=2) as response:
                value = json.loads(response.read(65536))
                return response.status == 200 and isinstance(value, dict) and (port != 8099 or value.get('ok') is True)
        except (OSError, ValueError, RuntimeError):
            return False

    def status(self):
        active = {n: self.service('is-active', n, check=False).stdout.strip() == 'active' for n in UNITS}
        enabled = {n: self.service('is-enabled', n, check=False).stdout.strip() == 'enabled' for n in UNITS}
        linger = self.command('loginctl', 'show-user', str(os.getuid()), '-p', 'Linger', '--value', check=False).stdout.strip() == 'yes'
        return {'host_online': active['lab'] and self.healthy(8099, '/health'),
                'engine_online': active['engine'] and self.healthy(11470, '/settings'),
                'server_running': active['lab'] or active['engine'],
                'shortcut_enabled': home_navigation.watchfree_enabled(),
                'shortcut_running': active['watch'],
                'start_at_boot': enabled['lab'] and enabled['engine'] and linger,
                'sleep_blocked': self.command('systemctl', '--user', 'is-active', '--quiet', 'vizio-stremio-awake.service', check=False).returncode == 0,
                'linger': linger, 'enabled': enabled, 'addons': addon_manager.summary(),
                'tv_ip': tvctl.read_private('tv.json')['ip'], 'pc_ip': self.bind(),
                **playback_preferences.read()}

    def subtitles(self, enabled):
        playback_preferences.set_subtitles(enabled)

    def update_tv_ip(self, value):
        change = tv_network.Change(value, self.bind())
        if change.ip == change.tv['ip']:
            return
        change.backup()
        running = [n for n in UNITS if self.service('is-active', n, check=False).stdout.strip()
                   in ('active', 'activating', 'reloading')]

        def resume():
            hosts = [n for n in ('lab', 'engine') if n in running]
            if hosts:
                self.service('start', *hosts)
                for _ in range(20):
                    if all(self.healthy(8099, '/health') if n == 'lab' else
                           self.healthy(11470, '/settings') for n in hosts):
                        break
                    time.sleep(.3)
                else:
                    raise RuntimeError('The server did not restart.')
            if 'watch' in running:
                self.service('start', 'watch')

        try:
            self.stop()
            change.apply()
            resume()
        except Exception:
            try:
                self.stop()
                change.restore()
                resume()
            except Exception:
                raise RuntimeError('The address update failed and recovery needs attention. A private backup was saved; try Start / repair.') from None
            raise RuntimeError('The address update failed. The previous address and server state were restored.') from None

    def boot_enabled(self):
        return all(self.service('is-enabled', n, check=False).stdout.strip() == 'enabled' for n in ('lab', 'engine'))

    def shortcut(self, enabled):
        # Stop observation before changing its settings; initial state never launches.
        self.service('stop', 'watch')
        self.command(sys.executable, str(tvctl.ROOT / 'scripts/configure_home.py'),
                     'enable-watchfree' if enabled else 'disable-watchfree')
        self.service('enable' if enabled and self.boot_enabled() else 'disable', 'watch')
        if enabled:
            self.service('start', 'lab', 'engine')
            self.service('start', 'watch')

    def boot(self, enabled):
        if enabled:
            self.command('loginctl', 'enable-linger', str(os.getuid()))
        self.service('enable' if enabled else 'disable', 'lab', 'engine')
        self.service('enable' if enabled and home_navigation.watchfree_enabled() else 'disable', 'watch')

    def start(self, restart=False):
        if restart:
            self.service('stop', 'watch')
        self.service('restart' if restart else 'start', 'lab', 'engine')
        if home_navigation.watchfree_enabled():
            self.service('start', 'watch')

    def stop(self):
        self.service('stop', 'watch', 'lab', 'engine')

    def open_tv(self):
        self.start()
        if not self.wait_ready():
            raise RuntimeError('The server is still starting. Try again in a few seconds.')
        tvctl.launch(f'http://{self.bind()}:8099/stremio/#/')

    def wait_ready(self):
        for _ in range(12):
            if self.healthy(8099, '/health') and self.healthy(11470, '/settings'):
                return True
            time.sleep(.3)
        return False

    def manage_addons(self, operation, addon=None):
        self.start()
        if not self.wait_ready():
            raise RuntimeError('The server is not ready. Try Start / repair.')
        return addon_manager.operate(self.bind(), operation, addon)

    def install_addon(self, url):
        self.start()
        try:
            addon = addon_manager.fetch_addon(url)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from None
        return self.manage_addons('install', addon)

    def remove_addon(self, key):
        return self.manage_addons('remove', addon_manager.selected_addon(key))


def desktop(screenshot=None, tab='overview'):
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gio, GLib, Gdk

    class App(Gtk.Application):
        def __init__(self):
            super().__init__(application_id='local.owner.StremioTV', flags=Gio.ApplicationFlags.FLAGS_NONE)
            self.backend = Backend()
            self.pool = ThreadPoolExecutor(max_workers=1)
            self.metric_pool = ThreadPoolExecutor(max_workers=1)
            self.sampler = Sampler()
            self.samples = deque(maxlen=121)
            self.metric_busy = False
            self.busy = False
            self.updating = False
            self.controls = []

        def label(self, text, style=None):
            item = Gtk.Label(label=text, xalign=0)
            item.set_line_wrap(True)
            if style:
                item.get_style_context().add_class(style)
            return item

        def card(self):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            box.get_style_context().add_class('card')
            self.body.pack_start(box, False, False, 0)
            return box

        def button(self, title, callback, primary=False, addon=False):
            button = Gtk.Button(label=title)
            if primary:
                button.get_style_context().add_class('primary')
            button.connect('clicked', lambda _: self.perform(callback, addon=addon))
            self.controls.append(button)
            return button

        def toggle(self, card, title, description, callback):
            row = Gtk.Box(spacing=20)
            text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            text.pack_start(self.label(title, 'section'), False, False, 0)
            text.pack_start(self.label(description, 'muted'), False, False, 0)
            row.pack_start(text, True, True, 0)
            switch = Gtk.Switch(valign=Gtk.Align.CENTER)
            switch.connect('state-set', lambda _, value: self.switch_changed(callback, value))
            row.pack_end(switch, False, False, 0)
            card.pack_start(row, False, False, 0)
            self.controls.append(switch)
            return switch

        def switch_changed(self, callback, value):
            if self.updating:
                return False
            if self.busy:
                return True
            self.perform(lambda: callback(value))
            return True

        def do_activate(self):
            if hasattr(self, 'window'):
                self.window.present()
                return
            css = Gtk.CssProvider()
            css.load_from_data(b'''
                window { background: #14121d; color: #f5f2ff; }
                .title { font-size: 30px; font-weight: bold; }
                .section { font-size: 16px; font-weight: bold; }
                .muted { color: #bbb4cd; font-size: 13px; }
                .card { background: #211d2d; border: 1px solid #393247; border-radius: 15px; padding: 16px; }
                .status { font-size: 23px; font-weight: bold; }
                .online { color: #81e3b6; }
                .offline { color: #ffc083; }
                notebook, notebook > stack, scrolledwindow, viewport { background: #14121d; color: #f5f2ff; }
                notebook > header { background: #211d2d; border-color: #393247; }
                notebook tab { background: #211d2d; color: #bbb4cd; padding: 8px 18px; }
                notebook tab:checked { background: #493360; color: #ffffff; }
                entry { background: #211d2d; color: #f5f2ff; border: 1px solid #69577d; border-radius: 8px; padding: 10px; }
                list.addons { background: #211d2d; color: #f5f2ff; }
                list.addons row { padding: 0; border-bottom: 1px solid #393247; }
                scrollbar trough { background: #14121d; }
                button { background: #342d45; color: #f5f2ff; border: 1px solid #51445f; border-radius: 8px; padding: 9px 12px; box-shadow: none; text-shadow: none; }
                button:hover { background: #49395e; }
                button.primary { background: #7950d7; border-color: #a782f3; }
                button.delete { background: #492b39; border-color: #94536c; color: #ffd6df; padding: 4px 10px; }
                button.delete:hover { background: #633346; }
                button:disabled { color: #8d849b; border-color: #393247; }
                switch { background: #4b425b; border: 1px solid #69577d; border-radius: 15px; min-width: 48px; min-height: 26px; }
                switch:checked { background: #8860dc; }
                switch slider { background: #f5f2ff; border: 2px solid #d9c9fa; border-radius: 13px; min-width: 20px; min-height: 20px; }
            ''')
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.window = Gtk.ApplicationWindow(application=self, title='Stremio TV')
            self.window.set_default_size(760, 940)
            self.window.set_resizable(True)
            self.window.set_icon_from_file(str(tvctl.ROOT / 'config/icons/stremio-tv.svg'))
            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=18)
            self.window.add(outer)
            outer.pack_start(self.label('Stremio TV', 'title'), False, False, 0)
            outer.pack_start(self.label('Your PC hosts it. Your remote opens it.', 'muted'), False, False, 0)
            tabs = Gtk.Notebook()
            outer.pack_start(tabs, True, True, 0)
            overview = Gtk.ScrolledWindow()
            overview.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin=12)
            overview.add(self.body)
            tabs.append_page(overview, Gtk.Label(label='Overview'))
            server = self.card()
            self.server_status = self.label('Checking server…', 'status')
            self.server_detail = self.label('Checking the interface and streaming engine.', 'muted')
            server.pack_start(self.server_status, False, False, 0)
            server.pack_start(self.server_detail, False, False, 0)
            buttons = Gtk.Box(spacing=8, homogeneous=True)
            for title, callback in [('Start / repair', lambda: self.backend.start(True)), ('Stop server', self.backend.stop)]:
                buttons.pack_start(self.button(title, callback), True, True, 0)
            server.pack_start(buttons, False, False, 0)
            bandwidth = self.card()
            bandwidth.pack_start(self.label('Server bandwidth', 'section'), False, False, 0)
            self.rates = self.label('Receive —   ·   Send —', 'section')
            bandwidth.pack_start(self.rates, False, False, 0)
            self.graph = Gtk.DrawingArea()
            self.graph.set_size_request(540, 130)
            self.graph.connect('draw', self.draw_bandwidth)
            bandwidth.pack_start(self.graph, False, False, 0)
            bandwidth.pack_start(self.label('Green: receive · Purple: send · Last 2 minutes', 'muted'), False, False, 0)
            scope = self.label('Estimated server TCP traffic. Other apps and UDP are excluded.', 'muted')
            scope.set_tooltip_text('Measures socket payload counters for the interface host and streaming engine. Closed sockets between samples may be missed. No media names or connection history are saved.')
            bandwidth.pack_start(scope, False, False, 0)
            remote = self.card()
            self.shortcut_switch = self.toggle(remote, 'WatchFree opens Stremio', 'Turn off to use WatchFree normally. Home stays normal.', self.backend.shortcut)
            self.remote_detail = self.label('Checking shortcut…', 'muted')
            remote.pack_start(self.remote_detail, False, False, 0)
            boot = self.card()
            self.boot_switch = self.toggle(boot, 'Start server when this PC turns on', 'Starts in the background, before desktop login.', self.backend.boot)
            playback = self.card()
            self.subtitles_switch = self.toggle(playback, 'Subtitles on by default',
                'Applies when each video starts. You can still change captions during playback.', self.backend.subtitles)
            self.subtitles_switch.get_accessible().set_name('Subtitles on by default')
            playback.pack_start(self.label('On uses your Stremio subtitle language, or English if none is set. Subtitles must be available for the video.', 'muted'), False, False, 0)
            self.body.pack_start(self.button('Open Stremio on TV', self.backend.open_tv, True), False, False, 0)
            self.message = self.label('Closing this window does not change server status.', 'muted')
            self.body.pack_start(self.message, False, False, 0)
            self.build_addons(tabs)
            self.build_network(tabs)
            self.window.show_all()
            if tab != 'overview':
                tabs.set_current_page({'addons': 1, 'network': 2}[tab])
            self.refresh()
            GLib.timeout_add_seconds(5, self.refresh)
            self.poll_bandwidth()
            GLib.timeout_add_seconds(1, self.poll_bandwidth)
            if screenshot:
                def capture():
                    window = self.window.get_window()
                    image = Gdk.pixbuf_get_from_window(window, 0, 0, self.window.get_allocated_width(), self.window.get_allocated_height())
                    image.savev(str(Path(screenshot).resolve()), 'png', [], [])
                    self.quit()
                    return False
                GLib.timeout_add(2800, capture)

        def build_network(self, tabs):
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin=20)
            scroll.add(box)
            tabs.append_page(scroll, Gtk.Label(label='Network'))
            box.pack_start(self.label('TV IP address', 'section'), False, False, 0)
            box.pack_start(self.label('If your router gives the TV a new address, find it in the TV’s network settings and enter it here. Keep the TV on.', 'muted'), False, False, 0)
            self.saved_address = self.label('Reading saved address…', 'muted')
            box.pack_start(self.saved_address, False, False, 0)
            address_row = Gtk.Box(spacing=8)
            self.tv_ip_parts = []
            for index in range(4):
                if index:
                    address_row.pack_start(Gtk.Label(label='.'), False, False, 0)
                entry = Gtk.Entry()
                entry.set_width_chars(3)
                entry.set_max_width_chars(3)
                entry.set_max_length(3)
                entry.set_alignment(.5)
                entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
                entry.get_accessible().set_name(f'TV IP address, part {index + 1} of 4')
                entry.connect('activate', lambda _: self.save_tv_address())
                entry.connect('key-press-event', self.address_key, index)
                address_row.pack_start(entry, False, False, 0)
                self.tv_ip_parts.append(entry)
                self.controls.append(entry)
            box.pack_start(address_row, False, False, 0)
            save = Gtk.Button(label='Save TV IP address')
            save.get_style_context().add_class('primary')
            save.connect('clicked', lambda _: self.save_tv_address())
            self.controls.append(save)
            box.pack_start(save, False, False, 0)
            box.pack_start(self.label('Saving briefly restarts any running hosting services and can interrupt playback. A stopped server stays stopped. Your WatchFree and startup preferences are kept.', 'muted'), False, False, 0)
            self.network_message = self.label('The app checks that the address belongs to your paired TV before saving.', 'muted')
            box.pack_start(self.network_message, False, False, 0)
            self.pc_address = self.label('', 'muted')
            box.pack_start(self.pc_address, False, False, 0)
            self.address_loaded = False

        def address_key(self, entry, event, index):
            if event.keyval in (Gdk.KEY_period, Gdk.KEY_KP_Decimal) and index < 3:
                self.tv_ip_parts[index + 1].grab_focus()
                self.tv_ip_parts[index + 1].select_region(0, -1)
                return True
            if event.keyval == Gdk.KEY_BackSpace and not entry.get_text() and index:
                self.tv_ip_parts[index - 1].grab_focus()
                return True
            return False

        def set_tv_address(self, value):
            for entry, part in zip(self.tv_ip_parts, value.split('.')):
                entry.set_text(part)

        def save_tv_address(self):
            if self.busy:
                return
            parts = [entry.get_text() for entry in self.tv_ip_parts]
            for index, part in enumerate(parts):
                if not part.isascii() or not part.isdigit() or not 0 <= int(part) <= 255:
                    self.network_message.set_text('Enter a number from 0 to 255 in each of the four boxes.')
                    self.tv_ip_parts[index].grab_focus()
                    return
            value = '.'.join(str(int(part)) for part in parts)
            self.perform(lambda: self.backend.update_tv_ip(value), network=True)

        def build_addons(self, tabs):
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin=20)
            scroll.add(box)
            tabs.append_page(scroll, Gtk.Label(label='Add-ons'))
            box.pack_start(self.label('Manage TV add-ons', 'section'), False, False, 0)
            box.pack_start(self.label('Paste an add-on Install link or manifest.json URL. Changes open the TV’s add-ons screen.', 'muted'), False, False, 0)
            self.addon_url = Gtk.Entry(placeholder_text='Paste https://…/manifest.json or stremio://…')
            self.addon_url.set_visibility(False)
            self.addon_url.set_input_purpose(Gtk.InputPurpose.URL)
            self.addon_url.connect('activate', lambda _: self.install_from_entry())
            box.pack_start(self.addon_url, False, False, 0)
            self.controls.append(self.addon_url)
            show = Gtk.CheckButton(label='Show URL')
            show.connect('toggled', lambda widget: self.addon_url.set_visibility(widget.get_active()))
            box.pack_start(show, False, False, 0)
            install = Gtk.Button(label='Install add-on')
            install.get_style_context().add_class('primary')
            install.connect('clicked', lambda _: self.install_from_entry())
            self.controls.append(install)
            box.pack_start(install, False, False, 0)
            box.pack_start(self.label('Installed on the TV', 'section'), False, False, 0)
            box.pack_start(self.label('Use Delete beside an add-on to uninstall it from the TV. Built-ins are protected.', 'muted'), False, False, 0)
            self.addon_rows = []
            self.addon_delete_buttons = []
            self.addon_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
            self.addon_list.get_style_context().add_class('addons')
            table = Gtk.ScrolledWindow()
            table.set_min_content_height(230)
            table.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            table.add(self.addon_list)
            box.pack_start(table, True, True, 0)
            box.pack_start(self.button('Refresh from TV', lambda: self.backend.manage_addons('list'), addon=True), False, False, 0)
            self.addon_message = self.label('Refresh to read the current TV list. Configured URLs stay private on this PC.', 'muted')
            box.pack_start(self.addon_message, False, False, 0)

        def install_from_entry(self):
            value = self.addon_url.get_text().strip()
            if not value:
                self.addon_message.set_text('Paste an add-on URL first.')
                return
            self.perform(lambda: self.backend.install_addon(value), addon=True, clear_url=True)

        def show_addons(self, rows):
            for button in self.addon_delete_buttons:
                self.controls.remove(button)
            self.addon_delete_buttons = []
            for row in self.addon_list.get_children():
                row.destroy()
            self.addon_rows = rows
            for name, version, key, protected in rows:
                row = Gtk.Box(spacing=16, margin=4)
                row.pack_start(self.label(name), True, True, 0)
                row.pack_start(self.label(version, 'muted'), False, False, 0)
                button = Gtk.Button(label='Built-in' if protected else 'Delete', valign=Gtk.Align.CENTER)
                button.set_sensitive(not protected)
                button.set_tooltip_text('Protected by Stremio' if protected else f'Delete {name} from the TV')
                if not protected:
                    button.get_style_context().add_class('delete')
                    button.connect('clicked', lambda _, addon_key=key, addon_name=name: self.delete_addon(addon_key, addon_name))
                    self.controls.append(button)
                    self.addon_delete_buttons.append(button)
                row.pack_end(button, False, False, 0)
                self.addon_list.add(row)
            self.addon_list.show_all()

        def delete_addon(self, key, name):
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True,
                message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                text=f'Delete {name} from Stremio on the TV?')
            dialog.format_secondary_text('This uninstalls the add-on and its catalogs. You can reinstall it later with its URL. The TV will open the add-ons screen.')
            dialog.add_button('Cancel', Gtk.ResponseType.CANCEL)
            dialog.add_button('Delete add-on', Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.CANCEL)
            answer = dialog.run(); dialog.destroy()
            if answer == Gtk.ResponseType.OK:
                self.perform(lambda: self.backend.remove_addon(key), addon=True)

        def poll_bandwidth(self):
            if not self.metric_busy:
                self.metric_busy = True
                def work():
                    result = self.sampler.sample()
                    GLib.idle_add(self.bandwidth_received, result)
                self.metric_pool.submit(work)
            return True

        def bandwidth_received(self, result):
            self.metric_busy = False
            self.samples.append(result)
            if result['available']:
                self.rates.set_text(f"Receive {result['receive_bps'] * 8 / 1e6:.2f} Mb/s   ·   Send {result['send_bps'] * 8 / 1e6:.2f} Mb/s")
            else:
                self.rates.set_text('Server counters unavailable')
            self.graph.queue_draw()
            return False

        def draw_bandwidth(self, widget, cr):
            width, height = widget.get_allocated_width(), widget.get_allocated_height()
            left, top, right, bottom = 65, 10, width - 12, height - 24
            now = self.samples[-1]['time'] if self.samples else time.monotonic()
            samples = [s for s in self.samples if s['time'] >= now - 120]
            values = [s[k] * 8 / 1e6 for s in samples if s['available'] for k in ('receive_bps', 'send_bps')]
            raw = max([1.0] + values) * 1.1
            magnitude = 10 ** math.floor(math.log10(raw))
            ceiling = math.ceil(raw / magnitude) * magnitude
            cr.select_font_face('Sans'); cr.set_font_size(10)
            for i in range(5):
                y = top + (bottom - top) * i / 4
                cr.set_source_rgba(.6, .55, .7, .22); cr.set_line_width(1)
                cr.move_to(left, y); cr.line_to(right, y); cr.stroke()
                cr.set_source_rgb(.72, .69, .79)
                cr.move_to(0, y + 4); cr.show_text(f'{ceiling * (4-i) / 4:g}')
            cr.move_to(0, height - 4); cr.show_text('Mb/s')
            cr.move_to(left, height - 4); cr.show_text('2m ago')
            cr.move_to(right - 22, height - 4); cr.show_text('Now')
            for key, color in [('receive_bps', (.5, .89, .71)), ('send_bps', (.7, .52, .98))]:
                cr.set_source_rgb(*color); cr.set_line_width(2)
                connected = False
                for sample in samples:
                    if not sample['available']:
                        cr.stroke(); connected = False; continue
                    x = left + (sample['time'] - now + 120) / 120 * (right - left)
                    y = bottom - sample[key] * 8 / 1e6 / ceiling * (bottom - top)
                    (cr.line_to if connected else cr.move_to)(x, y)
                    connected = True
                cr.stroke()
            return False

        def perform(self, callback, addon=False, clear_url=False, network=False):
            if self.busy:
                return
            self.busy = True
            self.addon_action = addon
            self.network_action = network
            self.clear_url = clear_url
            self.message.set_text('Updating…')
            if addon:
                self.addon_message.set_text('Waiting for confirmation from Stremio on the TV…')
            if network:
                self.network_message.set_text('Checking the TV and updating its address…')
            for control in self.controls:
                control.set_sensitive(False)
            def work():
                try:
                    callback()
                    result = self.backend.status()
                    GLib.idle_add(self.completed, result, None)
                except Exception as exc:
                    GLib.idle_add(self.completed, None, str(exc) if isinstance(exc, RuntimeError) else 'Could not reach the local services. Try Start / repair.')
            self.pool.submit(work)

        def completed(self, result, error):
            self.busy = False
            for control in self.controls:
                control.set_sensitive(True)
            if result:
                self.display(result)
            else:
                # Revert a switch's optimistic thumb when saving fails.
                self.updating = True
                for switch in (self.shortcut_switch, self.boot_switch, self.subtitles_switch):
                    switch.set_active(switch.get_state())
                self.updating = False
            self.message.set_text(error or 'Updated. Closing this window keeps your settings.')
            if self.addon_action:
                self.addon_message.set_text(error or 'Confirmed by Stremio. The list is the last verified TV snapshot.')
            if self.network_action:
                self.network_message.set_text(error or 'TV address verified and saved. You can use WatchFree or Open Stremio on TV.')
                if not error and result:
                    self.set_tv_address(result['tv_ip'])
            if not error and self.clear_url:
                self.addon_url.set_text('')
            return False

        def display(self, result):
            self.saved_address.set_text('Saved TV address: ' + result['tv_ip'])
            self.pc_address.set_text('PC server address: ' + result['pc_ip'] + '\nThis setting changes the TV address. PC address changes still require server setup.')
            if not self.address_loaded:
                self.set_tv_address(result['tv_ip'])
                self.address_loaded = True
            online = result['host_online'] and result['engine_online']
            stopped = not result['server_running']
            self.server_status.set_text('Server online' if online else 'Server stopped' if stopped else 'Server needs attention')
            context = self.server_status.get_style_context()
            context.remove_class('online'); context.remove_class('offline')
            context.add_class('online' if online else 'offline')
            self.server_detail.set_text('Interface ready · Streaming engine ready' if online else
                'Hosting is off. Use Start / repair when ready.' if stopped else
                'Interface: ' + ('ready' if result['host_online'] else 'offline') + ' · Streaming engine: ' + ('ready' if result['engine_online'] else 'offline'))
            self.updating = True
            for switch, key in ((self.shortcut_switch, 'shortcut_enabled'),
                                (self.boot_switch, 'start_at_boot'),
                                (self.subtitles_switch, 'subtitles_default_on')):
                switch.set_state(result[key])
                switch.set_active(result[key])
            self.updating = False
            self.remote_detail.set_text('On · waiting for WatchFree' if result['shortcut_enabled'] and result['shortcut_running'] else
                'On · paused while the server is stopped' if result['shortcut_enabled'] else 'Off · WatchFree works normally')
            if result['sleep_blocked']:
                self.message.set_text('Automatic sleep is blocked. Closing this window does not change server status.')
            rows = [(a['name'], a['version'], a['key'], a['protected']) for a in result['addons']]
            if rows != self.addon_rows:
                self.show_addons(rows)

        def refresh(self):
            if not self.busy:
                self.busy = True
                def work():
                    try:
                        result = self.backend.status()
                        GLib.idle_add(self.refreshed, result)
                    except Exception:
                        GLib.idle_add(self.refreshed, None)
                self.pool.submit(work)
            return True

        def refreshed(self, result):
            self.busy = False
            if result:
                self.display(result)
            else:
                self.message.set_text('Could not check the server. Try Start / repair.')
            return False

    return App().run([])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status', action='store_true', help='Print local status without opening the panel')
    parser.add_argument('--screenshot', help=argparse.SUPPRESS)
    parser.add_argument('--tab', choices=['overview','addons','network'], default='overview', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.status:
        print(json.dumps(Backend().status(), indent=2))
    else:
        raise SystemExit(desktop(args.screenshot, args.tab))
