import warnings

from .base import ClipboardBase, ClipboardSetupException, ClipboardException
from typing import Union
import shutil
import subprocess


class XclipClipboard(ClipboardBase):
    def __init__(self):
        self.xclip = shutil.which('xclip')
        if not self.xclip:
            raise ClipboardSetupException(
                "xclip must be installed. " "Please install xclip using your system package manager"
            )

    def copy(self, data: Union[str, bytes], encoding=None):
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

    def paste(self, encoding=None, text=None, errors=None):
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
            completed_proc = subprocess.run(
                args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        if completed_proc.returncode != 0:
            raise ClipboardException(
                f"Copy failed. xclip returned code: {completed_proc.returncode!r} "
                f"Stderr: {completed_proc.stderr!r} "
                f"Stdout: {completed_proc.stdout!r}"
            )
        return completed_proc.stdout

    def clear(self):
        self.copy('')
