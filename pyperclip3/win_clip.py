from .base import ClipboardBase, ClipboardSetupException
try:
    import win32clipboard as _win32clipboard
except ImportError:
    _win32clipboard = None


class WindowsClipboard(ClipboardBase):
    def __init__(self):
        if _win32clipboard is None:
            raise ClipboardSetupException("pywin32 must be installed to use this library on Windows platform.")
