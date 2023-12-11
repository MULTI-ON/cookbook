from .multion import (
    _Multion,
    login,
    post,
    get,
    new_session,
    update_session,
    list_sessions,
    close_session,
    close_sessions,
    refresh_token,
    get_screenshot,
    delete_token,
    get_token,
    get_video,
    set_remote,
    get_remote,
    set_api_url,
)

from .browse import MultionToolSpec

from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)
