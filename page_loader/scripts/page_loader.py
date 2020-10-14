#!usr/bin/env python3
import sys

from page_loader import cli, logging
from page_loader.loader import KnownError, save_page


def main():  # pragma: no cover
    parser = cli.get_parser()
    args = parser.parse_args()
    logging.setup(logging_level=args.level)
    try:
        save_page(args.url, args.output)
    except KnownError:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':  # pragma: no cover
    main()
