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
from .base import ClipboardBase, ClipboardException, ClipboardSetupException
import subprocess
import sys
import shutil
from typing import Union
import logging
import warnings
logger = logging.getLogger(__name__)


class _PBCopyPBPasteBackend(ClipboardBase):
    def __init__(self):
        self.pbcopy = shutil.which('pbcopy')
        self.pbpaste = shutil.which('pbpaste')
        if not self.pbcopy:
            raise ClipboardSetupException("pbcopy not found. pbcopy must be installed and available on PATH")
        if not self.pbpaste:
            raise ClipboardSetupException("pbpaste not found. pbpaste must be installed and available on PATH")

    def copy(self, data: Union[str, bytes], encoding=None) -> None:
        """
        Load data into the clipboard

        :param data:
        :return:
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
        :param encoding: same meaning as in ``subprocess.run``
        :param universal_newlines: same meaning as in ``subprocess.run``
        :param text: same meaning as in ``subprocess.run``
        :param errors: same meaning as in ``subprocess.run``
        :return: the clipboard contents. return type is binary by default. If encoding or errors or text are specified,
        the result is str
        """
        # TODO: pbpaste (and maybe even pbcopy) does not support binary data.
        #  We should replace it with a solution that works with any data

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
        self.copy(b'')

class _PasteboardBackend(ClipboardBase):
    def __init__(self):
        import pasteboard
        self.pb = pasteboard.Pasteboard()
        self._bytes_type = pasteboard.PDF

    def copy(self, data: Union[str, bytes], encoding=None):
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


    def paste(self, encoding=None, text=None, errors=None):
        contents = self.pb.get_contents(self._bytes_type)
        if contents is None:  # Data was not set as binary
            contents = self.pb.get_contents()
            if contents is None:
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
        self.copy('')

class MacOSClip(ClipboardBase):
    def __init__(self, _backend=None):
        if _backend:
            self.backend = _backend
        else:
            try:
                import pasteboard
                self.backend = _PasteboardBackend()
            except ImportError:
                self.backend = _PBCopyPBPasteBackend()

    def copy(self, *args, **kwargs):
        return self.backend.copy(*args, **kwargs)

    def paste(self, *args, **kwargs):
        return self.backend.paste(*args, **kwargs)

    def clear(self):
        return self.backend.clear()
