import sys, os
try:
    import pyperclip3 as clip
except ImportError:
    # XXX: probably shouldn't do this, but oh well ¯\_(ツ)_/¯
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import pyperclip3 as clip
import pytest

from unittest import mock

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
    import secrets
    randbytes = secrets.token_bytes(1024)
    clip.copy(randbytes)
    assert clip.paste() == randbytes

def test_clear():
    clip.copy('foo')
    assert clip.paste(), 'test setup failed; clipboard contents unexpectedly empty'
    clip.clear()
    data = clip.paste()
    assert not data, f'clipboard contents unexpectly present: {repr(data)}'


@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_copypaste_pbcopy_backend():
    from pyperclip3.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    clip.copy('foo')
    assert clip.paste()
    assert clip.paste() == b'foo'
    assert clip.paste(text=True) == 'foo'
@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_copypaste_unicode_pbcopy_backend():
    from pyperclip3.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    unicode = 'א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת װ ױ'
    clip.copy(unicode)
    assert clip.paste().decode() == unicode


@pytest.mark.skipif(sys.platform != 'darwin', reason='This test is for MacOS only')
def test_clear_pbcopy_backend():
    from pyperclip3.macos_clip import _PBCopyPBPasteBackend, MacOSClip
    backend = _PBCopyPBPasteBackend()
    clip = MacOSClip(_backend=backend)
    clip.copy('foo')
    assert clip.paste(), 'test setup failed; clipboard contents unexpectedly empty'
    clip.clear()
    data = clip.paste()
    assert not data, f'clipboard contents unexpectly present: {repr(data)}'

def test_cli():
    from pyperclip3.cli import _main, main
    args = ['pyperclip3', 'copy']
    import io
    stdin = io.BytesIO(b"foo")
    class MockStdin:
        def __init__(self, b):
            self.buffer = io.BytesIO(b)
    with mock.patch('sys.exit', new=lambda x: x):
        with mock.patch('sys.argv', new=args), mock.patch('sys.stdin', new=MockStdin(b'foo')):
            main()
        args = ['pyperclip3', 'paste']
        class MockStdout:
            def __init__(self):
                self.buffer = io.BytesIO()
        stdout = MockStdout()
        with mock.patch('sys.argv', new=args), mock.patch('sys.stdout', new=stdout):
            main()
        assert stdout.buffer.getvalue() == b'foo'
        args = ['pyperclip3', 'clear']
        with mock.patch('sys.argv', new=args):
            main()
        assert not clip.paste()
