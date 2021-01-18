import sys
from .util import detect_clipboard
from .base import ClipboardSetupException
import warnings

try:
    DEFAULT_CLIPBOARD = detect_clipboard()
except ClipboardSetupException as e:
    DEFAULT_CLIPBOARD = None
    _CLIPBOARD_EXCEPTION_TB = sys.exc_info()[2]


def copy(*args, **kwargs):
    if DEFAULT_CLIPBOARD is None:
        raise ClipboardSetupException("Could not setup clipboard").with_traceback(_CLIPBOARD_EXCEPTION_TB)
    return DEFAULT_CLIPBOARD.copy(*args, **kwargs)


def paste(*args, **kwargs):
    if DEFAULT_CLIPBOARD is None:
        raise ClipboardSetupException("Could not setup clipboard").with_traceback(_CLIPBOARD_EXCEPTION_TB)
    return DEFAULT_CLIPBOARD.paste(*args, **kwargs)


def clear(*args, **kwargs):
    if DEFAULT_CLIPBOARD is None:
        raise ClipboardSetupException("Could not setup clipboard").with_traceback(_CLIPBOARD_EXCEPTION_TB)
    return DEFAULT_CLIPBOARD.clear(*args, **kwargs)
