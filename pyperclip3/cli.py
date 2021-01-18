import argparse
import sys


def _main(args):
    from pyperclip3 import copy, clear, paste
    if args.command == "copy":
        copy(sys.stdin.read())
    elif args.command == 'paste':
        sys.stdout.buffer.write(paste())
    elif args.command == 'clear':
        clear()
    else:
        print('Unrecognized command', file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser('pyperclip3')
    subparsers = parser.add_subparsers(title='commands', dest='command', required=True, description='Valid commands')
    copy_parser = subparsers.add_parser('copy', help='Copy contents from stdin to the clipboard')
    paste_parser = subparsers.add_parser('paste', help='Output clipboard contents to stdout')
    clear_parser = subparsers.add_parser('clear', help='Clear the clipboard contents')
    args = parser.parse_args()
    ret = _main(args)
    sys.exit(ret)
