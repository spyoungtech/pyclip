import sys, os
try:
    import pyperclip3 as clip
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import pyperclip3 as clip



def test_copypaste():
    clip.copy('foo')
    assert clip.paste()
    assert clip.paste() == b'foo'
    assert clip.paste(text=True) == 'foo'


def test_clear():
    clip.copy('foo')
    assert clip.paste(), 'test setup failed; clipboard contents unexpectedly empty'
    clip.clear()
    assert not clip.paste(), 'clipboard contents unexpectly present'
