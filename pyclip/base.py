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
Provides the abstract base class from which all clipboard implementations are derived.
"""
from abc import ABC, abstractmethod
from typing import Union


class ClipboardException(Exception):
    ...

class ClipboardSetupException(ClipboardException):
    ...

class ClipboardBase(ABC):
    """
    Abstract base class for Clipboard implementations.
    """
    @abstractmethod
    def copy(self, data: Union[str, bytes], encoding: str = None):
        return NotImplemented  # pragma: no cover

    @abstractmethod
    def paste(self, encoding=None, text=None, errors=None) -> Union[str, bytes]:
        return NotImplemented  # pragma: no cover

    @abstractmethod
    def clear(self):
        return NotImplemented  # pragma: no cover
