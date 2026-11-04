"""Reviewed native descriptors from Vizio's public app feed, pinned locally.

No download at runtime. Never accept a client-supplied descriptor or URL.
See research/reviews/launcher-app-catalog.json for source identity and limits.
"""

NATIVE_APPS = {
    'netflix': {'NAME_SPACE': 3, 'APP_ID': '1', 'MESSAGE': None},
    'hulu': {'NAME_SPACE': 2, 'APP_ID': '3', 'MESSAGE': None},
    'hbo-max': {'NAME_SPACE': 2, 'APP_ID': '128', 'MESSAGE': None},
    'disney-plus': {'NAME_SPACE': 2, 'APP_ID': '75', 'MESSAGE': None},
    'youtube-tv': {'NAME_SPACE': 5, 'APP_ID': '3', 'MESSAGE': None},
    'youtube': {'NAME_SPACE': 5, 'APP_ID': '1', 'MESSAGE': None},
    # SOC=1, CHIPSET=9 maps to MTK5586 in the reported companion artifact.
    # Feed MT5586 override applies from firmware 86.700.0.0 onward.
    'prime': {'NAME_SPACE': 3, 'APP_ID': '3', 'MESSAGE': None},
    'paramount': {'NAME_SPACE': 2, 'APP_ID': '37', 'MESSAGE': None},
    'peacock': {'NAME_SPACE': 2, 'APP_ID': '88', 'MESSAGE': None},
    'apple-tv': {'NAME_SPACE': 3, 'APP_ID': '4', 'MESSAGE': None},
}
