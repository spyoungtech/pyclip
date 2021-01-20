# pyperclip3

Cross-platform clipboard utilities supporting both binary and text data.

Some key features include:

- A cross-platform API (supports MacOS, Windows, Linux)
- Can handle arbitrary binary data
- On Windows, some additional [clipboard formats](https://docs.microsoft.com/en-us/windows/win32/dataxchg/standard-clipboard-formats) 
are supported

## Installation

Requires python 3.7+

```bash
pip install pyperclip3
```

## Usage

pyperclip3 can be used in Python code
```python
import pyperclip3

pyperclip3.copy("hello clipboard") # copy data to the clipboard
cb_data = pyperclip3.paste() # retrieve clipboard contents 
print(cb_data)

pyperclip3.clear() # clears the clipboard contents
assert not pyperclip3.paste()
```

Or a CLI

```bash
# paste clipboard contents to stdout
python -m pyperclip3 paste

# load contents to the clipboard from stdin
python -m pyperclip3 copy < myfile.text
# same as above, but pipe from another command
some-program | python -m pyperclip3 copy
```

## Status

This library will implement functionality for several platforms and clipboard utilities. 

- [x] MacOS (via `pbcopy`/`pbpaste`)
- [x] Windows
- [ ] Linux (xclip - coming soon)
- [ ] Linux (xsel - coming soon)

If there is a platform or utility not currently listed, please request it by creating an issue.

## Platform specific notes/issues

### Windows

- On Windows, the `pywin32` package is required.
- On Windows, additional clipboard formats are supported, including copying from a file 
(like if you right-click copy from File Explorer)

### MacOS

There is a known issue that `pbcopy`/`pbpaste` do not support arbitrary binary data.

### Linux

Linux requires `xclip` or `xsel` to work. Install with your package manager, e.g. `sudo apt install ...`
