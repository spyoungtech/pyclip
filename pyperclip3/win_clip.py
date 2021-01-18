import shutil
import warnings
from typing import Union
import subprocess
from tkinter import Tk
from contextlib import contextmanager
from .base import ClipboardBase, ClipboardSetupException, ClipboardException
try:
    import win32clipboard as _win32clipboard
    import win32con as _win32con
except ImportError:
    _win32clipboard = None
    _win32con = None



# @contextmanager
# def tk_context():
#         r = Tk()
#         r.withdraw()
#         try:
#             yield r
#         finally:
#             r.update()
#             r.destroy()

class WindowsClipboard(ClipboardBase):
    def __init__(self):
        if _win32clipboard is None or _win32con is None:
            raise ClipboardSetupException("pywin32 must be installed to use this library on Windows platform.")
        self.__clipboard = _win32clipboard
        self._clip = shutil.which('clip')
        if not self._clip:
            raise ClipboardSetupException("Can't find `clip.exe`")
    #
    # def paste(self):
    #     with tk_context() as context:
    #         clipboard_text = context.clipboard_get()
    #     return clipboard_text
    # #

    @property
    @contextmanager
    def _clipboard(self):
        self.__clipboard.OpenClipboard()
        try:
            yield self.__clipboard
        finally:
            self.__clipboard.CloseClipboard()



    def copy(self, data, encoding=None):
        """Copy given string into system clipboard."""
        args = ['clip']
        if isinstance(data, bytes):
            if encoding is not None:
                warnings.warn("encoding specified with a bytes argument. "
                              "Encoding option will be ignored. "
                              "To remove this warning, omit the encoding parameter or specify it as None", stacklevel=2)
            proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding=encoding)
        elif isinstance(data, str):
            proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True, encoding=encoding)
        else:
            raise ClipboardException(f"data must be of type str or bytes. got {type(data)}")

        if data:
            stdout, stderr = proc.communicate(data)
        else:
            stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise ClipboardException(f"Copy failed. clip returned code: {proc.returncode!r} "
                                     f"Stderr: {stderr!r} "
                                     f"Stdout: {stdout!r}")

    def clear(self):
        self.copy(b'')
        return

    def paste(self):
        """
        Returns clipboard contents"""
        with self._clipboard as clip:
            d = clip.GetClipboardData(_win32con.CF_UNICODETEXT)
            return d
