#  Copyright 2021 Spencer Phillip Young
#  
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#  
#         http://www.apache.org/licenses/LICENSE-2.0
#  
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from typing import Union, Dict, Tuple, Any
import os
import ctypes
from contextlib import contextmanager
from .base import ClipboardBase, ClipboardSetupException, ClipboardException
try:
    import win32clipboard as _win32clipboard
    import win32con as _win32con
except ImportError:
    _win32clipboard = None
    _win32con = None

_CF_FORMATS = {
    value: name
    for name, value in ((n, getattr(_win32clipboard, n)) for n in dir(_win32clipboard) if n.startswith('CF_'))
}



class _Win32Clipboard:
    def __init__(self):
        self._clip_queue = Queue()
        self._clip = _win32clipboard

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self._clip.OpenClipboard()
        return self._clip

    def close(self):
        import pywintypes
        try:
            self._clip.CloseClipboard()
        except pywintypes.error as e:
            if e.winerror == 1418:
                return
            raise


    def _enumerate_clipboard_formats(self):
        formats = []
        with self.clip() as clip:
            fmt = clip.EnumClipboardFormats()
            formats.append(fmt)
            while True:
                fmt = clip.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                formats.append(fmt)
        return formats



class WindowsClipboard(ClipboardBase):
    def __init__(self):
        self ._clip_lock = threading.Lock()
        if _win32clipboard is None or _win32con is None:
            raise ClipboardSetupException("pywin32 must be installed to use this library on Windows platform.")
        self._clipboard = _Win32Clipboard()

    @property
    def _string_formats(self):
        return 1, 13, 0x0081



    def copy(self, data, encoding=None):
        """Copy given string into system clipboard."""
        with self._clipboard as clip:
            clip.EmptyClipboard()  # we clear the clipboard to become the clipboard owner
            if isinstance(data, str):
                clip.SetClipboardText(data, 13)
            elif isinstance(data, bytes):
                data = ctypes.create_string_buffer(data)
                clip.SetClipboardData(1, data)

    def clear(self):
        with self._clipboard as clip:
            clip.EmptyClipboard()
        return


    def paste(self, encoding=None, text=None, errors=None) -> Union[str, bytes]:
        """
        Returns clipboard contents"""
        with self._clipboard as clip:
            format = clip.EnumClipboardFormats()
            print(format)
            if format == 0:
                if text or encoding or errors:
                    return ''
                else:
                    return b''
            d = clip.GetClipboardData(format)
        if isinstance(d, bytes) and (text or encoding or errors):
            if format in self._string_formats:
                d = d.rstrip(b'\x00')  # string formats are null-terminated
            encoding = encoding or 'utf-8'
            errors = errors or 'strict'
            d = d.decode(errors=errors, encoding=encoding)
        elif isinstance(d, str):
            if format in self._string_formats:
                d = d.rstrip('\x00')  # string formats are null-terminated
            if not (text or encoding or errors):
                return d.encode('utf-8')
        return d