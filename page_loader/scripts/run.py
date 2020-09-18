#!usr/bin/env python3
from page_loader.load import save_page, KnownError
from page_loader.cli import get_parse_args
import os
import sys


CURRENT_DIR_PATH = os.path.dirname(__file__)


# def main():
#     parser = get_parse_args()
#     args = parser.parse_args()
#     response = get_response(args.url)
#     directory = args.output
#     if directory:
#         directory += '/'
#     page_name = make_name(args.url, postfix='.html')
#     # with open(f'{directory}{page_name}', 'w') as file:
#     #     content = file.write(response.text)
#     page_folder_name = make_name(args.url, postfix='_files')
#     if not os.path.exists(directory + page_folder_name):
#         os.mkdir(directory+page_folder_name)
#     soup = BeautifulSoup(response.text)


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
