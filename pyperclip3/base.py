from abc import ABC, abstractmethod
from typing import Union


class ClipboardException(Exception):
    ...

class ClipboardSetupException(ClipboardException):
    ...

class ClipboardBase(ABC):
    @abstractmethod
    def copy(self, data: Union[str, bytes], encoding=None):
        return NotImplemented

    @abstractmethod
    def paste(self, encoding=None, universal_newlines=None, text=None) -> Union[str, bytes]:
        return NotImplemented

    @abstractmethod
    def clear(self):
        return NotImplemented

    @property
    def type(self):
        return self.__class__.__name__
