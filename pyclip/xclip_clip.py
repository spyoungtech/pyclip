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
Provides the clipboard functionality for Linux via ``xclip``
"""
import shutil
import subprocess
import warnings
from typing import Union

from .base import ClipboardBase, ClipboardException, ClipboardSetupException


class XclipClipboard(ClipboardBase):
    def __init__(self):
        self.xclip = shutil.which('xclip')
        if not self.xclip:
            raise ClipboardSetupException(
                "xclip must be installed. " "Please install xclip using your system package manager"
            )

    def copy(self, data: Union[str, bytes], encoding: str = None) -> None:
        """
        Copy data into the clipboard

        :param data: the data to be copied to the clipboard. Can be str or bytes.
        :param encoding: same meaning as in ``subprocess.Popen``.
        :return: None
        """
        args = [
            self.xclip,
            '-selection',
            'clipboard',
        ]
        if isinstance(data, bytes):
            if encoding is not None:
                warnings.warn(
                    "encoding specified with a bytes argument. "
                    "Encoding option will be ignored. "
                    "To remove this warning, omit the encoding parameter or specify it as None",
                    stacklevel=2,
                )
            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                encoding=encoding,
            )
        elif isinstance(data, str):
            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                text=True,
                encoding=encoding,
            )
        else:
            raise TypeError(f"data argument must be of type str or bytes, not {type(data)}")
        stdout, stderr = proc.communicate(data)
        if proc.returncode != 0:
            raise ClipboardException(
                f"Copy failed. xclip returned code: {proc.returncode!r} "
                f"Stderr: {stderr!r} "
                f"Stdout: {stdout!r}"
            )

    def paste(self, encoding: str = None, text: bool = None, errors: str = None):
        """
        Retrieve data from the clipboard

        :param encoding: same meaning as in ``subprocess.run``
        :param text: same meaning as in ``subprocess.run``
        :param errors: same meaning as in ``subprocess.run``
        :return: the clipboard contents. return type is binary by default.
            If any of ``encoding``, ``errors``, or ``text`` are specified, the result type is str
        """
        args = [self.xclip, '-o', '-selection', 'clipboard']
        if encoding or text or errors:
            completed_proc = subprocess.run(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,
                encoding=encoding,
            )
        else:
            # retrieve the available targets and selects the first mime type available or plain text. 
            available_targets = [
                t for t in subprocess.check_output(args + ['-t', 'TARGETS'], text=True).splitlines() if t.islower()
            ]
            if "text/plain" in available_targets:
                target = ["-t", "text/plain"]
            elif available_targets:
                target = ["-t", available_targets[0]]
            else:
                target = []

            completed_proc = subprocess.run(
                args + target, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        if completed_proc.returncode != 0:
            raise ClipboardException(
                f"Copy failed. xclip returned code: {completed_proc.returncode!r} "
                f"Stderr: {completed_proc.stderr!r} "
                f"Stdout: {completed_proc.stdout!r}"
            )
        return completed_proc.stdout

    def clear(self):
        """
        Clear the clipboard contents

        :return:
        """
        self.copy('')
