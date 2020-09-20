#!usr/bin/env python3
from page_loader.load import save_page, KnownError
from page_loader.cli import get_parse_args
import sys


def main():
    parser = get_parse_args()
    args = parser.parse_args()
    url = args.url
    directory = args.output
    level_logging = args.level
    if directory:
        directory += '/'
    try:
        save_page(url, directory, level_logging)
    except KnownError:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
