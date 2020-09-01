#!usr/bin/env python3
from page_loader.load import get_response, save_page
from page_loader.cli import get_parse_args
import os
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse


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
    if directory:
        directory += '/'
    save_page(url, directory)





if __name__ == '__main__':
    main()
