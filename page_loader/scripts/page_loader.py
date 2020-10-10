#!usr/bin/env python3
import sys

from page_loader import cli
from page_loader.loader import KnownError, save_page, load_page
from page_loader import logging


def main():  # pragma: no cover
    parser = cli.get_parser()
    args = parser.parse_args()
    # logger = logging.setup(logging_level=args.level)
    # if args.output:
    #     args.output += '/'
    try:
        save_page(args.url, args.output, args.level)
    except KnownError as e:
        # logger.error('Что-то пошло не так')
        # raise KnownError('Чо-то пошло не так') from e
        sys.exit(1)
    else:
        sys.exit(0)


# def main():  # pragma: no cover
#     parser = cli.get_parser()
#     args = parser.parse_args()
#     # logger = logging.setup(logging_level=args.level)
#     # if args.output:
#     #     args.output += '/'
#     try:
#         load_page(args.url, args.output)
#     except KnownError as e:
#         # logger.error('Что-то пошло не так')
#         # raise KnownError('Чо-то пошло не так') from e
#         sys.exit(1)
#     else:
#         sys.exit(0)


if __name__ == '__main__':  # pragma: no cover
    main()
