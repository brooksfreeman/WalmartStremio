"""Isolated real GTK checks. Run with system Python and a graphical display."""
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tv_control_panel as panel
import tvctl
import playback_preferences


def status(_):
    return dict(host_online=False, engine_online=False, server_running=False,
                shortcut_enabled=True, shortcut_running=False, start_at_boot=True,
                sleep_blocked=False, addons=[], tv_ip='192.0.2.20', pc_ip='192.0.2.10',
                **playback_preferences.read())


def run(app, _):
    def wait(predicate):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            while GLib.MainContext.default().pending():
                GLib.MainContext.default().iteration(False)
            if predicate():
                return
            time.sleep(.01)
        raise AssertionError('GTK operation timed out')

    app.set_application_id('local.owner.StremioTV.SubtitleFixture')
    Gtk.Settings.get_default().set_property('gtk-enable-animations', False)
    app.register(None)
    app.activate()
    wait(lambda: not app.busy)
    switch = app.subtitles_switch
    assert switch.get_active() and switch.get_state()
    switch.set_active(False)
    wait(lambda: not app.busy)
    assert not switch.get_active() and not playback_preferences.read()['subtitles_default_on']
    switch.set_active(True)
    wait(lambda: not app.busy)
    assert switch.get_active() and playback_preferences.read()['subtitles_default_on']
    with patch.object(playback_preferences, 'set_subtitles', side_effect=RuntimeError('Fixture save failed')):
        switch.set_active(False)
        wait(lambda: not app.busy)
        assert switch.get_active() and switch.get_state(), 'Failed save must restore the thumb'
        assert app.message.get_text() == 'Fixture save failed'
    with patch.object(playback_preferences, 'set_subtitles', side_effect=AssertionError('Refresh must not save')):
        app.display(dict(status(None), subtitles_default_on=False))
        assert not switch.get_active()
        app.display(status(None))
        app.busy = True
        assert app.switch_changed(app.backend.subtitles, False)
        app.busy = False
    app.message.set_text('Subtitle preference saved. Applies when the next video starts.')
    drawn_at = time.monotonic() + .25
    wait(lambda: time.monotonic() >= drawn_at)
    # Scroll Overview so the newly added control and surrounding controls are visible.
    scroll = app.body.get_parent().get_parent()
    adjustment = scroll.get_vadjustment()
    adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
    drawn_at = time.monotonic() + .25
    wait(lambda: time.monotonic() >= drawn_at)
    wait(lambda: app.window.get_window() is not None)
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    image = Gdk.pixbuf_get_from_window(app.window.get_window(), 0, 0,
        app.window.get_allocated_width(), app.window.get_allocated_height())
    image.savev(str(tvctl.ROOT / 'research/reviews/subtitle-default-panel.png'), 'png', [], [])
    app.window.destroy()
    app.pool.shutdown(wait=True)
    app.metric_pool.shutdown(wait=True)
    print('GTK checks passed: initial state, Off/On saves, error rollback, refresh guard and busy guard.')
    return 0


with tempfile.TemporaryDirectory() as temporary, \
        patch.object(tvctl, 'PRIVATE', Path(temporary)), \
        patch.object(panel.Backend, 'status', status), \
        patch.object(panel.Sampler, 'sample', lambda _: {'available': False, 'time': time.monotonic()}), \
        patch.object(Gtk.Application, 'run', run):
    panel.desktop()
