from .multion import _Multion, login, post, get, new_session, update_session, list_sessions, refresh_token, get_screenshot, delete_token

from importlib import metadata
try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)