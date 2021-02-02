# PyClip

Cross-platform clipboard utilities supporting both binary and text data.

Some key features include:

- A cross-platform API (supports MacOS, Windows, Linux)
- Can handle arbitrary binary data
- On Windows, some additional [clipboard formats](https://docs.microsoft.com/en-us/windows/win32/dataxchg/standard-clipboard-formats) 
are supported

## Installation

Requires python 3.7+

```bash
pip install pyclip
```

## Usage

pyclip can be used in Python code
```python
import pyclip

pyclip.copy("hello clipboard") # copy data to the clipboard
cb_data = pyclip.paste() # retrieve clipboard contents 
print(cb_data)  # b'hello clipboard'
cb_text = pyclip.paste(text=True)  # paste as text
print(cb_text)  # 'hello clipboard'

pyclip.clear() # clears the clipboard contents
assert not pyclip.paste()
```

Or a CLI

```bash
# paste clipboard contents to stdout
python -m pyclip paste

# load contents to the clipboard from stdin
python -m pyclip copy < myfile.text
# same as above, but pipe from another command
some-program | python -m pyclip copy
```

Installing via pip also provides the console script `pyclip`:

```bash
pyclip copy < my_file.txt
```

This library implements functionality for several platforms and clipboard utilities. 

- [x] MacOS
- [x] Windows
- [x] Linux (with `xclip`)

If there is a platform or utility not currently listed, please request it by creating an issue.

## Platform specific notes/issues

### Windows

- On Windows, the `pywin32` package is installed as a requirement.
- On Windows, additional clipboard formats are supported, including copying from a file 
(like if you right-click copy from File Explorer)

### MacOS

MacOS has support for multiple backends. By default, the `pasteboard` package is used.

`pbcopy`/`pbpaste` can also be used as a backend, but does not support arbitrary binary data, which may lead to 
data being lost on copy/paste. This backend may be removed in a future release.

### Linux

Linux requires `xclip` to work (which means you must also use X). Install with your package manager, e.g. `sudo apt install xclip`

# Acknowledgements

Big thanks to [Howard Mao](https://github.com/zhemao) for donating the PyClip project name on PyPI to 
this project.