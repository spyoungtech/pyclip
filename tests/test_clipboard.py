import os
import secrets
import subprocess
import sys
from unittest import mock

import pytest

try:
    import pyclip as clip
except ImportError:
    # XXX: probably shouldn't do this, but oh well ¯\_(ツ)_/¯
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import pyclip as clip


def test_copypaste():
    clip.copy('foo')
    assert clip.paste()
    assert clip.paste() == b'foo'
    assert clip.paste(text=True) == 'foo'


def test_copypaste_unicode():
    unicode = 'א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת װ ױ'
    clip.copy(unicode)
    assert clip.paste().decode() == unicode


@pytest.mark.xfail(sys.platform == 'darwin', reason="MacOS doesn't yet support arbitrary data")
def test_copy_paste_arbitrary_data():
    randbytes = secrets.token_bytes(1024)
    clip.copy(randbytes)
    assert clip.paste() == randbytes

def test_copy_paste_null_bytes_in_body():
    randbytes = secrets.token_bytes(1024)

    data_body = b'somedata\x00\x00'+randbytes
    clip.copy(data_body)
    assert clip.paste() == data_body


def test_copy_paste_null_terminated_bytes():
    randbytes = secrets.token_bytes(1024)

    data_body = b'somedata\x00\x00'+randbytes + b'\x00\x00'
    clip.copy(data_body)
    assert clip.paste() == data_body


def test_clear():
    clip.copy('foo')
    assert clip.paste(), 'test setup failed; clipboard contents unexpectedly empty'
    clip.clear()
    data = clip.paste()
    assert not data, f'clipboard contents unexpectly present: {repr(data)}'


@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_copypaste_pbcopy_backend():
    from pyclip.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    clip.copy('foo')
    assert clip.paste()
    assert clip.paste() == b'foo'
    assert clip.paste(text=True) == 'foo'
@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_copypaste_unicode_pbcopy_backend():
    from pyclip.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    unicode = 'א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת װ ױ'
    clip.copy(unicode)
    assert clip.paste().decode() == unicode


@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_clear_pbcopy_backend():
    from pyclip.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    clip.copy('foo')
    assert clip.paste(), 'test setup failed; clipboard contents unexpectedly empty'
    clip.clear()
    data = clip.paste()
    assert not data, f'clipboard contents unexpectly present: {repr(data)}'

def test_cli():
    from pyclip.cli import _main, main
    args = ['pyclip', 'copy']
    import io
    stdin = io.BytesIO(b"foo")
    class MockStdin:
        def __init__(self, b):
            self.buffer = io.BytesIO(b)
    with mock.patch('sys.exit', new=lambda x: x):
        with mock.patch('sys.argv', new=args), mock.patch('sys.stdin', new=MockStdin(b'foo')):
            main()
        args = ['pyclip', 'paste']
        class MockStdout:
            def __init__(self):
                self.buffer = io.BytesIO()
        stdout = MockStdout()
        with mock.patch('sys.argv', new=args), mock.patch('sys.stdout', new=stdout):
            main()
        assert stdout.buffer.getvalue() == b'foo'
        args = ['pyclip', 'clear']
        with mock.patch('sys.argv', new=args):
            main()
        assert not clip.paste()
    class fakeargs:
        command = 'nonexistent'
    r = _main(fakeargs)
    assert r == 1

@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_pbcopy_missing_raises_error():
    with mock.patch('shutil.which') as mock_which:
        mock_which.return_value = None
        from pyclip.macos_clip import _PBCopyPBPasteBackend, ClipboardSetupException
        with pytest.raises(ClipboardSetupException):
            c = _PBCopyPBPasteBackend()

@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_pbcopy_fallback():
    with mock.patch.dict('sys.modules', {'pasteboard': None}):
        from pyclip.macos_clip import MacOSClip, _PBCopyPBPasteBackend
        c = MacOSClip()
        assert isinstance(c.backend, _PBCopyPBPasteBackend)

@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_pasteboard_default():
    from pyclip.macos_clip import MacOSClip, _PasteboardBackend
    c = MacOSClip()
    assert isinstance(c.backend, _PasteboardBackend)

@pytest.mark.skipif(sys.platform != 'win32', reason='This test is for Windows only')
def test_nopywin32_raises_exception():
    with mock.patch.dict('sys.modules', {'win32clipboard': None, 'win32con': None}) as mock_modules:
        # force package reload
        del mock_modules['pyclip']
        del mock_modules['pyclip.win_clip']
        from pyclip.win_clip import WindowsClipboard, ClipboardSetupException
        with pytest.raises(ClipboardSetupException):
            c = WindowsClipboard()


def test_copy_bad_type_raises_typeerror():
    with pytest.raises(TypeError):
        clip.copy({})


@pytest.mark.skipif(sys.platform != 'linux', reason='This test is for Linux only')
def test_xclip_missing_raises_error():
    with mock.patch('shutil.which') as mock_which:
        mock_which.return_value = None
        from pyclip.xclip_clip import XclipClipboard, ClipboardSetupException
        with pytest.raises(ClipboardSetupException):
            c = XclipClipboard()


@pytest.mark.skipif(sys.platform != 'linux' or os.environ.get("WAYLAND_DISPLAY", "") != "", reason='This test is for Xorg only')
@pytest.mark.parametrize('targets, expected', [
    (["TARGETS", "TIMESTAMP", "image/png"], ["-t", "image/png"]),
    ([], []),
    (["TARGETS", "TIMESTAMP", "text/plain"], ["-t", "text/plain"]),
    (["text/html", "TARGETS", "TIMESTAMP", "text/plain"], ["-t", "text/plain"]),
])
def test_xclip_with_target(targets, expected):
    with mock.patch.object(subprocess, 'check_output', return_value="\n".join(targets)):
        with mock.patch.object(subprocess, 'run', wraps=subprocess.run) as wrapped_run:
            data = secrets.token_bytes(10)
            clip.copy(data)
            assert clip.paste() == data
            
    # the expected target was selected
    args = wrapped_run.call_args[0][0]
    assert args[1:] == ['-o', '-selection', 'clipboard'] + expected

def test_unknown_platform_raises_error():
    from pyclip.util import detect_clipboard, ClipboardSetupException
    with mock.patch('sys.platform', new='unknown'):
        with pytest.raises(ClipboardSetupException):
            c = detect_clipboard()

class MockProcess:
    def communicate(self, *args, **kwargs):
        self.returncode = 1
        return ('mock stdout', 'mock stderr')

class MockPopen:
    def __call__(self, *args, **kwargs):
        return MockProcess()

class MockCompletedProcess:
    def __init__(self, *args, **kwargs):
        self.returncode = 1
        self.stdout = 'mock stdout'
        self.stderr = 'mock stderr'

class MockSubprocessRun:
    def __call__(self, *args, **kwargs):
        return MockCompletedProcess()



@pytest.mark.skipif(sys.platform == 'win32', reason='Windows backend does not use subprocess')
def test_subprocess_fails_raises_clipboardexception_copy():
    from pyclip.base import ClipboardException
    if sys.platform == 'darwin':
        from pyclip.macos_clip import _PBCopyPBPasteBackend
        clip = _PBCopyPBPasteBackend()
    else:
        import pyclip as clip
    with mock.patch('subprocess.Popen', new=MockPopen()):
        with pytest.raises(ClipboardException):
            clip.copy('')

@pytest.mark.skipif(sys.platform == 'win32', reason='Windows backend does not use subprocess')
def test_subprocess_fails_raises_clipboardexception_paste():
    from pyclip.base import ClipboardException
    if sys.platform == 'darwin':
        from pyclip.macos_clip import _PBCopyPBPasteBackend
        clip = _PBCopyPBPasteBackend()
    else:
        import pyclip as clip
    with mock.patch('subprocess.run', new=MockSubprocessRun()):
        with pytest.raises(ClipboardException):
            clip.paste()
