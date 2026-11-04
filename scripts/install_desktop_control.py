#!/usr/bin/env python3
"""Install the local Stremio TV application launcher and desktop shortcut."""
from pathlib import Path
import subprocess

import tvctl


def quote(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$') + '"'


def main():
    desktop = Path(subprocess.check_output(['xdg-user-dir', 'DESKTOP'], text=True).strip())
    applications = Path.home() / '.local/share/applications'
    text = ('[Desktop Entry]\nType=Application\nName=Stremio TV\n'
            'Comment=Control the Stremio server and WatchFree shortcut\n'
            f'Exec=/usr/bin/python3 {quote(tvctl.ROOT / "scripts/tv_control_panel.py")}\n'
            f'Icon={tvctl.ROOT / "config/icons/stremio-tv.svg"}\n'
            'Terminal=false\nCategories=AudioVideo;\nStartupNotify=true\n')
    for folder in (desktop, applications):
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / 'stremio-tv.desktop'
        if path.exists() and path.read_text() != text:
            backup = tvctl.PRIVATE / 'desktop-shortcut-before-install.desktop'
            if not backup.exists():
                backup.write_bytes(path.read_bytes()); backup.chmod(0o600)
        path.write_text(text); path.chmod(0o755)
        subprocess.run(['desktop-file-validate', str(path)], check=True)
    subprocess.run(['gio', 'set', str(desktop / 'stremio-tv.desktop'), 'metadata::trusted', 'true'], check=True)
    print('Installed Stremio TV in Applications and on the desktop.')


if __name__ == '__main__':
    main()
