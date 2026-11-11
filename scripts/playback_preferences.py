"""PC-owned playback defaults, shared by the desktop panel and TV frontend."""
import tvctl

FILE = 'playback-preferences.json'


def read():
    try:
        value = tvctl.read_private(FILE)
        enabled = value['subtitles_default_on']
        if type(enabled) is not bool:
            raise ValueError('Invalid subtitle preference')
    except FileNotFoundError:
        enabled = True
    return {'subtitles_default_on': enabled}


def set_subtitles(enabled):
    if type(enabled) is not bool:
        raise ValueError('Subtitle preference must be on or off')
    tvctl.save_private(FILE, {'subtitles_default_on': enabled})
