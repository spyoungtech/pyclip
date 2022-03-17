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
"""
Provides clipboard functionality for Windows via the ``pywin32`` package
"""

from typing import Union, Dict, Tuple, Any
import os
import ctypes
from .base import ClipboardBase, ClipboardSetupException
import warnings
import time
try:
    import win32clipboard as _win32clipboard
    import win32con as _win32con
except ImportError:
    _win32clipboard = None
    _win32con = None

_TIMEOUT = 0.05

_CF_FORMATS = {
    value: name
    for name, value in ((n, getattr(_win32clipboard, n)) for n in dir(_win32clipboard) if n.startswith('CF_'))
}

class UnparsableClipboardFormatException(Exception):
    ...

class ClipboardNotTextFormatException(Exception):
    ...

class _Win32Clipboard:
    """
    Class for handling lower level details of managing Windows Clipboard
    """
    def __init__(self):
        self._clip = _win32clipboard
        self._is_open = False

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self, *, _timeout=None):
        import pywintypes
        if self._is_open:
            return self
        try:
            self._clip.OpenClipboard()
            self._is_open = True
        except pywintypes.error as e:
            if e.winerror == 5:
                if _timeout:
                    if time.time() < _timeout:
                        time.sleep(0.001)
                        return self.open(_timeout=_timeout)
                    else:
                        raise
                else:
                    t = time.time() + _TIMEOUT
                    time.sleep(0.001)
                    return self.open(_timeout=t)
        return self

    def close(self):
        import pywintypes
        try:
            self._clip.CloseClipboard()
            self._is_open = False
        except pywintypes.error as e:
            if e.winerror == 1418:
                self._is_open = False
                return
            raise

    def _get_format_name(self, fmt):
        if fmt in _CF_FORMATS:
            return _CF_FORMATS.get(fmt)
        return self._clip.GetClipboardFormatName(fmt)

    def _enumerate_clipboard_formats(self):
        """
        Clipboard must already be open to use this!
        """
        formats = []
        fmt = self._clip.EnumClipboardFormats()
        formats.append(fmt)
        while True:
            fmt = self._clip.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            formats.append(fmt)
        return formats

    def __getattr__(self, item):
        return getattr(self._clip, item)


class WindowsClipboard(ClipboardBase):
    def __init__(self):
        if _win32clipboard is None or _win32con is None:
            raise ClipboardSetupException("pywin32 must be installed to use this library on Windows platform.")
        self._clipboard = _Win32Clipboard()

    @property
    def _string_formats(self):
        return 1, 13, 0x0081, 7


    @property
    def _implemented_formats(self):
        implemented = [15, 11]
        implemented.extend(self._string_formats)
        return implemented

    def copy(self, data: Union[str, bytes], encoding=None):
        """Copy given string into system clipboard."""
        with self._clipboard as clip:
            clip.EmptyClipboard()  # we clear the clipboard to become the clipboard owner
            if isinstance(data, str):
                clip.SetClipboardText(data, 13)
            elif isinstance(data, bytes):
                data = ctypes.create_string_buffer(data)
                clip.SetClipboardData(11, data)
            else:
                raise TypeError(f"data must be str or bytes, not {type(data)}")

    def clear(self) -> None:
        """
        Clear the clipboard contents

        :return:
        """
        with self._clipboard as clip:
            clip.EmptyClipboard()
        return

    def _handle_dibv5(self, data):
        return data[:-1]

    def _handle_format(self, fmt, data):
        if fmt == 11:
            return self._handle_dibv5(data)
        if fmt == 15:
            return self._handle_hdrop(data)
        else:
            raise ValueError(f"Unknown format: {fmt}")

    def _handle_hdrop(self, data: Tuple[str, ]) -> bytes:
        if not isinstance(data, tuple):
            raise TypeError(f"Unexpected type for HDROP. Data must be tuple, not {type(data)}")
        if len(data) > 1:
            raise NotImplementedError("Currently HDROP paste is only supported for single files. It appears multiple files or directories were specified")
        if len(data) < 1:
            raise ValueError("Data unexpectedly empty")
        fname = data[0]
        if not os.path.isfile(fname):
            raise ValueError("Can only paste files. Did you copy a directory?")
        with open(fname, 'rb') as f:
            return f.read()

    def _get_all_formats(self) -> Dict[Tuple[int, str], Any]:  # pragma: no cover
        """
        Unused. Useful for debugging.

        :return:
        """
        import pywintypes
        d = {}
        formats = self._clipboard._enumerate_clipboard_formats()
        with self._clipboard as clip:
            for fmt in formats:
                name = self._clipboard._get_format_name(fmt)
                try:
                    d[(fmt, name)] = clip.GetClipboardData(fmt)
                except pywintypes.error as e:
                    if e.winerror == 0:
                        warnings.warn(f"Could not retrieve clipboard data for format {name} ({fmt}). Skipping.")
                        continue
                    raise
        return d

    def paste(self, encoding: str = None, text: bool = None, errors: str = None) -> Union[str, bytes]:
        """
        Returns clipboard contents

        :param encoding: same meaning as in ``bytes.encode``. Implies ``text=True``
        :param text: if True, bytes object will be en
        :param errors: same meaning as in ``bytes.encode``. Implies ``text=True``.
        :return: clipboard contents. Return value is bytes by default
            or str if any of ``encoding``, ``text``, or ``errors`` is provided.
        """
        with self._clipboard as clip:
            format = clip.EnumClipboardFormats()
            if format == 0:
                if text or encoding or errors:
                    return ''
                else:
                    return b''
            if format not in _CF_FORMATS:
                all_formats = self._clipboard._enumerate_clipboard_formats()
                acceptable_formats = [f for f in all_formats if f in self._implemented_formats]
                if not acceptable_formats:
                    raise UnparsableClipboardFormatException("Clipboard contents have no standard formats available. "
                                                    "The contents can only be understood by a private program")
                if (text or encoding or errors) and format not in self._string_formats:
                    raise ClipboardNotTextFormatException("Clipboard has no text formats available, but text options "
                                                          "were specified.")
                format = max(acceptable_formats)

            d = clip.GetClipboardData(format)
            if format not in self._string_formats and format in self._implemented_formats:
                return self._handle_format(format, d)

        if isinstance(d, str):
            if format in self._string_formats:
                d = d.rstrip('\x00')  # string formats are null-terminated
            if not (text or encoding or errors):
                return d.encode()  # even though the windows API returned a string
                                   # We convert back to bytes for API consistency here
        return d