import sys
from .base import ClipboardSetupException


def detect_clipboard():
    if sys.platform == 'darwin':
        from .macos_clip import MacOSClip
        return MacOSClip()
    elif sys.platform == 'win32':
        from .win_clip import WindowsClipboard
        return WindowsClipboard()
    else:
        raise ClipboardSetupException("No suitable clipboard found.")