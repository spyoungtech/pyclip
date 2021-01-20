import sys, os
try:
    import pyperclip3 as clip
except ImportError:
    # XXX: probably shouldn't do this, but oh well ¯\_(ツ)_/¯
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import pyperclip3 as clip
import pytest


def test_copypaste():
    clip.copy('foo')
    assert clip.paste()
    assert clip.paste() == b'foo'
    assert clip.paste(text=True) == 'foo'


def test_copypaste_unicode():
    unicode = 'א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת װ ױ'
    clip.copy(unicode)
    assert clip.paste().decode() == unicode


@pytest.mark.xfail(sys.platform == 'darwin', reason="MacOS doesn't yet support arbitrary data", strict=True)
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
