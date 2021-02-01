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
Provides clipboard for MacOS
"""
from .base import ClipboardBase, ClipboardException, ClipboardSetupException
import subprocess
import shutil
from typing import Union
import logging
import warnings
from functools import wraps
logger = logging.getLogger(__name__)


class _PBCopyPBPasteBackend(ClipboardBase):
    """
    MacOS Clipboard backend using pbcopy/pbpaste

    """
    def __init__(self):
        self.pbcopy = shutil.which('pbcopy')
        self.pbpaste = shutil.which('pbpaste')
        if not self.pbcopy:
            raise ClipboardSetupException("pbcopy not found. pbcopy must be installed and available on PATH")
        if not self.pbpaste:
            raise ClipboardSetupException("pbpaste not found. pbpaste must be installed and available on PATH")

    def copy(self, data: Union[str, bytes], encoding: str = None) -> None:
        """
        Copy data into the clipboard

        :param data: the data to be copied to the clipboard. Can be str or bytes.
        :param encoding: same meaning as in ``subprocess.Popen``.
        :return: None
        """
        args = [self.pbcopy]
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
            raise TypeError(f"data argument must be of type str or bytes, not {type(data)}")
        stdout, stderr = proc.communicate(data)
        if proc.returncode != 0:
            raise ClipboardException(f"Copy failed. pbcopy returned code: {proc.returncode!r} "
                                     f"Stderr: {stderr!r} "
                                     f"Stdout: {stdout!r}")
        return

    def paste(self, encoding=None, text=None, errors=None) -> Union[str, bytes]:
        """
        Retrieve data from the clipboard

        :param encoding: same meaning as in ``subprocess.run``
        :param text: same meaning as in ``subprocess.run``
        :param errors: same meaning as in ``subprocess.run``
        :return: the clipboard contents. return type is binary by default.
        If any of ``encoding``, ``errors``, or ``text`` are specified, the result type is str
        """

        args = [self.pbpaste]
        if encoding or text or errors:
            completed_proc = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            text=text, encoding=encoding)
        else:
            completed_proc = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if completed_proc.returncode != 0:
            raise ClipboardException(f"Copy failed. pbcopy returned code: {completed_proc.returncode!r} "
                                     f"Stderr: {completed_proc.stderr!r} "
                                     f"Stdout: {completed_proc.stdout!r}")
        return completed_proc.stdout

    def clear(self):
        """
        Clear the clipboard contents

        :return:
        """
        self.copy(b'')

class _PasteboardBackend(ClipboardBase):
    """
    MacOS Clipboard backend using the ``pasteboard`` package.
    """
    def __init__(self):
        import pasteboard
        self.pb = pasteboard.Pasteboard()
        self._bytes_type = pasteboard.PDF

    def copy(self, data: Union[str, bytes], encoding: str =None):
        """

        :param data: data to copy to the clipboard
        :param encoding: this parameter is ignored on this backend
        :return:
        """
        if isinstance(data, bytes):
            try:
                data = data.decode()
                self.pb.set_contents(data)
            except UnicodeDecodeError:
                self.pb.set_contents(data, self._bytes_type)
        elif isinstance(data, str):
            self.pb.set_contents(data)
        else:
            raise TypeError(f"data argument must be of type str or bytes, not {type(data)}")

    def paste(self, encoding: str = None, text: bool = None, errors: str = None):
        """
        Retrieve contents of the clipboard

        :param encoding: same meaning as in ``bytes.encode``. Implies ``text=True``
        :param text: if True, bytes object will be en
        :param errors: same meaning as in ``bytes.encode``. Implies ``text=True``.
        :return: clipboard contents. Return value is bytes by default
        or str if any of ``encoding``, ``text``, or ``errors`` is provided.
        """
        contents = self.pb.get_contents(self._bytes_type)
        if contents is None:  # Data was not set as binary
            contents = self.pb.get_contents()
            if contents is None:  # no string contents either
                return b'' if not (encoding or text or errors) else ''
            if not (encoding or text or errors):
                contents = contents.encode()
            return contents
        else:  # found some binary contents
            if not (encoding or text or errors):
                return contents
            else:
                return contents.encode(encoding=encoding, errors=errors)

    def clear(self):
        """
        Clear the clipboard contents

        :return:
        """
        self.copy('')


class MacOSClip(ClipboardBase):
    """
    Provides Clipboard functionality for MacOS.

    Defers to one of two backends: :py:class:`_PasteboardBackend` (the default) or :py:class:`_PBCopyPBPasteBackend`.
    """
    def __init__(self, _backend=None):
        if _backend:
            self.backend = _backend
        else:
            try:
                import pasteboard
                self.backend = _PasteboardBackend()
            except ImportError:
                self.backend = _PBCopyPBPasteBackend()
    @wraps(_PasteboardBackend.copy)
    def copy(self, *args, **kwargs):
        return self.backend.copy(*args, **kwargs)

    @wraps(_PasteboardBackend.paste)
    def paste(self, *args, **kwargs):
        return self.backend.paste(*args, **kwargs)

    @wraps(_PasteboardBackend.clear)
    def clear(self):
        return self.backend.clear()
