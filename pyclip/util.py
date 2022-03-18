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
import sys
import os
from .base import ClipboardSetupException, ClipboardBase


def detect_clipboard() -> ClipboardBase:
    """
    Determine what implementation to use based on ``sys.platform``
    """
    if sys.platform == 'darwin':
        from .macos_clip import MacOSClip
        return MacOSClip()
    elif sys.platform == 'win32':
        from .win_clip import WindowsClipboard
        return WindowsClipboard()
    elif sys.platform == 'linux' and os.environ.get("WAYLAND_DISPLAY"):
        from .wayland_clip import WaylandClipboard
        return WaylandClipboard()
    elif sys.platform == 'linux':
        from .xclip_clip import XclipClipboard
        return XclipClipboard()
    else:
        raise ClipboardSetupException("No suitable clipboard found.")