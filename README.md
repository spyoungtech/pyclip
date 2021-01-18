# pyperclip3

Cross-platform clipboard utilities supporting both binary and text data.


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
- [ ] Windows (coming soon)
- [ ] Linux (xclip - coming soon)
- [ ] Linux (xsel - coming soon)

If there is a platform or utility not currently listed, please request it by creating an issue.