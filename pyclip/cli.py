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
import argparse
import sys


def _main(args) -> int:
    from pyclip import copy, clear, paste
    if args.command == "copy":
        copy(sys.stdin.buffer.read())
    elif args.command == 'paste':
        sys.stdout.buffer.write(paste())
    elif args.command == 'clear':
        clear()
    else:
        print('Unrecognized command', file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser('pyclip')
    subparsers = parser.add_subparsers(title='commands', dest='command', required=True, description='Valid commands')
    copy_parser = subparsers.add_parser('copy', help='Copy contents from stdin to the clipboard')
    paste_parser = subparsers.add_parser('paste', help='Output clipboard contents to stdout')
    clear_parser = subparsers.add_parser('clear', help='Clear the clipboard contents')
    args = parser.parse_args()
    ret = _main(args)
    sys.exit(ret)
