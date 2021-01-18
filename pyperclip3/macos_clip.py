from .base import ClipboardBase, ClipboardException, ClipboardSetupException
import subprocess
import sys
import shutil
from typing import Union
import logging
import warnings
logger = logging.getLogger(__name__)


class MacOSClip(ClipboardBase):
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
            warnings.warn(f"expected object of type str or bytes. got {type(data)}. Automatic conversion to str may result in undesired result. To remove this warning, convert your object to a string or bytes object first", stacklevel=2)
            try:
                data = str(data)  # try to blindly convert object to str... this might be bad
                proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as e:
                tb = sys.exc_info()[2]
                raise ClipboardException(f"Could not convert object to str: {data!r}.").with_traceback(tb)

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



